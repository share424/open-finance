"""
Author: share424

Google Spreadheet modules
"""

from typing import List
import sys
import datetime
import gspread
from finance import Finance


class GSheet:
    """
    Google spreadsheet class
    """

    def __init__(self, sheet_url: str, config_path: str = 'config.json') -> None:
        self.app = gspread.service_account(filename=config_path)
        self.spreadsheet = self.app.open_by_url(sheet_url)

    def is_worksheet_exists(self, worksheet_name: str) -> bool:
        '''Return True if worksheet exists'''
        return worksheet_name in [sheet.title for sheet in self.spreadsheet.worksheets()]

    def get_or_create_worksheet(self, worksheet_name: str) -> gspread.Worksheet:
        '''Return worksheet if exists, otherwise create new worksheet'''
        if self.is_worksheet_exists(worksheet_name):
            return self.spreadsheet.worksheet(worksheet_name)
        worksheet = self.spreadsheet.add_worksheet(
            worksheet_name, rows=1, cols=4)
        worksheet.update('A1', 'Date')
        worksheet.update('B1', 'Type')
        worksheet.update('C1', 'Amount')
        worksheet.update('D1', 'Notes')

        return worksheet

    def add_data(self, data: Finance, title: str = None) -> None:
        '''Add data to worksheet'''
        # get data month and year
        if title is None:
            title = data.date.strftime('%B %Y')

        worksheet = self.get_or_create_worksheet(title)
        worksheet.append_row(data.get_row())

    def get_data(self, title: str) -> List[Finance]:
        '''Return data from worksheet'''
        if not self.is_worksheet_exists(title):
            raise ValueError('Sheet does not exist')
        worksheet = self.spreadsheet.worksheet(title)
        rows = worksheet.get_all_values()

        data = []
        for i in range(1, len(rows)):
            row = rows[i]
            date, finance_type, amount, note = row
            # convert yyyy-mm-dd to datetime
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            data.append(Finance(finance_type, int(amount), note, date))

        return data


if __name__ == '__main__':
    url = sys.argv[1]
    sheet = sys.argv[2]

    gsheet = GSheet(url)
    print(gsheet.get_data(sheet))
