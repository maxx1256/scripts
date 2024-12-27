import array

income   = array.array('f', [37.0])   # annual income, initial year value
spending = array.array('f', [80.0])   # how much need to spend per year, initial year value
savings  = array.array('f', [2000.0])   # amount of savings each year, initial year value

incomeIncrease = 2   # income increase per year. percent
inflation      = 4   # yearly inflation, percent
interestRate   = 3   # savings yearly interest rate, percent

i = 0
print('year         income       spending        savings')
print(f'{i:4}{income[i]:15.0f}{spending[i]:15.0f}{savings[i]:15.0f}')
for i in range(0, 30):
    income.append(income[i] * (1.0 + incomeIncrease/100.0))
    spending.append(spending[i] * (1.0 + inflation/100.0))
    savings.append(savings[i] * (1.0 + interestRate/100.0) + income[i] - spending[i])
    if savings[i+1] < 0:
        break
    print(f'{i+1:4}{income[i+1]:15.0f}{spending[i+1]:15.0f}{savings[i+1]:15.0f}')
