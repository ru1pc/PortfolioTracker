import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os,sys

# Add the parent directory of 'backend' to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import backend.database as db 

st.set_page_config(page_title="Portfolio Tracker", layout="wide")



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



def performance_chart(portfolio_name):
    if portfolio_name == "Overview":
        history_data = db.get_history_overview()
    else:
        history_data = db.get_portfolio_history(portfolio_name)
    fig_history = px.area(
        history_data,
        x='Date',
        y='Value',
        title='Performance',
        labels={'Date': '', 'Value': ''},
        template='plotly_white'  # Optional: Use a clean theme
    )       
    fig_history.update_layout(width=600, height=400)
    fig_history.update_traces(mode="markers+lines", hovertemplate="Date: %{x|%Y-%m-%d}<br>Balance: $%{y:.2f}")
    st.plotly_chart(fig_history, use_container_width=True)

def allocation_chart(portfolio_name,allocation_view):
    if portfolio_name == "Overview":
        if not allocation_view:
            allocation_view = "asset"
        allocation_view = allocation_view.lower()
        allocation_df = db.get_allocation_by(allocation_view)
        fig_allocation = px.pie(allocation_df, values=allocation_df['total_allocation'], names=allocation_df[allocation_view], title=f"{allocation_view.capitalize()}s")    
    else:
        allocation_df = db.get_holdings(portfolio_name)
        fig_allocation = px.pie(allocation_df, values="Balance", names='Asset', title='Assets')

    st.plotly_chart(fig_allocation, use_container_width=True)

def PortfolioMetrics(portfolio,allocation_view):
    
    metricas_portfolio(portfolio)

    chart_tab, transaction_tab = st.tabs(["Charts", "Transactions"])

    with chart_tab:

        performance,allocation= st.columns(2)

        with performance:
            performance_chart(portfolio['portfolio'])
        with allocation:
            allocation_chart(portfolio['portfolio'],allocation_view)

        if portfolio['portfolio'] == "Overview":
            df_asset_metrics = db.get_assets()
        else:
            df_asset_metrics = db.get_holdings(portfolio['portfolio'])
        st.subheader(f"Holdings ({len(df_asset_metrics)})")
        st.dataframe(df_asset_metrics,hide_index=True)


    with transaction_tab:
        if portfolio['portfolio'] == "Overview":
            transactions = db.get_all_transactions()
        else:
            transactions = db.get_transactions_by_portfolio(portfolio['portfolio'])
        st.subheader(f"Asset Transactions ({len(transactions)})")
        st.dataframe(transactions,hide_index=True)

def menu():

    portfolios_latest_data = db.get_portfolio_latest_data()
    overview = {
        "portfolio": "Overview",
        "total_invested": portfolios_latest_data["total_invested"].sum(),
        "realised_profit": portfolios_latest_data["realised_profit"].sum(),
        "unrealised_profit": portfolios_latest_data["unrealised_profit"].sum(),
        "balance": portfolios_latest_data["balance"].sum()
    }
    
    default_focus=True
    portfolio_focus=overview
    allocation_view = "asset"
    st.sidebar.button(f"**Overview**",type='primary')
    allocation_view = st.sidebar.radio("Alocation by", ["Asset", "Portfolio","Type", "Platform"],index=None)
    
    
    st.sidebar.header(f"My Portfolios ({len(portfolios_latest_data['portfolio'])})")

    for _, portfolio in portfolios_latest_data.iterrows():
        if st.sidebar.button(f"**{portfolio['portfolio']}** *({portfolio['balance']:,.2f})*",type='tertiary'):
            default_focus=False
            portfolio_focus = portfolio
        
    PortfolioMetrics(portfolio_focus,allocation_view)
   
    st.sidebar.divider()

    if st.sidebar.button("+ Create Portfolio"):
        new_portfolio_name = st.text_input("Enter new portfolio name")
        if new_portfolio_name:
            new_portfolio = {'Portfolio': new_portfolio_name, 'Value': 0}
            portfolio_list = portfolio_list.append(new_portfolio, ignore_index=True)
            st.success(f"Portfolio '{new_portfolio_name}' created!")

menu()