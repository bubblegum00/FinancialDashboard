import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import cufflinks as cf


def initialize_ticker_obj():
    st.session_state['ticker_obj'] = yf.Ticker(st.session_state.ticker)


def create_chart(data,chart_type,up_color="green",down_color="red"):
    ###################### From cufflinks ######################
    if chart_type=='line':
        bar_colors=[]
        base = data['Volume']
        for i in range(len(base)):
            if i != 0:
                if base[i] > base[i-1]:
                    bar_colors.append(up_color)
                else:
                    bar_colors.append(down_color)
            else:
                bar_colors.append(down_color)
    ############################################################

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Line(x=data.index, y=data['Close'], fill='tozeroy', name='close', hovertemplate=None))
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='volume', hovertemplate=None), secondary_y=True)
        fig['data'][1].update(marker=dict(color=bar_colors), opacity=0.8)
        fig.update_layout(hovermode="x", height=600)
        fig.update_xaxes(showspikes=True, spikemode="across", title=None)
        fig.update_yaxes(showspikes=True, spikemode="across", title=None, row=1, col=1)
        fig.update_yaxes(range=[0, data['Volume'].max()*3], showspikes=True, spikemode="across", title=None, showticklabels=False, secondary_y=True)
        
    elif chart_type=='candle':
        qf = cf.QuantFig(data, name=st.session_state.ticker,kind='candlestick')
        qf.add_volume()
        fig = qf.iplot(asFigure=True, up_color=up_color, down_color=down_color)
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
    return st.session_state.ticker_obj.history(period,interval,start,end)


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

    st.header(st.session_state.ticker_obj.info['longName'])
    
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