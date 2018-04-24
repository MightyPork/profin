import profin

pf = profin.Projector()

# This demo simulates Mr. Bob who gave up one poorly paying job, then had trouble finding a better one,
# had to borrow from a friend, then finally found a good paying job and all was OK


# Start date and balance
pf.date(2018, 'April', 24)
pf.balance(+100_000) # initial savings

# Recurring payments, paid on 1st of eahc month
rent = pf.monthly('Rent', -12_000) # a pretty high rent...
internet = pf.monthly('Internet', -450).on(10) # this is paid on the 10th
spotify = pf.monthly('Spotify', -160)

# using .spread() to distribute the cost over the whole month
# Set to False for less accurate graph but more readable stdout logs
want_spread = True

food = pf.monthly('Food', -3500).spread(want_spread)
membership = pf.monthly('Club Member.', -200).spread(want_spread)
misc = pf.monthly('Misc Expenses', -2000).spread(want_spread)

# A poorly paying job
job1 = pf.monthly('Cleaning Job', +15_000, day=12)

# Not going to the Club in May
membership.skip_month(2018, 'May')

# --- we can set a global date instead of specifying it in each start() and end()
# also, if .start() is not called, the global date is used
pf.date(2018, 'June')

job1.end() # Quit the job in May, last pay received in June

# cancel non-essential expenses
spotify.end()
membership.end()
misc.end()

# Looking bad, borrow from a friend
friend_loan = pf.borrow('Loan from Luke', +50_000).on(2018, 'Oct')\
    .repay_monthly(-5000, day=18)

# A new job with much better pay than before!
pf.date(2018, 'Dec')
job2 = pf.monthly('Sausage Stand Job', +25_000, day=15)


# --- We generate the prediction until December 31, 2019
# You can pass a second argument verbose=False to disable stdout printing
samples = pf.project_to(2019)

# show in a graph
pf.graph(samples)
