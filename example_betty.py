import profin

pf = profin.Projector()

# This demo simulates Betty who saved for a car


# Start date and balance
pf.date(2018, 'March', 24)
pf.balance(+40_000) # initial savings

# Recurring payments, paid on 1st of eahc month
rent = pf.monthly('Rent', -8_000) # a pretty high rent...

# using .spread() to distribute the cost over the whole month
# Set to False for less accurate graph but more readable stdout logs
want_spread = True

food = pf.monthly('Food', -3500).spread(want_spread)

# Betty goes to gym and it's very expensive
gym1 = pf.monthly('Gym 1', -500).on(10)
gym2 = pf.monthly('Gym 2', -500).on(20)

# She is a cashier but the pay isn't that good
job = pf.monthly('Cashier Job', +22_000, day=6)


pf.date(2018, 'June')
# Betty is saving for a car, she stopped going to the gym and instead jogs outside.
gym1.end()
gym2.end()


# In September, Frank lent Betty some cash for the car
friend_loan = pf.borrow('Frank\'s Loan', +35_000).on(2018, 'Sep')\
    .repay_monthly(-8000, day=7)\
    .begin(2018, 'Dec') # Frank gives Betty 3 months before she has to start paying it back

# Betty can't decide which car to buy. Finally...
pf.expend("Car Purchase", 120_000).on(2018, 'Sep', 28)

# whoops that was expensive. But she'll recover ...

# Now she's paying off the loan. It's done in about 3 months after December


# --- We generate the prediction until December 31, 2019
# You can pass a second argument verbose=False to disable stdout printing
samples = pf.project_to(2019)

# show in a graph
pf.graph(samples)
