# Options Bactesting
## Purpose
This project is for Options Backtesting. Since prices on options data are quite high, there is an idea to use underlying price and BlackScholes model to actually price the options.

## Implementation
Main parts of this project are:
- Portfolio
- BlackScholes prices
- Strategy
- Data feeds

### Portfolio
The main part, which includes data on all movements - order open/close, account balances, etc.

### Black-Scholes pricer
This part do the only thing - calculates option price based on strike, spot price, date to expiration, risk-free rate and volatility.

### Strategy
In this module we define basic rules when to trade and when to not. Also, here describe rules to close all existing posiiotns

### Data feeds 
This part only includes CBOE for now, so we can pull historical data directly from CBOE
