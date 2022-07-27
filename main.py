"""
Author: share424

Main Bot modules
"""
import datetime
import os
from telegram import Update, User
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
import matplotlib.pyplot as plt
from finance import Finance, get_surplus, get_info
from gsheet import GSheet
from helper import parse_int, load_config


def authenticate(user: User) -> bool:
    '''Return account data'''
    user_config = load_config()
    for account in user_config['users']:
        if str(user.id) == str(account['user_id']):
            return account
    raise ValueError('You are not authorized to use this bot')


async def user_info(update: Update) -> None:
    '''Show user info'''
    await update.message.reply_text(
        f'Hello {update.effective_user.first_name}, your id is {update.effective_user.id}'
    )


async def help_commands(update: Update) -> None:
    '''Show help commands'''
    commands = [
        '/in <amount> <notes> add new income',
        '/out <amount> <notes> add new outcome',
        '/info [title|year] [month] show income vs outcome. default current month',
        '/help show this help'
    ]
    await update.message.reply_text('\n'.join(commands))


async def income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Add new income to current month sheets

    /in <amount> <notes>
    """
    try:
        account = authenticate(update.effective_user)
        if len(context.args) != 2:
            await update.message.reply_text('Usage: /in <amount> <notes>')
            return
        amount = parse_int(context.args[0])
        notes = context.args[1]

        data = Finance('income', amount, notes)
        gsheet = GSheet(account['sheet_url'])
        gsheet.add_data(data)

        await update.message.reply_text('Added income')
        print(f'Added outcome {amount} {notes} {data.get_date()}')
    except ValueError as error:
        await update.message.reply_text(f'Error: {error}')


async def outcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Add new outcome to current month sheets

    /out <amount> <notes>
    """
    try:
        account = authenticate(update.effective_user)
        if len(context.args) != 2:
            await update.message.reply_text('Usage: /out <amount> <notes>')
            return
        amount = parse_int(context.args[0])
        notes = context.args[1]

        data = Finance('outcome', amount, notes)
        gsheet = GSheet(account['sheet_url'])
        gsheet.add_data(data)

        await update.message.reply_text('Added outcome')
        print(f'Added outcome {amount} {notes} {data.get_date()}')
    except ValueError as error:
        await update.message.reply_text(f'Error: {error}')


def generate_income_outcome_chart(title: str, surplus: dict, tmp_dir: str) -> str:
    """
    Generate income vs outcome chart
    """
    # generate pie chart income vs outcome
    plt.pie([surplus['income'], surplus['outcome']],
            labels=['Income', 'Outcome'], startangle=90)
    plt.title(f'Income vs Outcome: {title}')
    save_path = os.path.join(tmp_dir, 'income_vs_outcome.png')
    plt.savefig(save_path)
    plt.close()

    return save_path


def generate_chart(title: str, data: dict, tmp_dir: str) -> str:
    """
    Generate pie chart
    """
    # generate pie chart for income
    plt.pie([item['amount'] for _, item in data.items()],
            labels=data.keys(), startangle=90)
    plt.title(title)
    save_path = os.path.join(tmp_dir, 'chart.png')
    plt.savefig(save_path)
    plt.close()

    return save_path


def summary_data(title: str, surplus: dict, incomes: dict, outcomes: dict) -> str:
    """
    Summarize data
    """
    # summarize income and outcome
    income_summary = []
    outcome_summary = []
    for key, item in incomes.items():
        income_summary.append(
            f'- {key}: Rp.{format(item["amount"], ",")} ({item["qty"]})\n')

    for key, item in outcomes.items():
        outcome_summary.append(
            f'- {key}: Rp.{format(item["amount"], ",")} ({item["qty"]})\n')

    return f"""
Title: {title}

Income: Rp.{format(surplus['income'], ',')}
Outcome: Rp.{format(surplus['outcome'], ',')}
Surplus: Rp.{format(surplus['surplus'], ',')}

Income
{''.join(income_summary)}
Outcome
{''.join(outcome_summary)}
      """


def get_title(context: ContextTypes.DEFAULT_TYPE) -> str:
    '''Get title of chart'''
    title = datetime.datetime.now().strftime('%B %Y')
    # /info <month> <year>
    if len(context.args) == 2:
        month = context.args[1]
        year = parse_int(context.args[0])

        # convert int month to string
        if month.isdigit():
            month = datetime.date(year=year, month=parse_int(month), day=1).strftime('%B')
        else:
            month = month.capitalize()
        title = f'{month} {year}'
    elif len(context.args) == 1:  # /info <title>
        title = context.args[0]
    return title


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get income vs outcome info

    /info [title|month] [year]
    """
    try:
        account = authenticate(update.effective_user)
        title = get_title(context)

        gsheet = GSheet(account['sheet_url'])
        datas = gsheet.get_data(title)

        if len(datas) <= 0:
            await update.message.reply_text('No data')
            return

        surplus = get_surplus(datas)
        incomes = get_info(datas, 'income')
        outcomes = get_info(datas, 'outcome')

        summary = summary_data(title, surplus, incomes, outcomes)

        await update.message.reply_markdown(summary)

        # create temp dir
        dir_path = os.path.join(os.getcwd(), 'temp',
                                str(update.effective_user.id))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # generate income vs outcome chart
        chart = generate_income_outcome_chart(title, surplus, dir_path)
        with open(chart, 'rb') as img:
            await update.message.reply_photo(photo=img)

        # generate pie chart for income
        chart = generate_chart(f'Income: {title}', incomes, dir_path)
        with open(chart, 'rb') as img:
            await update.message.reply_photo(photo=img)

        # generate pie chart for outcome
        chart = generate_chart(f'Outcome: {title}', outcomes, dir_path)
        with open(chart, 'rb') as img:
            await update.message.reply_photo(photo=img)

    except ValueError as error:
        await update.message.reply_text(f'Error: {error}')
        print(error)

if __name__ == '__main__':
    print('Starting bot...')
    config = load_config()

    app: Application = ApplicationBuilder().token(
        config['access_token']).build()

    app.add_handler(CommandHandler("user_info", user_info))
    app.add_handler(CommandHandler("in", income))
    app.add_handler(CommandHandler("out", outcome))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("help", help_commands))

    print('Bot started')
    app.run_polling()
