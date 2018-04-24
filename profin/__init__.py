from calendar import monthrange
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas as pd


def parse_month(month) -> int:
    """ Parse string month to a number 1-12 """
    map = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12,

        'sept': 9,

        'january': 1,
        'february': 2,
        'march': 3,
        'april': 4,
        'june': 6,
        'july': 7,
        'august': 8,
        'september': 9,
        'october': 10,
        'november': 11,
        'december': 12
    }

    k = str(month).lower()
    if k in map:
        return map[k]

    return int(month)  # try it as numeric

class Projector:
    def __init__(self):
        self.incomes = []
        self.cursor = datetime.datetime.now().date()
        self.oldest = None

    def date(self, year:int, month='Jan', day:int=1) -> 'Projector':
        self.cursor = datetime.date(year, parse_month(month), day)

        if self.oldest is None:
            self.oldest = self.cursor

        return self

    def project_to(self, year, month='Dec', day=31, verbose=True):
        records = []

        end = None
        aday = day
        while aday >= 28:
            try:
                end = datetime.date(year, parse_month(month), aday)
                break
            except ValueError:
                aday -= 1

        if end is None:
            raise ValueError("Bad projection end date")

        now = self.oldest
        balance = 0
        while now <= end:
            buf = ""
            any_non_balance = False
            any = False

            for inc in self.incomes:
                ain = inc.get_absolute_income_on(now)
                if ain is not None:
                    balance = ain
                    any = True
                    if verbose:
                        buf += "\nSet Balance: %d" % balance
                else:
                    inco = inc.get_income_on(now)
                    if inco is not None and inco != 0:
                        any = True
                        any_non_balance = True
                        balance += inco
                        if verbose:
                            buf += "\n| %20s ... %s%d" % (inc.name, '+' if inco>0 else '', inco)

            if any:
                if verbose:
                    print(now)
                    print(buf.strip())
                    if any_non_balance:
                        print('End Balance: %d' % balance)
                    print('\n')

                records.append({'date': now, 'balance': balance})

            now += datetime.timedelta(days=1)

        return records

    def graph(self, samples, currency='CZK'):
        """ Show samples from project_to() in a line graph """
        years = mdates.YearLocator()  # every year
        months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')

        r = pd.DataFrame().from_records(samples)

        fig, ax = plt.subplots()
        ax.step(r.date, r.balance, where='post')

        # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)

        # round to nearest years...
        datemin = np.datetime64(r.date[0], 'Y')
        datemax = np.datetime64(r.date[len(r.date)-1], 'Y') + np.timedelta64(1, 'Y')
        ax.set_xlim(datemin, datemax)

        # format the coords message box
        def price(x):
            return currency+' %1.0f' % x

        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.format_ydata = price
        ax.grid(True)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.show()

    def balance(self, balance:int) -> 'Projector':
        """ Set known balance at a date cursor (this modifies the total value) """
        self.incomes.append(SetBalance(self, balance))
        return self

    def monthly(self, name: str, income: int, day=1) -> 'MonthlyIncome':
        """ Monthly recurrent expense or income """
        m = MonthlyIncome(self, name, per_month=income, payday=day)
        self.incomes.append(m)
        return m

    def receive(self, name, money) -> 'SingleIncome':
        """ Once-off Income """
        return self.single(name, +abs(money))

    def expend(self, name, money) -> 'SingleIncome':
        """ Expense """
        return self.single(name, -abs(money))

    def single(self, name, money) -> 'SingleIncome':
        """ Non-recurrent expense or income """
        m = SingleIncome(self, name, money=money)
        self.incomes.append(m)
        return m

    def borrow(self, name, money) -> 'SimpleLoan':
        """ Borrow money with no interest, to be repaid """
        m = SimpleLoan(self, name, money=money)
        self.incomes.append(m)
        return m


class AIncome:
    """ Abstract income record """
    def __init__(self, name:str, pf:Projector):
        self.pf = pf
        self.name = name

        self.date_start = pf.cursor
        self.date_end = None
        self.started = False
        self.ended = False

    def get_income_on(self, date):
        """ Get income on a given date """

        if self.ended:
            return 0

        if self.date_end is not None and self.date_end <= date:
            self.ended = True

        if not self.started and self.date_start <= date:
            self.started = True

        if self.started:
            return self._day_income(date)

    def _day_income(self, date):
        """ Day's income, end dates have been already checked and are OK """
        raise NotImplementedError()

    def get_absolute_income_on(self, date):
        """ Get absolute income value (used for SetBalance) """
        return None


