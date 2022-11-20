import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt


class MonteCarlo(object):
    """
    Run Monte Carlo simulation on stock closing price. Code from class.
    Parameters
    ----------
    ticker: yfinance.Ticker object
        yfinance ticker object for stock of interest
    
    start_date: date
        Start date for stock closing price history
    
    end_date: date
        End date for stock closing price history
    
    time_horizon: int
        Number of days in future for which stock price prediction is being made
    
    n_simulation: int
        Number of monte carlo simulations to run

    seed: int
        Seed for random number generator
    

    Methods
    -------

    run_simulation
        Run the monte carlo simulation based on parameters passed during object initialization
    
    plot_simulation_price
        Plot the result of monte carlo simulation

    plot_simulation_hist
        Plot the histogram of closing price at time_horizon from the monte carlo simulations
    
    value_at_risk
        Print the Value at Risk at 95% confidence interval 
    """
    def __init__(self, ticker, start_date, end_date, time_horizon, n_simulation, seed):
        
        # Initiate class variables
        self.ticker = ticker  # Stock ticker
        self.start_date = start_date # Start Date
        self.end_date = end_date # End Date
        self.time_horizon = time_horizon  # Days
        self.n_simulation = n_simulation  # Number of simulations
        self.seed = seed  # Random seed
        self.simulation_df = pd.DataFrame()  # Table of results
        
        # Extract stock data
        self.stock_price = self.ticker.history(interval="1d", start=self.start_date, end=self.end_date)
        
        # Calculate financial metrics
        # Daily return (of close price)
        self.daily_return = self.stock_price['Close'].pct_change()
        # Volatility (of close price)
        self.daily_volatility = np.std(self.daily_return)
        
    def run_simulation(self):
        
        # Run the simulation
        np.random.seed(self.seed)
        self.simulation_df = pd.DataFrame()  # Reset
        
        for i in range(self.n_simulation):

            # The list to store the next stock price
            next_price = []

            # Create the next stock price
            last_price = self.stock_price['Close'][-1]

            for j in range(self.time_horizon):
                
                # Generate the random percentage change around the mean (0) and std (daily_volatility)
                future_return = np.random.normal(0, self.daily_volatility)

                # Generate the random future price
                future_price = last_price * (1 + future_return)

                # Save the price and go next
                next_price.append(future_price)
                last_price = future_price

            # Store the result of the simulation
            next_price_df = pd.Series(next_price).rename('sim' + str(i))
            self.simulation_df = pd.concat([self.simulation_df, next_price_df], axis=1)

    def plot_simulation_price(self):
        
        # Plot the simulation stock price in the future
        fig, ax = plt.subplots()
        fig.set_size_inches(15, 10, forward=True)

        plt.plot(self.simulation_df)
        # plt.title('Monte Carlo simulation for ' + self.ticker + \
        #           ' stock price in next ' + str(self.time_horizon) + ' days')
        plt.xlabel('Day')
        plt.ylabel('Price')

        plt.axhline(y=self.stock_price['Close'][-1], color='red')
        plt.legend(['Current stock price is: ' + str(np.round(self.stock_price['Close'][-1], 2))])
        ax.get_legend().legendHandles[0].set_color('red')

        return fig
    
    def plot_simulation_hist(self):
        
        # Get the ending price of the 200th day
        ending_price = self.simulation_df.iloc[-1:, :].values[0, ]

        # Plot using histogram
        fig, ax = plt.subplots()
        plt.hist(ending_price, bins=50)
        plt.axvline(x=self.stock_price['Close'][-1], color='red')
        plt.legend(['Current stock price is: ' + str(np.round(self.stock_price['Close'][-1], 2))])
        ax.get_legend().legendHandles[0].set_color('red')
        return fig
    
    def value_at_risk(self):
        # Price at 95% confidence interval
        future_price_95ci = np.percentile(self.simulation_df.iloc[-1:, :].values[0, ], 5)

        # Value at Risk
        VaR = self.stock_price['Close'][-1] - future_price_95ci
        return f'VaR at 95% confidence interval is {str(np.round(VaR, 2))} USD'