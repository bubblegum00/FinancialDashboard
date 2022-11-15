## Import Modules
from datetime import datetime,timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf


def get_info():
    st.session_state['info'] = yf.Ticker(st.session_state.ticker).info


@st.cache
def get_histoy(period, interval):
    return yf.Ticker(st.session_state.ticker).history(period, interval)


def format_info_table(content):
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
    st.set_page_config(layout="wide")

    if "ticker" not in st.session_state:
        st.session_state.ticker = "MSFT"
    else:
        st.session_state.ticker = st.session_state.ticker

    ############################################ Reference fin_dashboard01.py ############################################
    # Get the list of stock tickers from S&P500
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']

    # Add the ticker selection on the sidebar
    ticker_val = st.sidebar.selectbox(label="Select a ticker", options=ticker_list,key='ticker')
    get_info()
    #######################################################################################################################
    
    ## Title
    st.header(f"{st.session_state.info['longName']} ({st.session_state.ticker})")
    st.caption(f"Currency in {st.session_state.info['currency']}")
    st.metric(label="Current Price", value=st.session_state.info['currentPrice'], delta=round(st.session_state.info['currentPrice']-st.session_state.info['previousClose'], 2))

    col_info1, col_info2, col_chart = st.columns([1,1,2], gap="medium")

    col_info1_content = {"Previous Close": st.session_state.info['previousClose'],
        "Open": st.session_state.info['open'],
        "Bid": f"{st.session_state.info['bid']} x {st.session_state.info['bidSize']}",
        "Ask": f"{st.session_state.info['ask']} x {st.session_state.info['askSize']}",
        "Days's Range": f"{st.session_state.info['dayLow']} - {st.session_state.info['dayHigh']}",
        "52 Week Range": f"{st.session_state.info['fiftyTwoWeekLow']} - {st.session_state.info['fiftyTwoWeekHigh']}",
        "Volume": f"{st.session_state.info['volume']:,}",
        "Average Volume": f"{st.session_state.info['averageVolume']:,}"
    }

    col_info2_content = {
        "Market Cap": human_format(st.session_state.info['marketCap']),
        "Beta": st.session_state.info['beta'],
        "PE Ratio (TTM)": st.session_state.info['trailingPE'],
        "EPS (TTM)": st.session_state.info['trailingEps'],
        "Earnings Date": "a",
        "Forward Dividend & Yield": f"{st.session_state.info['dividendRate'] if st.session_state.info['dividendRate'] else 'N/A'} ({str(st.session_state.info['dividendYield'])+'%' if st.session_state.info['dividendYield'] else 'N/A'})",
        "exDividendDate": pd.to_datetime(st.session_state.info['exDividendDate']).strftime("%b %d, %Y") if st.session_state.info['exDividendDate'] else "N/A",
        "1y Target EST": 'a'
    }

    ## Display table w/o index/column header - https://stackoverflow.com/questions/69875734/how-to-hide-dataframe-index-on-streamlit
    with col_info1:
        st.write(format_info_table(col_info1_content), unsafe_allow_html=True)
    with col_info2:
        st.write(format_info_table(col_info2_content), unsafe_allow_html=True)
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