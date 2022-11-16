import streamlit as st
import yfinance as yf
import pandas as pd


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

    ##################################################### Company Name ####################################################
    st.header(st.session_state.ticker_obj.info['longName'])
    #######################################################################################################################

    ################################################ Companny Information #################################################
    ## Two columns:
    ##  1. Display Address, phone and website
    ##  2. Display information about sector, industry and employee count
    col_address, col_info = st.columns(2)
    ######################### FROM Stackoverflow #########################
    st.markdown("""
    <style>
    [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
        gap: 0rem;
    }
    </style>
    """,unsafe_allow_html=True)
    #######################################################################
    
    ## Display Address, phone and website
    with col_address:
        st.write(st.session_state.ticker_obj.info['address1'])
        if "state" in st.session_state.ticker_obj.info:
            line2 = f"{st.session_state.ticker_obj.info['city']}, {st.session_state.ticker_obj.info['state']} {st.session_state.ticker_obj.info['zip']}"
        else:
            line2 = f"{st.session_state.ticker_obj.info['city']} {st.session_state.ticker_obj.info['zip']}"
        st.write(line2)
        st.write(st.session_state.ticker_obj.info['country'])
        st.write(st.session_state.ticker_obj.info['phone'])
        st.write(st.session_state.ticker_obj.info['website'])
    
    ## Display information about sector, industry and employee count
    with col_info:
        st.write(f"Sector(s): **{st.session_state.ticker_obj.info.get('sector', 'N/A')}**")
        st.write(f"Industry: **{st.session_state.ticker_obj.info.get('industry', 'N/A')}**")
        st.write(f"Full Time Employees: **{st.session_state.ticker_obj.info['fullTimeEmployees']:,}**")
    #######################################################################################################################

    ################################################# Company Description #################################################
    st.subheader("Description")
    st.markdown(f"<p style='text-align:justify; word-break:keep-all'>{st.session_state.ticker_obj.info['longBusinessSummary']}</p>", unsafe_allow_html=True)
    #######################################################################################################################

    ################################################# Major Shareholders ##################################################
    st.subheader("Share Distribution")
    df = st.session_state.ticker_obj.major_holders
    s = df.style.set_properties(subset=[1], **{'font-weight': 'bold', 'text-align': 'right'})
    s = s.hide_index().hide_columns()
    st.write(s.to_html(), unsafe_allow_html=True)
    st.markdown('')

    st.subheader("Institutional Holders")
    df = st.session_state.ticker_obj.institutional_holders
    s = df.style.set_properties(subset=['Holder', '% Out'], **{'font-weight': 'bold', 'text-align': 'right'})
    s = s.hide_index()
    st.write(s.to_html(), unsafe_allow_html=True)
    st.markdown('')

    st.subheader("Mutual Fund Holders")
    df = st.session_state.ticker_obj.mutualfund_holders
    s = df.style.set_properties(subset=['Holder', '% Out'], **{'font-weight': 'bold', 'text-align': 'right'})
    s = s.hide_index()
    st.write(s.to_html(), unsafe_allow_html=True)
    #######################################################################################################################