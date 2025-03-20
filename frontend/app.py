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

def portfolio_metrics(portfolio):
    st.subheader(portfolio['Portfolio'])
    balance,total_invested,realised_profit,unrealised_profit = st.columns(4) 
    with balance:
        st.metric("Balance", f"${portfolio['Balance']:,.2f}")
    with total_invested:
        st.metric("Total Invested", f"${portfolio['Total_Invested']:,.2f}")
    with realised_profit:
        st.metric("Realised Profit", f"${portfolio['Realised_Profit']:,.2f}")
    with unrealised_profit:
        st.metric("Unrealised Profit", f"${portfolio['Unrealised_Profit']:,.2f}")

def performance_chart(portfolio_name):
    if portfolio_name == "Overview":
        df = db.get_portfolio_history_overview()
        df = df.rename(columns={'total_balance': 'Balance'})
    else:
        df = db.get_portfolio_history(portfolio_name)

    if df is not None:
        fig_history = px.area(
            df,
            x='Date',
            y='Balance',
            title='Performance History',
            labels={'Date': 'Date', 'Balance': 'Balance'},
            markers=True,
            template='plotly_white'
        )       
        fig_history.update_layout(hovermode="x unified")
        st.subheader("Performance History")
        st.line_chart(df,x='Date',y='Balance',x_label='Date',y_label='Balance')
    else:
        st.subheader("Performance History")
        st.line_chart(pd.DataFrame({'Date': ['No Data'], 'Balance': [0]}), x='Date', y='Balance', x_label='Date', y_label='Balance')

def allocation_chart(portfolio_name,allocation_view):
    st.subheader("Allocation")
    if portfolio_name == "Overview":
        if allocation_view == "Asset":
            holdings = db.get_all_assets()
           
            holdings = holdings[['Asset', 'Balance']].sort_values('Balance', ascending=False)
            total_balance = holdings['Balance'].sum()
            holdings['Allocation'] = holdings.apply(lambda row: ((row['Balance']) / total_balance) * 100, axis=1)
            holdings['Allocation'] = holdings['Allocation'].round(2)

            fig_allocation = px.pie(holdings, values='Allocation', names=f"{allocation_view}")
            st.plotly_chart(fig_allocation)
        else:
            if allocation_view == "Portfolio":
                holdings = db.get_portfolio_latest_data()
                holdings = holdings[['Portfolio', 'Balance']].sort_values('Balance', ascending=False)
                total_balance = holdings['Balance'].sum()
                holdings['Allocation'] = holdings.apply(lambda row: ((row['Balance']) / total_balance) * 100, axis=1)
                holdings['Allocation'] = holdings['Allocation'].round(2)
                fig_allocation = px.pie(holdings, values='Allocation', names=f"{allocation_view}")
                st.plotly_chart(fig_allocation)

            if allocation_view == "Type":
                holdings = db.get_allocation_by_type()
            if allocation_view == "Platform":
                holdings = db.get_allocation_by_platform()
    else:
        allocation_view = "Asset"
        holdings = db.get_assets_by_portfolio(portfolio_name)
        holdings = holdings[['Asset', 'Balance']].sort_values('Balance', ascending=False)


        total_balance = holdings['Balance'].sum()
        holdings['Allocation'] = holdings.apply(lambda row: ((row['Balance']) / total_balance) * 100, axis=1)
        holdings['Allocation'] = holdings['Allocation'].round(2)

        fig_allocation = px.pie(holdings, values='Allocation', names=f"{allocation_view}")
        
    #    fig_allocation = px.pie(pd.DataFrame({f"{allocation_view.capitalize()}": ['No Data'], 'Allocation': [0]}), values='Allocation', names=f"{allocation_view.capitalize()}")
    
        st.plotly_chart(fig_allocation)
   

