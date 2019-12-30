
rates = [0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
accumulated = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

year = 0
while (year < 10):
    year += 1
    msg = "{:02d}  ".format(year)
    x = 0
    while (x < 6):
        accumulated[x] = accumulated[x] * (1.0 + rates[x])
        msg = msg + "{:8.2f}%".format((accumulated[x] - 1)*100)
        x += 1

    print(msg)