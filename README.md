# ProFin - Personal Finance Projector

```
                         __
      o                 /' ) 
                      /'   (                          ,
                  __/' PRO )                        .' `;
   o      _.-~~~~'          ``---..__             .'   ;
     _.--'   b)                      ``--...____.'   .'
    (     _.      )).      `-._                     <
     `vvvvvvv-)-.....___.-     `-.         __...--'-.'.
       `^^^^^'-------.....`-.___.'----... .'         `.;
                                  jgs    `-`           `
```

ProFin is a python module for projecting the balance of a personal savings account 
over a future period.

The output can be used to visualise the balance development when planning some big
purchase or a change of the living situation, such as buying a flat or a car, 
getting a new job with possible months of no income, etc.

Please note the script is intended only for orientation and there may be minor
inaccuracies or bugs (please report!)

## Supported Features

### Financial Operations & Schemes

- Once-off expenses and income
- Recurrent monthly payments / income at a fixed date
- Monthly payments with a total expense cap
- Skipping a month in monthly payments / income
- Spread monthly expenses (e.g. food cost) - distributed over all days in a month
- Simple loan (borrowing money from a friend) with back-payments
- Setting initial or correction balance

### Functions

- Setting up a financial situation with changes at arbitrary dates
- Simulating account balance with day granularity
- Plotting results using PyPlot

## Dependencies

The script uses NumPy, MatPlotLib and Pandas for plotting. This may be improved in a future version
(in particular Pandas could be replaced). 

If plotting is not needed and the dependencies are not available (e.g. some old Debian), 
remove their imports and comment out the graph() function

## Usage

See the example files for an example of usage. (The examples are silly and not very representative, but they show the API well).
Additionally the code is documented with doc comments.
