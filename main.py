from telegram import Update, User
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
from finance import Finance
import json
import sheet
import datetime
import matplotlib.pyplot as plt

def parse_int(value: str) -> int:
  try:
    return int(value)
  except ValueError:
    return 0

def load_config() -> dict:
  with open('config.json', 'r') as f:
    return json.load(f)

def authentice(user: User) -> bool:
  config = load_config()
  return str(user.id) == str(config['user_id'])

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  await update.message.reply_text(f'Hello {update.effective_user.first_name}, your id is {update.effective_user.id}')

async def income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if not authentice(update.effective_user):
    await update.message.reply_text('You are not authorized to use this bot')
    return
  if len(context.args) != 2:
    await update.message.reply_text('Usage: /in <amount> <notes>')
    return
  amount = parse_int(context.args[0])
  notes = context.args[1]

  try:
    data = Finance('income', amount, notes)
    sheet.add_data(data)
    await update.message.reply_text('Added income')
    print(f'Added outcome {amount} {notes} {data.get_date()}')
  except Exception as e:
    await update.message.reply_text(f'Error: {e}')

async def outcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if not authentice(update.effective_user):
    await update.message.reply_text('You are not authorized to use this bot')
    return
  if len(context.args) != 2:
    await update.message.reply_text('Usage: /out <amount> <notes>')
    return
  amount = parse_int(context.args[0])
  notes = context.args[1]

  try:
    data = Finance('outcome', amount, notes)
    sheet.add_data(data)
    await update.message.reply_text('Added income')
    print(f'Added outcome {amount} {notes} {data.get_date()}')
  except Exception as e:
    await update.message.reply_text(f'Error: {e}')

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if not authentice(update.effective_user):
    await update.message.reply_text('You are not authorized to use this bot')
    return
  
  title = datetime.datetime.now().strftime('%B %Y')
  try:
    if len(context.args) == 2:
      month = context.args[1]
      year = context.args[0]

      # convert int month to string
      if month.isdigit():
        month = datetime.date(year=int(year), month=int(month), day=1).strftime('%B')
      else:
        month = month.capitalize()
      title = f'{month} {year}'
    elif len(context.args) == 1:
      title = context.args[0]
    income, outcome, notes, incomes, outcomes = sheet.get_data(title)
    summary = []
    for note, value in notes.items():
      summary.append(f'{note}: Rp.{format(value["amount"], ",")} ({value["qty"]})\n')
    await update.message.reply_text(f'Title: {title}\nIncome: Rp.{format(income, ",")}\nOutcome: Rp.{format(outcome, ",")}\nSummarize: \n{"".join(summary)}')

    if len(notes) <= 0:
      await update.message.reply_text('No data')
      return
    
    # generate pie chart income vs outcome
    plt.pie([income, outcome], labels=['Income', 'Outcome'], autopct='%1.1f%%', startangle=90)
    plt.title(f'{title}')

    plt.savefig('chart.png')
    img = open('chart.png', 'rb')
    await update.message.reply_photo(photo=img)
    img.close()

    # generate pie chart for income
    plt.clf()
    plt.pie(incomes.values(), labels=incomes.keys(), autopct='%1.1f%%', startangle=90)
    plt.title('Income')
    plt.savefig('chart_income.png')
    img = open('chart_income.png', 'rb')
    await update.message.reply_photo(photo=img)
    img.close()

    # generate pie chart for outcome
    plt.clf()
    plt.pie(outcomes.values(), labels=outcomes.keys(), autopct='%1.1f%%', startangle=90)
    plt.title('Outcome')
    plt.savefig('chart_outcome.png')
    img = open('chart_outcome.png', 'rb')
    await update.message.reply_photo(photo=img)
    img.close()

  except Exception as e:
    await update.message.reply_text(f'Error: {e}')
    print(e)

if __name__ == '__main__':
  print('Starting bot...')
  config = load_config()

  app: Application = ApplicationBuilder().token(config['access_token']).build()

  app.add_handler(CommandHandler("user_info", user_info))
  app.add_handler(CommandHandler("in", income))
  app.add_handler(CommandHandler("out", outcome))
  app.add_handler(CommandHandler("info", info))
  
  print('Bot started')
  app.run_polling()

  