class MonthlyIncome(AIncome):
    """ Periodic income with monthly period """
    def __init__(self, pf: Projector, name:str, per_month:int, payday:int=1):
        """
        payday - the day of the month when the money is sent or received
        per_month - money sent or received per month
        """
        super().__init__(name, pf)
        self.skip_dates = []
        self.monthly = per_month
        self.payday = payday
        self.remains = None
        self.spreading = False

    def on(self, day:int) -> 'MonthlyIncome':
        """ Set the payday """
        self.payday = day
        return self

    def _day_income(self, date:datetime.date) -> int:
        if datetime.date(date.year, date.month, 1) in self.skip_dates:
            return 0

        if self.spreading:
            if self.remains is not None:
                if self.remains > 0:
                    if abs(self.monthly) > self.remains:
                        self.ended = True
                        topay = self.remains
                        self.remains = 0
                        return topay if self.monthly > 0 else -topay
                    self.remains -= round(abs(self.monthly) / monthrange(date.year, date.month)[1])
                else:
                    return 0

            x = round(self.monthly / monthrange(date.year, date.month)[1])
            return x
        else:
            if date.day == self.payday:
                if self.remains is not None:
                    if self.remains > 0:
                        if abs(self.monthly) > self.remains:
                            self.ended = True
                            topay = self.remains
                            self.remains = 0
                            return topay if self.monthly > 0 else -topay
                        self.remains -= abs(self.monthly)
                    else:
                        return 0
                return self.monthly
            else:
                return 0

    def skip_month(self, year, month) -> 'MonthlyIncome':
        """ Skip a month """
        self.skip_dates.append(datetime.date(year, parse_month(month), 1))
        return self

    def start(self, year=None, month=1, day=1) -> 'MonthlyIncome':
        """ Set the start date """
        if year is None:
            self.date_start = self.pf.cursor
        else:
            self.date_start = datetime.date(year, parse_month(month), day)
        return self

    def end(self, year=None, month=1, day=1) -> 'MonthlyIncome':
        """ Set the end date """

        if year is None:
            self.date_end = datetime.date(self.pf.cursor.year, self.pf.cursor.month,
                                          monthrange(self.pf.cursor.year, self.pf.cursor.month)[1]) # last day of the month
        else:
            self.date_end = datetime.date(year, parse_month(month), day)
        return self

    def total(self, total) -> 'MonthlyIncome':
        """ Set the total after which the payment is stopped """
        self.remains = total
        return self

    def spread(self, doSpread=True) -> 'MonthlyIncome':
        """ Spread over the month """
        self.spreading = doSpread
        return self


class SingleIncome(AIncome):
    """ Single-shot income """

    def __init__(self, pf: Projector, name:str, money:int):
        super().__init__(name, pf)
        self.money = money
        self.start = pf.cursor
        self.end = pf.cursor

    def _day_income(self, date):
        return self.money

    def on(self, year, month=1, day=1) -> 'SingleIncome':
        """ Set the exact date """
        self.date_start = self.date_end = datetime.date(year, parse_month(month), day)
        return self


class SimpleLoan(AIncome):
    """ Simple interest-free loan """
    def __init__(self, pf: Projector, name:str, money:int):
        """
        Money is the total borrowed money
        """
        super().__init__(name, pf)
        self.borrowed = money
        self.start = pf.cursor
        self.end = pf.cursor

        self.receipt = pf.receive(name, money)
        self.repay = None

    def on(self, year, month=1, day=1) -> 'SimpleLoan':
        """ Set borrow date """
        self.start = datetime.date(year, parse_month(month), day)
        self.receipt.on(year, month, day)
        return self

    def repay_monthly(self, payment, day=1) -> 'SimpleLoan':
        """
        Configure monthly payments.
        payment - how much to pay monthly
        day - day of the month to pay
        """
        self.repay = self.pf.monthly(self.name, -abs(payment), day=day).total(abs(self.borrowed))
        return self.begin(self.start.year, self.start.month)

    def begin(self, year, month) -> 'SimpleLoan':
        """ Set the payments start month """
        self.repay.start(year, month)
        return self

    def _day_income(self, date):
        return None


class SetBalance (AIncome):
    """ Set balance to a known value """
    def __init__(self, pf: Projector, balance:int):
        super().__init__('Balance', pf)
        self.balance = balance
        self.start = pf.cursor
        self.end = pf.cursor

    def _day_income(self, date):
        return 0

    def get_absolute_income_on(self, date):
        if date == self.start:
            return self.balance
        else:
            return None