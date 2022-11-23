from humanize import number
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


def initialize_ticker_obj():
    """
    Store the yfinance ticker object for the selected ticker
    in session state to reduce API hits and persist ticker
    selection across pages
    """
    st.session_state['ticker_obj'] = yf.Ticker(st.session_state.ticker)


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

    ######################################################## Title ########################################################
    st.header(st.session_state.ticker_obj.info['longName'])
    #######################################################################################################################

    ######################################################## Data #########################################################
    ## Stop Execution if no data available
    if st.session_state.ticker_obj.sustainability is None:
        st.text("Sustainaility data is currently unavailable!!")
        st.stop()

    ## Data
    sustain_se = st.session_state.ticker_obj.sustainability.squeeze()
    #######################################################################################################################

    ################################ Environment, Social and Governance (ESG) Risk Ratings ################################
    ## Title for sub-section
    st.subheader('Environment, Social and Governance (ESG) Risk Ratings')
    
    ## Description
    ### Text Reference: Yahoo Finance
    help_str_esg = "Sustainalytics' ESG Risk Ratings assess the degree to which a company's enterprise business value is at risk driven by environmental, social and governance issues. The rating employs a two-dimensional framework that combines an assessment of a company's exposure to industry-specific material ESG issues with an assessment of how well the company is managing those issues. The final ESG Risk Ratings scores are a measure of unmanaged risk on an absolute scale of 0-100, with a lower score signaling less unmanaged ESG Risk."
    formatted_help_str_esg = f"""
    <p style='text-align:justify; word-break:keep-all'>
        {help_str_esg}
    </p>
    """
    st.markdown(formatted_help_str_esg, unsafe_allow_html=True)
    
    ## Columns to display the following:
    ### 1. Total ESG Score
    ### 2. Environment Risk Score
    ### 3. Social Risk Score
    ### 4. Governance Risk Score

    col_total, col_env, col_social, col_gov = st.columns([2,1,1,1])
    ## Total ESG Score
    with col_total:
        total_str = f"""
            <p style='font-size:20px; color:grey; margin-bottom:-10px'>
                Total ESG Risk Score
            </p>
            <p style='margin-bottom:-10px'>
                <span style='font-size:40px; font-weight:bold'>
                    {sustain_se['totalEsg']}
                </span>
                <span style='font-size:20px'>
                    |  {number.ordinal(round(sustain_se['percentile']))} percentile
                </span>
            </p>
            <p style='font-size:20px; margin-bottom: 20px'>
                {'Negligile' if sustain_se['esgPerformance']=='LAG_PERF' else 'Low' if sustain_se['esgPerformance']=='UNDER_PERF' else 'Medium' if sustain_se['esgPerformance']=='AVG_PERF' else 'High' if sustain_se['esgPerformance']=='OUT_PERF' else ''}
            </p>
            """
        st.markdown(total_str,unsafe_allow_html=True)
    ## Environment Risk Score
    with col_env:
        env_str = f"""
            <p style='font-size:15px; color:grey; margin-bottom:-10px'>
                Environment Risk Score
            </p>
            <p style='font-size:30px; font-weight:bold'>
                {sustain_se['environmentScore']}
            </p>
            """
        st.markdown(env_str,unsafe_allow_html=True)
    ## Social Risk Score
    with col_social:
        social_str = f"""
            <p style='font-size:15px; color:grey; margin-bottom:-10px'>
                Social Risk Score
            </p>
            <p style='font-size:30px; font-weight:bold'>
                {sustain_se['socialScore']}
            </p>
            """
        st.markdown(social_str,unsafe_allow_html=True)
    ## Governance Risk Score
    with col_gov:
        gov_str = f"""
            <p style='font-size:15px; color:grey; margin-bottom:-10px'>
                Governance Risk Score
            </p>
            <p style='font-size:30px; font-weight:bold'>
                {sustain_se['governanceScore']}
            </p>
            """
        st.markdown(gov_str,unsafe_allow_html=True)
    #######################################################################################################################
    
    ################################################## Controversy Level ###################################################
    ## Title for sub-section
    st.subheader('Controversy Level')
    
    ## No Data
    if not sustain_se['highestControversy']:
        st.text('Data not available..')
        st.stop()
    
    ## Description
    help_str_controversy = "Sustainalytics’ Controversies Research identifies companies involved in incidents and events that may negatively impact stakeholders, the environment or the company’s operations. Controversies are rated on a scale from one to five with five denoting the most serious controversies with the largest potential impact."
    formatted_help_str_controversy = f"""
    <p style='text-align:justify; word-break:keep-all'>
        {help_str_controversy}
    </p>
    """
    st.markdown(formatted_help_str_controversy, unsafe_allow_html=True)
    
    ## Figure
    gauge_color = 'green' if sustain_se['highestControversy'] <= 2 else 'orange' if sustain_se['highestControversy']<=4 else 'red'
    fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = sustain_se['highestControversy'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range' : [1,5], 'tickvals': [1,2,3,4,5], 'ticktext': ['1','2','3','4','5']},
                'bar': {'color': gauge_color}
            }
        ))
    st.plotly_chart(fig, use_container_width=True)
    #######################################################################################################################

    ####################################################### Source ########################################################
    source_str=f"""
    <p style='font-size:15px; color:grey; text-align:right'>
        ESG data provided by Sustainalytics, Inc. Last updated on {'/'.join(sustain_se.index.name.split('-')[::-1])}
    </p>
    """
    st.markdown(source_str,unsafe_allow_html=True)
    #######################################################################################################################