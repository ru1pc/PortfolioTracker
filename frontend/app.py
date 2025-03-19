import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os,sys

# Add the parent directory of 'backend' to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import backend.database as db 

st.set_page_config(page_title="Portfolio Tracker", layout="wide")

df_alltransactions = db.get_all_transactions()

def metricas_portfolio(portfolio):
    st.subheader(portfolio['portfolio'])
    balance,total_invested,realised_profit,unrealised_profit = st.columns(4) 
    with balance:
        st.metric("Balance", f"${portfolio['balance']:,.2f}")
    with total_invested:
        st.metric("Total Invested", f"${portfolio['total_invested']:,.2f}")
    with realised_profit:
        st.metric("Realised Profit", f"${portfolio['realised_profit']:,.2f}")
    with unrealised_profit:
        st.metric("Unrealised Profit", f"${portfolio['unrealised_profit']:,.2f}")

def PortfolioMetrics_overview(portfolio,allocation_view):
    
    metricas_portfolio(portfolio)
    
    chart_tab, transaction_tab = st.tabs(["Charts", "Transactions"])

    with chart_tab:

        performance,allocation= st.columns(2)

        with performance:
            # TODO: sum balances of portfolios group by date
            history_data = db.get_history_overview()
            fig_history = px.area(
                history_data,
                x='Date',
                y='Value',
                title='Performance',
                labels={'Date': '', 'Value': ''},
                template='plotly_white'  # Optional: Use a clean theme
            )       
            fig_history.update_layout(width=600, height=400)
            st.plotly_chart(fig_history, use_container_width=True)

        with allocation:
            # TODO: get_assets holdings / overview_balance
            if allocation_view =="Asset":
                allocation_data = {
                    'Asset': ['BTC'],
                    'Percentage': [100]
                }
                allocation_df = pd.DataFrame(allocation_data)
                fig_allocation = px.pie(allocation_df, values='Percentage', names='Asset', title='Assets')
            elif allocation_view == "Portfolio":
                # TODO: get transactions group by asset , sum(asset holdings) / overview_balance group by portfolio?
                allocation_data = {
                    'Portfolio': ['Portfolio1'],
                    'Percentage': [100]
                }
                allocation_df = pd.DataFrame(allocation_data)
                fig_allocation = px.pie(allocation_df, values='Percentage', names='Portfolio', title='Portfolios')
            elif allocation_view == "Asset Class":
                # TODO: get transactions group by asset , sum(asset holdings) / overview_balance group by portfolio?
                allocation_data = {
                    'Type': ['Crypto'],
                    'Percentage': [100]
                }
                allocation_df = pd.DataFrame(allocation_data)
                fig_allocation = px.pie(allocation_df, values='Percentage', names='Type', title='Asset class')
            else:
                # TODO: get transactions group by asset , sum(asset holdings) / overview_balance group by platform?
                allocation_data = {
                    'Platform': ['Binance'],
                    'Percentage': [100]
                }
                allocation_df = pd.DataFrame(allocation_data)
                fig_allocation = px.pie(allocation_df, values='Percentage', names='Platform', title='Platform')
            st.plotly_chart(fig_allocation, use_container_width=True)

        st.subheader("Holdings")
        df_asset_metrics = db.get_assets()
        st.dataframe(df_asset_metrics,hide_index=True)


    with transaction_tab:
        st.subheader("Asset Transactions")
        st.dataframe(df_alltransactions,hide_index=True)

def PortfolioMetrics(portfolio):
    
    metricas_portfolio(portfolio)

    chart_tab, transaction_tab = st.tabs(["Charts", "Transactions"])

    with chart_tab:

        performance,allocation= st.columns(2)

        with performance:
            ## TODO: select date, balance from portfolio where portfolio = portfolio
            history_data = {
                    'Date': ['17 Mar', '4:00 AM', '8:00 AM', '12:00 PM', '4:00 PM', '8:00 PM'],
                    'Value': [82000, 83000, 83500, 84000, 84500, 85000]
                }
            history_df = pd.DataFrame(history_data)
            fig_history = px.area(
                history_df,
                x='Date',
                y='Value',
                title='Performance',
                labels={'Date': '', 'Value': ''},
                template='plotly_white'  # Optional: Use a clean theme
            )       
            fig_history.update_layout(width=600, height=400)
            st.plotly_chart(fig_history, use_container_width=True)

        with allocation:
                # TODO: get assets by portfolio , asset_balance / portfolio_balance * 100%
                allocation_data = {
                    'Asset': ['BTC'],
                    'Percentage': [100]
                }
                allocation_df = pd.DataFrame(allocation_data)
                fig_allocation = px.pie(allocation_df, values='Percentage', names='Asset', title='Assets')
        
                st.plotly_chart(fig_allocation, use_container_width=True)

        st.subheader("Holdings")
        # TODO: get_asset_by_portfolio
        df_asset_metrics = db.get_asset()
        st.dataframe(df_asset_metrics,hide_index=True)


    with transaction_tab:
        # TODO: get transactions by portfolio
        st.subheader("Asset Transactions")
        st.dataframe(df_alltransactions,hide_index=True)

def menu(portfolios_latest_data):

    overview = {
        "portfolio": "Overview",
        "total_invested": portfolios_latest_data["total_invested"].sum(),
        "realised_profit": portfolios_latest_data["realised_profit"].sum(),
        "unrealised_profit": portfolios_latest_data["unrealised_profit"].sum(),
        "balance": portfolios_latest_data["balance"].sum()
    }
    
    default_focus=True
    portfolio_focus=overview
    st.sidebar.button(f"**Overview**",type='primary')
    allocation_view = st.sidebar.radio("Alocation by", ["Asset", "Portfolio","Asset Class", "Platform"],index=None)
    
    
    st.sidebar.header(f"My Portfolios({len(portfolios_latest_data['portfolio'])})")

    for _, portfolio in portfolios_latest_data.iterrows():
        if st.sidebar.button(f"**{portfolio['portfolio']}** *({portfolio['balance']:,.2f})*",type='tertiary'):
            default_focus=False
            portfolio_focus = portfolio
        
    if default_focus:
        PortfolioMetrics_overview(portfolio_focus,allocation_view)
    else:
        PortfolioMetrics(portfolio_focus)
    
    st.sidebar.divider()

    if st.sidebar.button("+ Create Portfolio"):
        new_portfolio_name = st.text_input("Enter new portfolio name")
        if new_portfolio_name:
            new_portfolio = {'Portfolio': new_portfolio_name, 'Value': 0}
            portfolio_list = portfolio_list.append(new_portfolio, ignore_index=True)
            st.success(f"Portfolio '{new_portfolio_name}' created!")

portfolios_latest_data = db.get_portfolio_latest_data()
#print(portfolios_latest_data)

menu(portfolios_latest_data)

#dummy(allocation_view)


    