def PortfolioMetrics(portfolio,allocation_view):
    st.session_state.selected_portfolio = portfolio['Portfolio']
    portfolio_metrics(portfolio)

    chart_tab, transaction_tab = st.tabs(["Charts", "Transactions"])

    with chart_tab:

        performance,allocation= st.columns(2)

        with performance:
            performance_chart(portfolio['Portfolio'])
        with allocation:
            allocation_chart(portfolio['Portfolio'],allocation_view)

        if portfolio['Portfolio'] == "Overview":
            df_asset_metrics = db.get_all_assets()
        else:
            df_asset_metrics = db.get_assets_by_portfolio(portfolio['Portfolio'])
        
        if df_asset_metrics is not None:
            st.subheader(f"Holdings ({len(df_asset_metrics)})")
        else:
            st.subheader(f"Holdings (0)")
        st.dataframe(df_asset_metrics,hide_index=True)

    with transaction_tab:
        
        if st.session_state.selected_portfolio == "Overview":
            transactions = db.get_all_transactions()
        else:
            transactions = db.get_transactions_by_portfolio(portfolio['Portfolio'])
        
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
    uploaded_file = st.file_uploader(
        "Upload your transaction data",
        type=["csv", "xlsx"],
        accept_multiple_files=False,
        help="Upload a CSV or Excel file containing your transaction data"
    )

    col1,col2=st.columns(2)
    with col1:
        if st.button("Import", type="primary", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                temp_file.write(uploaded_file.getbuffer())  
                temp_filepath = temp_file.name  
            imported_data = dp.load_platform_file(temp_filepath, selected_module)
            unique_assets = imported_data['Asset'].unique()
            asset_prices = {asset: main.asset_current_price(asset) for asset in unique_assets}
            dper.save_to_db(imported_data,portfolio=selectPortfolio,asset_prices=asset_prices)
            st.rerun()
    with col2:
        if st.button("Cancel", type="secondary", use_container_width=True):
            st.rerun()

def menu():
    
    #allocation_view = "asset"

    overview_bool= st.sidebar.button(f"**Overview**",type='primary')
    allocation_view = st.sidebar.radio("Alocation by", ["Asset", "Portfolio","Type", "Platform"],index=0)
    
    portfolios_latest_data = db.get_portfolio_latest_data()
    overview = {
        "Portfolio": "Overview",
        "Total_Invested": portfolios_latest_data["Total_Invested"].sum(),
        "Realised_Profit": portfolios_latest_data["Realised_Profit"].sum(),
        "Unrealised_Profit": portfolios_latest_data["Unrealised_Profit"].sum(),
        "Balance": portfolios_latest_data["Balance"].sum()
    }
    portfolio_focus=overview

    st.sidebar.header(f"My Portfolios ({len(portfolios_latest_data['Portfolio'])})")

    for _, portfolio in portfolios_latest_data.iterrows():
        if st.sidebar.button(f"**{portfolio['Portfolio']}** *({portfolio['Balance']:,.2f})*",type='tertiary'):
            portfolio_focus = portfolio
        
    PortfolioMetrics(portfolio_focus,allocation_view)
   
    st.sidebar.divider()

   
    if st.sidebar.button("+ Create Portfolio"):
        create_portfolio()

    if st.sidebar.button("Import Data"):
       import_data()
        

# def load_settings():
#     if os.path.exists(SETTINGS_PATH):
#         with open(SETTINGS_PATH, "r") as f:
#             return json.load(f)
#     return {"DEFAULT_PORTFOLIO": "", "DEFAULT_DATA_SOURCE": ""}

# # Function to save settings
# def save_settings(setting,value):
#     try:
#         # Load existing settings
#         with open(SETTINGS_PATH, "r") as f:
#             settings = json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         # If file doesn't exist or is empty/corrupt, start with an empty dict
#         settings = {}

#     # Update the setting
#     settings[setting] = value  

#     # Save updated settings
#     with open(SETTINGS_PATH, "w") as f:
#         json.dump(settings, f, indent=4)

# def settings():
#     settings = load_settings()

#     check_settings = st.sidebar.button("⚙️ Settings", type='tertiary')

#     if check_settings:
#         default_data_filepath = st.sidebar.text_input(
#             "Default Data Source",
#             value=settings.get("DEFAULT_DATA_FILEPATH", ""),
#             key="DEFAULT_DATA_FILEPATH",
#             on_change=lambda: save_settings("DEFAULT_DATA_FILEPATH", st.session_state["DEFAULT_DATA_FILEPATH"])
#         )

#         default_portfolio_name = st.sidebar.text_input(
#             "Default Project Name",
#             value=settings.get("DEFAULT_PORTFOLIO_NAME", ""),
#             key="DEFAULT_PORTFOLIO_NAME",
#             on_change=lambda: save_settings("DEFAULT_PORTFOLIO_NAME", st.session_state["DEFAULT_PORTFOLIO_NAME"])
#         )

if __name__ == "__main__":
    menu()  