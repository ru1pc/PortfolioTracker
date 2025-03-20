import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os
import json
import tempfile

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend.database as db 
import backend.data_processing as dp
import backend.data_persistence as dper
import backend.main as main

SETTINGS_PATH = "utils/settings.json"

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
    
    st.session_state.selected_portfolio = portfolio['portfolio']
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
        

        #unique_assets = df_asset_metrics['Asset'].unique()
        #prices = {asset: main.asset_current_price(asset) for asset in unique_assets}
       # df_asset_metrics['Price'] = df_asset_metrics['Asset'].map(prices)
        st.subheader(f"Holdings ({len(df_asset_metrics)})")
        st.dataframe(df_asset_metrics,hide_index=True)

    with transaction_tab:
        
        if st.session_state.selected_portfolio == "Overview":
            transactions = db.get_all_transactions()
        else:
            transactions = db.get_transactions_by_portfolio(portfolio['portfolio'])
        
        st.subheader(f"Asset Transactions ({len(transactions)})")
        st.dataframe(transactions, hide_index=True)


def get_modules_available():
    modules_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'modules')
    available_modules = [os.path.splitext(f)[0] for f in os.listdir(modules_path) if f.endswith('.py') and not f.startswith('__')]
    return available_modules

@st.dialog("Create New Portfolio",)
def create_portfolio():
    new_portfolio_name = st.text_input("Portfolio Name", placeholder="Enter portfolio name")
    if st.button("Create", type="primary", use_container_width=True):
        db.add_new_portfolio(new_portfolio_name)
        st.rerun()

@st.dialog("Import Data",)
def import_data():
    selectPortfolio=st.selectbox("Select Portfolio",db.get_portfolios(),index=None)
    
    modules_available = get_modules_available()
    selected_module = st.selectbox(
        "Select Platform",
        modules_available,
        help="Suported platform/exchange"
    )
    uploaded_files = st.file_uploader(
    "Upload Transactions CSV", 
    type=['csv'], 
    accept_multiple_files=True,
    help="Upload one or more CSV files with your transaction data",
    
    )

    col1,col2=st.columns(2)
    with col1:
        if st.button("Import", type="primary", use_container_width=True):
            for file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                    temp_file.write(file.getbuffer())  
                    temp_filepath = temp_file.name  
                imported_data = dp.load_platform_file(temp_filepath, selected_module)
                unique_assets = imported_data['Asset'].unique()
                asset_prices = {asset: main.asset_current_price(asset) for asset in unique_assets}
                dper.save_to_db(imported_data,portfolio=selectPortfolio,asset_prices=asset_prices)
            st.rerun()
    with col2:
        if st.button("Cancel", type="secondary", use_container_width=True):
            st.rerun()

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {"DEFAULT_PORTFOLIO": "", "DEFAULT_DATA_SOURCE": ""}

# Function to save settings
def save_settings(setting,value):
    try:
        # Load existing settings
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty/corrupt, start with an empty dict
        settings = {}

    # Update the setting
    settings[setting] = value  

    # Save updated settings
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)

def settings():
    settings = load_settings()

    check_settings = st.sidebar.button("⚙️ Settings", type='tertiary')

    if check_settings:
        default_data_filepath = st.sidebar.text_input(
            "Default Data Source",
            value=settings.get("DEFAULT_DATA_FILEPATH", ""),
            key="DEFAULT_DATA_FILEPATH",
            on_change=lambda: save_settings("DEFAULT_DATA_FILEPATH", st.session_state["DEFAULT_DATA_FILEPATH"])
        )

        default_portfolio_name = st.sidebar.text_input(
            "Default Project Name",
            value=settings.get("DEFAULT_PORTFOLIO_NAME", ""),
            key="DEFAULT_PORTFOLIO_NAME",
            on_change=lambda: save_settings("DEFAULT_PORTFOLIO_NAME", st.session_state["DEFAULT_PORTFOLIO_NAME"])
        )

def menu():
    
    allocation_view = "asset"

    overview_bool= st.sidebar.button(f"**Overview**",type='primary')
    allocation_view = st.sidebar.radio("Alocation by", ["Asset", "Portfolio","Type", "Platform"],index=None)
    
    portfolios_latest_data = db.get_portfolio_latest_data()
 
    overview = {
        "portfolio": "Overview",
        "total_invested": portfolios_latest_data["total_invested"].sum(),
        "realised_profit": portfolios_latest_data["realised_profit"].sum(),
        "unrealised_profit": portfolios_latest_data["unrealised_profit"].sum(),
        "balance": portfolios_latest_data["balance"].sum()
    }
    portfolio_focus=overview

    st.sidebar.header(f"My Portfolios ({len(portfolios_latest_data['portfolio'])})")

    for _, portfolio in portfolios_latest_data.iterrows():
        if st.sidebar.button(f"**{portfolio['portfolio']}** *({portfolio['balance']:,.2f})*",type='tertiary'):
            portfolio_focus = portfolio
        
    PortfolioMetrics(portfolio_focus,allocation_view)
   
    st.sidebar.divider()

   
    if st.sidebar.button("+ Create Portfolio"):
        create_portfolio()

    if st.sidebar.button("Import Data"):
       import_data()
        

if __name__ == "__main__":
    menu()  