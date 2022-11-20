import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from monte_carlo import MonteCarlo


def initialize_ticker_obj():
    st.session_state['ticker_obj'] = yf.Ticker(st.session_state.ticker)


if __name__ == '__main__':
    ## Page config
    st.set_page_config(layout="wide")

    ####################################################### Ticker #######################################################
    ## Set ticker value in session state to persist
    if "ticker" not in st.session_state:
        st.session_state.ticker = "MSFT"
    else:
        st.session_state.ticker = st.session_state.ticker

    ## Store stock info in session state to persist
    if "ticker_obj" not in st.session_state:
        initialize_ticker_obj()
    else:
        st.session_state.ticker_obj = st.session_state.ticker_obj
    
    ################ Reference fin_dashboard01.py ################
    # Get the list of stock tickers from S&P500
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']

    # Add the ticker selection on the sidebar
    st.sidebar.selectbox(label="Select a ticker", options=ticker_list,key='ticker', on_change=initialize_ticker_obj)
    ##############################################################
    #######################################################################################################################

    ################################## Initialize Parameters of Monte Carlo Simulation ####################################
    ## Start Date: Select how far back to look at actuals to initialize the algorithm
    ## Number of Simulations: Number of monte carlo simulation to run
    ## Time Horizon: Number of days in future for which stock price prediction will be made
    
    end_date = datetime.today().date() - timedelta(days=1)
    col_start_date, col_nsim, col_time_horizon = st.columns(3)
    
    with col_start_date:
        start_date = st.date_input(label="Start date", 
                        value=datetime.today().date() - timedelta(days=365), max_value=datetime.today().date() - timedelta(days=60),
                        help="Select how far back to look at actuals to initialize the algorithm. Default 1 year.")

    with col_nsim:
        nsim = st.selectbox(label="Number of Simulations", options=(250,500,1000), help="Number of monte carlo simulation to run")
    
    with col_time_horizon:
        time_horizon = st.selectbox(label="Time Horizon", options=(30,60,90), help="Number of days in future for which stock price prediction will be made")
    #######################################################################################################################

    ######################################### Monte Carlo Simulation and Plotting #########################################
    mc_sim = MonteCarlo(ticker=st.session_state.ticker_obj,
                    start_date=start_date, end_date=end_date,
                    time_horizon=time_horizon, n_simulation=nsim, seed=1024)

    # Run simulation
    mc_sim.run_simulation()

    # Title and Value at Risk
    st.markdown(f"<p style='font-size:30px; font-weight:bold; text-align: center; margin-bottom:0px'>Monte Carlo simulation for {mc_sim.ticker.info['shortName']} stock price in next {str(mc_sim.time_horizon)} days</p><p style='font-size:20px; text-align:center; color:grey'>{mc_sim.value_at_risk()}</p>",unsafe_allow_html=True)

    # Plot the results
    st.pyplot(mc_sim.plot_simulation_price(), clear_figure=True)
    #######################################################################################################################