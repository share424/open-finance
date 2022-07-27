"""
Author: share424

Module for finance data
"""

import datetime
from typing import List


class Finance:
    """
    Finance data class
    """

    def __init__(self,
                 finance_type: str,
                 amount: int,
                 note: str,
                 date: datetime.date = datetime.date.today()):
        if finance_type not in ['income', 'outcome']:
            raise ValueError('Type must be income or outcome')
        if amount < 0:
            raise ValueError('Amount must be positive')

        self.type = finance_type
        self.amount = amount
        self.note = note
        self.date = date

    def get_date(self) -> str:
        '''Return date in yyyy-mm-dd format'''
        return self.date.strftime('%Y-%m-%d')

    def get_row(self) -> list:
        '''Return row data in list (used for gsheet)'''
        return [self.get_date(), self.type, self.amount, self.note]


def get_surplus(data: List[Finance]) -> int:
    """
    Return surplus, income, and outcome amount
    """
    income = 0
    outcome = 0
    for row in data:
        if row.type == 'income':
            income += row.amount
        else:
            outcome += row.amount

    return {
        'income': income,
        'outcome': outcome,
        'surplus': income - outcome
    }


def get_info(data: List[Finance], finance_type: str) -> List[Finance]:
    """
    Return qty and amount of notes of finance_type
    """
    income = {}
    for row in data:
        if row.type == finance_type:
            note = row.note.lower()
            if note not in income:
                income[note] = {
                    'qty': 0,
                    'amount': 0
                }
            income[note]['qty'] += 1
            income[note]['amount'] += row.amount
    return income
