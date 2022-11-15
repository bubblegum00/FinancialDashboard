import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import cufflinks as cf


def get_info():
    st.session_state['info'] = yf.Ticker(st.session_state.ticker).info


def create_chart(data,chart_type):
    if chart_type=='line':
        fig = px.area(data, x=data.index, y="Close")
        fig.update_traces(hovertemplate=None)
        fig.update_layout(hovermode="x")
        fig.update_xaxes(showspikes=True, spikemode="across", title=None)
        fig.update_yaxes(showspikes=True, spikemode="across", title=None)
        # return fig
    elif chart_type=='candle':
        qf = cf.QuantFig(data, name=st.session_state.ticker)
        qf.add_volume()
        fig = qf.iplot(asFigure=True, up_color="green", down_color="red")
        fig.update_layout(hovermode="x")
        fig.update_xaxes(showspikes=True, spikemode="across", title=None)
        fig.update_yaxes(showspikes=True, spikemode="across", title=None)
    return fig

def get_histoy(period="1mo", interval="1d", start=None, end=None):
    if interval == "1 Day":
        interval = "1d"
    elif interval == "5 Day":
        interval = "5d"
    elif interval == "1 Week":
        interval = "1wk"
    elif interval == "1 Month":
        interval = "1mo"
    elif interval == "3 Month":
        interval = "3mo"
    else:
        interval = "1d"
    return yf.Ticker(st.session_state.ticker).history(period, interval,start,end)


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
    if "info" not in st.session_state:
        get_info()
    else:
        st.session_state.info = st.session_state.info
    
    ################ Reference fin_dashboard01.py ################
    # Get the list of stock tickers from S&P500
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']

    # Add the ticker selection on the sidebar
    st.sidebar.selectbox(label="Select a ticker", options=ticker_list,key='ticker', on_change=get_info)
    ##############################################################
    #######################################################################################################################

    st.write(st.session_state['ticker'])
    
    col_interval, col_chart_type = st.columns(2)
    
    with col_interval:
        _ = st.selectbox(label="Interval", options=("1 Day", "5 Day", "1 Week", "1 Month", "3 Month"), key="interval")
    
    with col_chart_type:
        _ = st.selectbox(label="Chart Type", options=("line", "candle"), key="chart_type")
    
    
    tab_date_range, tab_1m, tab_6m, tab_ytd, tab_1y, tab_3y, tab_5y, tab_max = st.tabs(["Date Range", "1M", "6M", "YTD", "1Y", "3Y", "5Y", "MAX"])
    with tab_date_range:
        # # Add select begin-end date
        sb_col1, sb_col2 = st.columns(2)
        start_date = sb_col1.date_input("Start date", datetime.today().date() - timedelta(days=30))
        end_date = sb_col2.date_input("End date", datetime.today().date())
        data = get_histoy(period=None, interval="Day",start=start_date,end=end_date)
        fig = create_chart(data, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True)
    with tab_1m:
        data = get_histoy(period="1mo", interval=st.session_state.interval)
        fig = create_chart(data, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True)
    with tab_6m:
        data = get_histoy(period="6mo", interval=st.session_state.interval)
        fig = create_chart(data, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True)
    with tab_ytd:
        data = get_histoy(period="ytd", interval=st.session_state.interval)
        fig = create_chart(data, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True)
    with tab_1y:
        data = get_histoy(period="1y", interval=st.session_state.interval)
        fig = create_chart(data, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True)
    with tab_3y:
        data = get_histoy(period="3y", interval=st.session_state.interval)
        fig = create_chart(data, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True)
    with tab_5y:
        data = get_histoy(period="5y", interval=st.session_state.interval)
        fig = create_chart(data, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True)
    with tab_max:
        data = get_histoy(period="max", interval=st.session_state.interval)
        fig = create_chart(data, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True)