import streamlit as st
import pandas as pd
import yfinance as yf


def initialize_ticker_obj():
    st.session_state['ticker_obj'] = yf.Ticker(st.session_state.ticker)


if __name__=='__main__':
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

    ##################################################### Company Name ####################################################
    st.header(st.session_state.ticker_obj.info['longName'])
    #######################################################################################################################


    tab_IS, tab_BS, tab_CF = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])

    ## Income Statement
    with tab_IS:
        tab_q, tab_y = st.tabs(["Quarterly", "Yearly"])
        with tab_q:
            st.table(st.session_state.ticker_obj.quarterly_financials)
        with tab_y:
            st.table(st.session_state.ticker_obj.financials)
    
    ## Balance Sheet
    with tab_BS:
        tab_q, tab_y = st.tabs(["Quarterly", "Yearly"])
        with tab_q:
            st.table(st.session_state.ticker_obj.quarterly_balance_sheet)
        with tab_y:
            st.table(st.session_state.ticker_obj.balance_sheet)
    
    ## Cash Flow
    with tab_CF:
        tab_q, tab_y = st.tabs(["Quarterly", "Yearly"])
        with tab_q:
            st.table(st.session_state.ticker_obj.quarterly_cashflow)
        with tab_y:
            st.table(st.session_state.ticker_obj.cashflow)
        