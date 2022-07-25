from typing import Tuple
import gspread
from helper import load_config
from finance import Finance

def create_app(config_path: str = 'config.json') -> gspread.Client:
  return gspread.service_account(filename=config_path)

def load_sheet(app: gspread.Client, config_path: str = 'config.json') -> gspread.Spreadsheet:
  config = load_config(config_path)
  return app.open_by_url(config['sheet_url'])

def check_if_exists(sheet: gspread.Spreadsheet, worksheet_name: str) -> bool:
  return worksheet_name in [sheet.title for sheet in sheet.worksheets()]

def get_or_create_worksheet(sheet: gspread.Spreadsheet, worksheet_name: str) -> gspread.Worksheet:
  if check_if_exists(sheet, worksheet_name):
    return sheet.worksheet(worksheet_name)
  worksheet = sheet.add_worksheet(worksheet_name, rows=1, cols=4)
  worksheet.update('A1', 'Date')
  worksheet.update('B1', 'Type')
  worksheet.update('C1', 'Amount')
  worksheet.update('D1', 'Notes')

  return worksheet

def add_row(worksheet: gspread.Worksheet, data: Finance) -> None:
  worksheet.append_row(data.get_row())

def get_spreadsheet(config_path: str = 'config.json') -> gspread.Spreadsheet:
  app = create_app(config_path)
  return load_sheet(app, config_path)

def add_data(data: Finance) -> None:
  spreadsheet = get_spreadsheet()

  # get data month and year
  title = data.date.strftime('%B %Y')

  sheet = get_or_create_worksheet(spreadsheet, title)

  add_row(sheet, data)

def get_data(title: str) -> Tuple[int, int, dict, dict, dict]:
  spreadsheet = get_spreadsheet()
  if not check_if_exists(spreadsheet, title):
    raise ValueError('Sheet does not exist')
  sheet = spreadsheet.worksheet(title)
  rows = sheet.get_all_values()

  income = 0
  outcome = 0
  notes = []
  incomes = {}
  outcomes = {}

  for i in range(1, len(rows)):
    row = rows[i]
    date, type, amount, note = row
    if type == 'income':
      income += int(amount)
      if note.lower() not in incomes:
        incomes[note.lower()] = 0
      incomes[note.lower()] += int(amount)
    else:
      outcome += int(row[2])
      if note.lower() not in outcomes:
        outcomes[note.lower()] = 0
      outcomes[note.lower()] += int(amount)
    notes.append([note, int(amount)])

  # group notes and count
  notes_count = {}
  for note in notes:
    if note[0].lower() not in notes_count:
      notes_count[note[0].lower()] = {
        'qty': 0,
        'amount': 0
      }
    notes_count[note[0].lower()]['qty'] += 1
    notes_count[note[0].lower()]['amount'] += int(note[1])

  return int(income), int(outcome), notes_count, incomes, outcomes

if __name__ == '__main__':
  spreadsheet = get_spreadsheet()

  print(spreadsheet.worksheets())

  print(get_data('Test'))

  # sheet = get_or_create_worksheet(spreadsheet, 'Test')
  # add_row(sheet, Finance('income', 100, 'Test'))