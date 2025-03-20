# Portfolio Tracker

A powerful portfolio management application that helps you track your investments across multiple platforms and assets. Built with Python, Streamlit, and SQLite.

## Features

- 📊 **Multi-Platform Support**: Import data from various cryptocurrency exchanges and platforms
- 💰 **Real-time Price Tracking**: Get current prices for your assets
- 📈 **Portfolio Analytics**: 
  - Performance charts
  - Asset allocation visualization
  - Realized and unrealized profit tracking
  - Transaction history
- 🔄 **Data Import**: Support for CSV file imports from supported platforms
- 📱 **Modern UI**: Clean and intuitive interface built with Streamlit
- 💾 **Local Database**: SQLite database for secure data storage

## Screenshots

### Main Dashboard
![Main Dashboard](docs/screenshots/dashboard.png)
*Overview of your portfolio with key metrics and performance charts*

### Asset Allocation
![Asset Allocation](docs/screenshots/allocation.png)
*Visual representation of your portfolio's asset distribution*

### Transaction History
![Transaction History](docs/screenshots/transactions.png)
*Detailed view of all your transactions*

### Data Import
![Data Import](docs/screenshots/import.png)
*Easy-to-use interface for importing transaction data*

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PortfolioTracker.git
cd PortfolioTracker
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

1. Make sure your virtual environment is activated:
```bash
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

2. Start the application:
```bash
# On Windows
.venv\Scripts\python.exe backend/main.py
# On Unix or MacOS
python backend/main.py
```

3. The application will:
   - Process any data files in the `data` directory
   - Initialize the database if needed
   - Launch the Streamlit interface in your default browser

### Data Import

1. Place your CSV files in the appropriate platform folder under the `data` directory:
```
data/
  ├── binance/
  │   └── your_transactions.csv
  └── other_platform/
      └── your_transactions.csv
```

2. Use the "Import Data" button in the UI to import new transactions

### Supported Platforms

Currently supports importing data from:
- Binance (export trades orders)

## Project Structure

```
PortfolioTracker/
├── backend/
│   ├── data_processing.py    # Data processing and normalization
│   ├── data_persistence.py   # Database operations
│   ├── database.py          # Database queries
│   └── main.py              # Application entry point
├── frontend/
│   └── app.py               # Streamlit UI
├── modules/
│   └── platform_specific/   # Platform-specific data processors
├── utils/
│   ├── logger.py           # Logging configuration
└── data/                   # Data directory for CSV files
```

## Development

### Adding New Platform Support

1. Create a new module in the `modules` directory
2. Implement the required functions:
   - `clean_data(df)`: Clean and normalize platform-specific data

### Database Schema

The application uses SQLite with the following main tables:
- `transactions`: Transaction history
- `assets`: Asset information
- `portfolios`: Portfolio details
- `current_prices`: Latest asset prices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Data visualization powered by [Plotly](https://plotly.com/)
- Price data from [cryptoprices.cc](https://cryptoprices.cc/)