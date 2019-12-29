
class MortgageCalc(object):
    def __init__(self):
        self._balance = 391000.0
        self._rate = 0.0375
        self._periodsPerYear = 12
        self._payPerPeriod = 2000.66
        self._ratePaidTotal = 0.0
        self._primePaidTotal = 0.0
        self._ratePaidYear = 0.0
        self._primePaidYear = 0.0

    def _RunPeriod(self, year, month):
        ratePaid = self._balance * self._rate / self._periodsPerYear
        primePaid = self._payPerPeriod - ratePaid
        if (primePaid > self._balance):
            primePaid = self._balance
            ratePaid = 0

        print("{}/{:02d}    {:11.2f} {:11.2f}        {:9.2f}     {:9.2f}"
              .format(year, month, self._balance, self._balance - primePaid, primePaid, ratePaid))
        self._balance = self._balance - primePaid
        self._ratePaidTotal = self._ratePaidTotal + ratePaid
        self._primePaidTotal = self._primePaidTotal + primePaid
        self._ratePaidYear = self._ratePaidYear + ratePaid
        self._primePaidYear = self._primePaidYear + primePaid

    def _RunYear(self, year):
        print("Month     BalanceStart  BalanceEnd    PrincipalPaid  InterestPaid".format())
        self._ratePaidYear = 0.0
        self._primePaidYear = 0.0
        i = 0
        while i < self._periodsPerYear:
            i += 1
            self._RunPeriod(year, i)
        print("{} total      --        --              {:9.2f}     {:9.2f}".format(year, self._primePaidYear, self._ratePaidYear))
        print()

    def Run(self):
        year = 2020
        while year < 2027:
            self._RunYear(year)
            year += 1
        print("Grand Total     --        --              {:9.2f}     {:9.2f}".format(self._primePaidTotal, self._ratePaidTotal))


mort = MortgageCalc()
mort.Run()

