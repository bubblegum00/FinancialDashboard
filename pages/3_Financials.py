import pandas as pd
import streamlit as st
import yfinance as yf


def initialize_ticker_obj():
    """
    Store the yfinance ticker object for the selected ticker
    in session state to reduce API hits and persist ticker
    selection across pages
    """
    st.session_state['ticker_obj'] = yf.Ticker(st.session_state.ticker)


if __name__=='__main__':
    ## Page config
    st.set_page_config(layout="wide")

    ####################################################### Ticker #######################################################
    ## Set ticker value in session state to persist. Default 'MSFT'
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

    ################################################# Financial Information #################################################
    tab_IS, tab_BS, tab_CF = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])

    ## Income Statement
    with tab_IS:
        tab_q, tab_y = st.tabs(["Quarterly", "Yearly"])
        ## Quaterly
        with tab_q:
            st.table(st.session_state.ticker_obj.quarterly_financials)
        ## Yearly
        with tab_y:
            st.table(st.session_state.ticker_obj.financials)
    
    ## Balance Sheet
    with tab_BS:
        tab_q, tab_y = st.tabs(["Quarterly", "Yearly"])
        ## Quaterly
        with tab_q:
            st.table(st.session_state.ticker_obj.quarterly_balance_sheet)
        ## Yearly
        with tab_y:
            st.table(st.session_state.ticker_obj.balance_sheet)
    
    ## Cash Flow
    with tab_CF:
        tab_q, tab_y = st.tabs(["Quarterly", "Yearly"])
        ## Quaterly
        with tab_q:
            st.table(st.session_state.ticker_obj.quarterly_cashflow)
        ## Yearly
        with tab_y:
            st.table(st.session_state.ticker_obj.cashflow)
    #######################################################################################################################
        