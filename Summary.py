## Import Modules
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf


def initialize_ticker_obj():
    """
    Store the yfinance ticker object for the selected ticker
    in session state to reduce API hits and persist ticker
    selection across pages
    """
    st.session_state['ticker_obj'] = yf.Ticker(st.session_state.ticker)


def format_table(content):
    """
    Format the summary table for display
    using pandas styler

    Parameters
    ----------
    content: dict
        The data to be shown as key-value pairs
    """
    df = pd.Series(content).reset_index()
    s = df.style.set_properties(subset=[0], **{'font-weight': 'bold', 'text-align': 'right'})
    s = s.hide_index().hide_columns()
    return s.to_html()


def human_format(num):
    """
    Format number to human-readable string.
    Ref: https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings/45846841#45846841

    Parameters
    ----------
    num: int
        The number to format
    """
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T'][magnitude])


def create_chart(data):
    """
    Creates line chart of closing price of stock data

    Parameters
    ----------
    data: DataFrame
        Historical closing price stored in field "Close"
    """
    fig = px.area(data, x=data.index, y="Close")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_xaxes(showspikes=True, spikemode="across", title=None)
    fig.update_yaxes(showspikes=True, spikemode="across", title=None)
    return fig


def run():
    ## Page config
    st.set_page_config(layout="wide")

    ############################################# Ticker #############################################
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
    st.sidebar.selectbox(label="Select a ticker"
                        , options=ticker_list,key='ticker'
                        , on_change=initialize_ticker_obj)
    ##############################################################
    ####################################################################################################
    
    ############################################### Title ##############################################
    title_str = f"""
    <p style='font-size:50px; font-weight:bold; margin-bottom:-20px'>
        {st.session_state.ticker_obj.info['longName']} ({st.session_state.ticker})
    </p>
    <span style='font-size:15px; color:grey'>
        Currency in {st.session_state.ticker_obj.info['currency']}
    </span>
    """
    st.markdown(title_str,unsafe_allow_html=True)
    ####################################################################################################

    ######################## Metric - Current Price and change from last close #########################
    st.markdown("""
    <style>
    [data-testid=stMetricLabel]{
        font-size:20px;
    }
    </style>
    """,unsafe_allow_html=True)
    st.metric(label="Current Price"
                , value=st.session_state.ticker_obj.info['currentPrice']
                , delta=round(st.session_state.ticker_obj.info['currentPrice']-st.session_state.ticker_obj.info['previousClose'], 2))
    ####################################################################################################

    ########################################## Summary Data ############################################
    ## Summary Data:
    ### 1. Previous Close, Open, Bid, Ask, Day's Range, 52 Week Range, Volume, Avg. Volume
    ### 2. Market Cap, Beta(5Y Monthly), PE Ratio (TTM), EPS (TTM), Earnings Date, 
    ###    Forward Dividend & Yield, Ex-Dividend Date, 1y target Est
    ### 3. Chart for historical closing price
    col_info1, col_info2, col_chart = st.columns([1,1,2], gap="medium")

    ######################## Data Column 1 ########################
    col_info1_content = {"Previous Close": f"{round(st.session_state.ticker_obj.info['previousClose'], 2) if st.session_state.ticker_obj.info['previousClose'] else 'N/A'}",
        "Open": f"{round(st.session_state.ticker_obj.info['open'], 2) if st.session_state.ticker_obj.info['open'] else 'N/A'}",
        "Bid": f"{st.session_state.ticker_obj.info['bid']} x {st.session_state.ticker_obj.info['bidSize']}",
        "Ask": f"{st.session_state.ticker_obj.info['ask']} x {st.session_state.ticker_obj.info['askSize']}",
        "Days's Range": f"{st.session_state.ticker_obj.info['dayLow']} - {st.session_state.ticker_obj.info['dayHigh']}",
        "52 Week Range": f"{st.session_state.ticker_obj.info['fiftyTwoWeekLow']} - {st.session_state.ticker_obj.info['fiftyTwoWeekHigh']}",
        "Volume": f"{st.session_state.ticker_obj.info['volume']:,}",
        "Average Volume": f"{st.session_state.ticker_obj.info['averageVolume']:,}"
    }

    with col_info1:
        st.write(format_table(col_info1_content), unsafe_allow_html=True)
    ###############################################################
    
    ######################## Data Column 2 ########################
    col_info2_content = {
        "Market Cap": human_format(st.session_state.ticker_obj.info['marketCap']),
        "Beta": f"{round(st.session_state.ticker_obj.info['beta'], 2) if st.session_state.ticker_obj.info['beta'] else 'N/A'}",
        "PE Ratio (TTM)": f"{round(st.session_state.ticker_obj.info['trailingPE'], 2) if st.session_state.ticker_obj.info['trailingPE'] else 'N/A'}",
        "EPS (TTM)": f"{round(st.session_state.ticker_obj.info['trailingEps'], 2) if st.session_state.ticker_obj.info['trailingEps'] else 'N/A'}",
        "Earnings Date": ' - '.join(st.session_state.ticker_obj.calendar.loc['Earnings Date'].map(lambda x: x.date().strftime('%b %d, %Y')).to_list()) if st.session_state.ticker_obj.calendar.loc['Earnings Date'].any() else 'N/A',
        "Forward Dividend & Yield": f"{st.session_state.ticker_obj.info.get('dividendRate', 'N/A')} ({str(round(st.session_state.ticker_obj.info['dividendYield']*100, 2))+'%' if st.session_state.ticker_obj.info['dividendYield'] else 'N/A'})",
        "exDividendDate": pd.to_datetime(st.session_state.ticker_obj.info['exDividendDate'], unit='s', origin='unix').strftime("%b %d, %Y") if st.session_state.ticker_obj.info['exDividendDate'] else "N/A",
        "1y Target EST": f"{round(st.session_state.ticker_obj.info['targetMeanPrice'], 2) if st.session_state.ticker_obj.info['targetMeanPrice'] else 'N/A'}"
    }
    with col_info2:
        st.write(format_table(col_info2_content), unsafe_allow_html=True)
    ###############################################################

    ######################## Chart Column ########################
    with col_chart:
        ## Multiple tabs show different period of historical
        ## closing price data
        tab_1m, tab_6m, tab_ytd, tab_1y, tab_5y, tab_max = st.tabs(["1M", "6M", "YTD", "1Y", "5Y", "MAX"])
        ## 1 Month
        with tab_1m:
            data = st.session_state.ticker_obj.history(period="1mo", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        ## 6 Month
        with tab_6m:
            data = st.session_state.ticker_obj.history(period="6mo", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        ## Year to Date
        with tab_ytd:
            data = st.session_state.ticker_obj.history(period="ytd", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        ## 1 Year
        with tab_1y:
            data = st.session_state.ticker_obj.history(period="1y", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        ## 5 Year
        with tab_5y:
            data = st.session_state.ticker_obj.history(period="5y", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        ## All available data
        with tab_max:
            data = st.session_state.ticker_obj.history(period="max", interval="1d")
            fig = create_chart(data)
            st.plotly_chart(fig, use_container_width=True)
    ###############################################################  
    ####################################################################################################

    ############################################## Source ##############################################
    source_str="""
    <p style='font-size:15px; color:grey; text-align:right'>
        Source: Yahoo Finance
    </p>
    """
    st.markdown(source_str,unsafe_allow_html=True)
    #####################################################################################################

if __name__ == '__main__':
    run()