## Import Modules
from datetime import datetime,timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf


def initialize_ticker_obj():
    st.session_state['ticker_obj'] = yf.Ticker(st.session_state.ticker)


def get_histoy(period, interval):
    return st.session_state.ticker_obj.history(period, interval)


def format_table(content):
    df = pd.Series(content).reset_index()
    s = df.style.set_properties(subset=[0], **{'font-weight': 'bold', 'text-align': 'right'})
    s = s.hide_index().hide_columns()
    return s.to_html()


def human_format(num):
    """
    Format number to human-readable string.
    https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings/45846841#45846841
    """
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T'][magnitude])


def create_chart(data):
    fig = px.area(data, x=data.index, y="Close")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_xaxes(showspikes=True, spikemode="across", title=None)
    fig.update_yaxes(showspikes=True, spikemode="across", title=None)
    return fig


def run():
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
    
    ## Title
    st.markdown(f"<p style='font-size:50px; font-weight:bold; margin-bottom:-20px'>{st.session_state.ticker_obj.info['longName']} ({st.session_state.ticker})</p><span style='font-size:15px; color:grey'>Currency in {st.session_state.ticker_obj.info['currency']}</span>",unsafe_allow_html=True)
    
    ## Metric - Current Price andchange from last close
    st.markdown("""
    <style>
    [data-testid=stMetricLabel]{
        font-size:20px;
    }
    </style>
    """,unsafe_allow_html=True)
    st.metric(label="Current Price", value=st.session_state.ticker_obj.info['currentPrice'], delta=round(st.session_state.ticker_obj.info['currentPrice']-st.session_state.ticker_obj.info['previousClose'], 2))

    col_info1, col_info2, col_chart = st.columns([1,1,2], gap="medium")

    col_info1_content = {"Previous Close": st.session_state.ticker_obj.info['previousClose'],
        "Open": st.session_state.ticker_obj.info['open'],
        "Bid": f"{st.session_state.ticker_obj.info['bid']} x {st.session_state.ticker_obj.info['bidSize']}",
        "Ask": f"{st.session_state.ticker_obj.info['ask']} x {st.session_state.ticker_obj.info['askSize']}",
        "Days's Range": f"{st.session_state.ticker_obj.info['dayLow']} - {st.session_state.ticker_obj.info['dayHigh']}",
        "52 Week Range": f"{st.session_state.ticker_obj.info['fiftyTwoWeekLow']} - {st.session_state.ticker_obj.info['fiftyTwoWeekHigh']}",
        "Volume": f"{st.session_state.ticker_obj.info['volume']:,}",
        "Average Volume": f"{st.session_state.ticker_obj.info['averageVolume']:,}"
    }

    col_info2_content = {
        "Market Cap": human_format(st.session_state.ticker_obj.info['marketCap']),
        "Beta": st.session_state.ticker_obj.info['beta'],
        "PE Ratio (TTM)": st.session_state.ticker_obj.info['trailingPE'],
        "EPS (TTM)": st.session_state.ticker_obj.info['trailingEps'],
        "Earnings Date": ' - '.join(st.session_state.ticker_obj.calendar.loc['Earnings Date'].map(lambda x: x.date().strftime('%b %d, %Y')).to_list()) if st.session_state.ticker_obj.calendar.loc['Earnings Date'].any() else 'N/A',
        "Forward Dividend & Yield": f"{st.session_state.ticker_obj.info.get('dividendRate', 'N/A')} ({str(st.session_state.ticker_obj.info['dividendYield'])+'%' if st.session_state.ticker_obj.info['dividendYield'] else 'N/A'})",
        "exDividendDate": pd.to_datetime(st.session_state.ticker_obj.info['exDividendDate'], unit='s', origin='unix').strftime("%b %d, %Y") if st.session_state.ticker_obj.info['exDividendDate'] else "N/A",
        "1y Target EST": st.session_state.ticker_obj.info['targetMeanPrice']
    }

    ## Display table w/o index/column header - https://stackoverflow.com/questions/69875734/how-to-hide-dataframe-index-on-streamlit
    with col_info1:
        st.write(format_table(col_info1_content), unsafe_allow_html=True)
    with col_info2:
        st.write(format_table(col_info2_content), unsafe_allow_html=True)
    with col_chart:
        tab_1m, tab_6m, tab_ytd, tab_1y, tab_5y, tab_max = st.tabs(["1M", "6M", "YTD", "1Y", "5Y", "MAX"])
        with tab_1m:
            data = get_histoy(period="1mo", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        with tab_6m:
            data = get_histoy(period="6mo", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        with tab_ytd:
            data = get_histoy(period="ytd", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        with tab_1y:
            data = get_histoy(period="1y", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        with tab_5y:
            data = get_histoy(period="5y", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        with tab_max:
            data = get_histoy(period="max", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        


if __name__ == '__main__':
    run()