## Import Modules
from datetime import datetime, timedelta

import cufflinks as cf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf


def initialize_ticker_obj():
    """
    Store the yfinance ticker object for the selected ticker
    in session state to reduce API hits and persist ticker
    selection across pages
    """
    st.session_state['ticker_obj'] = yf.Ticker(st.session_state.ticker)


def create_chart(data,chart_type,ma=None,up_color="green",down_color="red"):
    """
    Create the ticker history chart and 
    return the figure

    Parameters
    ----------
    data: DataFrame
        The stock price history data. Expected to have
        the following fields: Open, Close, High, Low
        , Volume
    
    chart_type: str
        The type of chart to create.
        Valid chart_type: line, candle
    
    ma: int
        Number of periods to use for simple
        moving average. None indicates not to
        add a sma line

    up_color: str
        The color to use to show iprovement in a
        field from last period
        Default: green
    
    down_color: str
        The color to use to show decline in a
        field from last period
        Default: red
    """
    if chart_type=='line':
    ###################### Ref: cufflinks ######################
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
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', fill='tozeroy', name='close', hovertemplate=None))
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='volume', hovertemplate=None), secondary_y=True)
        fig['data'][1].update(marker=dict(color=bar_colors), opacity=0.8)
        if ma:
            data[f'SMA({ma})'] = data['Close'].rolling(ma).mean()
            fig.add_trace(go.Scatter(x=data.index, y=data[f'SMA({ma})'], name=f'SMA({ma})', hovertemplate=None, line=dict(color="orange")))
        fig.update_layout(hovermode="x", height=600)
        fig.update_xaxes(showspikes=True, spikemode="across", title=None)
        fig.update_yaxes(showspikes=True, spikemode="across", title=None, row=1, col=1)
        fig.update_yaxes(range=[0, data['Volume'].max()*3], showspikes=True, spikemode="across", title=None, showticklabels=False, secondary_y=True)
    
    elif chart_type=='candle':
        qf = cf.QuantFig(data, name=st.session_state.ticker,kind='candlestick')
        qf.add_volume()
        if ma:
            qf.add_sma(ma)
        fig = qf.iplot(asFigure=True, up_color=up_color, down_color=down_color)
        fig.update_layout(hovermode="x")
        fig.update_xaxes(showspikes=True, spikemode="across", title=None)
        fig.update_yaxes(showspikes=True, spikemode="across", title=None)
    
    return fig

def get_histoy(period="1mo", interval="1d", start=None, end=None):
    """
    Get the history of the stock for the specified period or dates
    and interval
    persistance

    Parameters
    ----------
    period: str
        Specifies the period for which history is returned
        Either Use period parameter or use start and end
        Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        Default: 1mo
    
    interval: str
        The interval at which stock data is available
        Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        Intraday data cannot exceed last 60 days
        Default: 1d
    
    start: str
        Download start date string (YYYY-MM-DD) or _datetime.
        Default is 1900-01-01
    end: str
        Download end date string (YYYY-MM-DD) or _datetime.
        Default is now
    """
    return st.session_state.ticker_obj.history(period,interval,start,end)


if __name__ == '__main__':
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

    ############################################### Title ##############################################
    st.header(st.session_state.ticker_obj.info['longName'])
    ####################################################################################################

    ########################################### Input Boxes ############################################
    ## 1. Select interval from the dropdown - 1 Day, 5 Day, 1 Week, 1 Month, 3 Month
    ## 2. Select the chart type - line, candle
    col_interval, col_chart_type = st.columns(2)
    
    with col_interval:
        interval = st.selectbox(label="Interval"
                        , options=("1 Day", "5 Day", "1 Week", "1 Month", "3 Month")
                        , help="Historical data interval")
    
    ## Parsing Interval value
    if interval == "1 Day":
        interval = "1d"
        ma = 50
    elif interval == "5 Day":
        interval = "5d"
        ma = 50
    elif interval == "1 Week":
        interval = "1wk"
        ma = 7
    elif interval == "1 Month":
        interval = "1mo"
        ma = None
    elif interval == "3 Month":
        interval = "3mo"
        ma = None
    else:
        interval = "1d"
        ma = 50

    with col_chart_type:
        chart_type = st.selectbox(label="Chart Type"
                        , options=("line", "candle")
                        , help="Visualization type")
    ####################################################################################################
    
    ############################################### Period ##############################################
    tab_date_range, tab_1m, tab_6m, tab_ytd, tab_1y, tab_3y, tab_5y, tab_max = st.tabs(["Date Range", "1M", "6M", "YTD", "1Y", "3Y", "5Y", "MAX"])
    with tab_date_range:
        ## Date range for historical data
        sb_col1, sb_col2 = st.columns(2)
        start_date = sb_col1.date_input(label="Start date"
                                        , value=datetime.today().date() - timedelta(days=30))
        end_date = sb_col2.date_input(label="End date"
                                    , value=datetime.today().date())
        ## Historical data for selected period and interval
        data = get_histoy(period=None,interval=interval,start=start_date,end=end_date)
        ## Plotly figure object containing plotting data
        if (end_date-start_date).days > 50:
            fig = create_chart(data, chart_type, ma)
        else:
            fig = create_chart(data, chart_type)
        ## Show visualization
        st.plotly_chart(fig, use_container_width=True)
    with tab_1m:
        ## Historical data for selected period and interval
        data = get_histoy(period="1mo", interval=interval)
        ## Plotly figure object containing plotting data
        fig = create_chart(data, chart_type)
        ## Show visualization
        st.plotly_chart(fig, use_container_width=True)
    with tab_6m:
        ## Historical data for selected period and interval
        data = get_histoy(period="6mo", interval=interval)
        ## Plotly figure object containing plotting data
        fig = create_chart(data, chart_type, ma)
        ## Show visualization
        st.plotly_chart(fig, use_container_width=True)
    with tab_ytd:
        ## Historical data for selected period and interval
        data = get_histoy(period="ytd", interval=interval)
        ## Plotly figure object containing plotting data
        if (datetime.today()-datetime(datetime.today().year, 1, 1)).days > 50:
            fig = create_chart(data, chart_type, ma)
        else:
            fig = create_chart(data, chart_type)
        ## Show visualization
        st.plotly_chart(fig, use_container_width=True)
    with tab_1y:
        ## Historical data for selected period and interval
        data = get_histoy(period="1y", interval=interval)
        ## Plotly figure object containing plotting data
        fig = create_chart(data, chart_type, ma)
        ## Show visualization
        st.plotly_chart(fig, use_container_width=True)
    with tab_3y:
        ## Historical data for selected period and interval
        data = get_histoy(period="3y", interval=interval)
        ## Plotly figure object containing plotting data
        fig = create_chart(data, chart_type, ma)
        ## Show visualization
        st.plotly_chart(fig, use_container_width=True)
    with tab_5y:
        ## Historical data for selected period and interval
        data = get_histoy(period="5y", interval=interval)
        ## Plotly figure object containing plotting data
        fig = create_chart(data, chart_type, ma)
        ## Show visualization
        st.plotly_chart(fig, use_container_width=True)
    with tab_max:
        ## Historical data for selected period and interval
        data = get_histoy(period="max", interval=interval)
        ## Plotly figure object containing plotting data
        fig = create_chart(data, chart_type, ma)
        ## Show visualization
        st.plotly_chart(fig, use_container_width=True)
    ####################################################################################################