import datetime

class Finance:
  def __init__(self, type: str, amount: int, note: str, date: datetime.date = datetime.date.today()):
    if type not in ['income', 'outcome']:
      raise ValueError('Type must be income or outcome')
    if amount < 0:
      raise ValueError('Amount must be positive')

    self.type = type
    self.amount = amount
    self.note = note
    self.date = date

  def get_date(self) -> str:
    return self.date.strftime('%Y-%m-%d')

  def get_row(self) -> list:
    return [self.get_date(), self.type, self.amount, self.note]