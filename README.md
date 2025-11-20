# Factor Investing Analyzer

A production-grade Python application for analyzing factor-based and geographic investment strategies. This tool provides comprehensive performance analysis, risk metrics, and professional visualizations using real market data.

## Features

- **Factor Analysis**: Evaluate classic investment factors including Value (VLUE), Momentum (MTUM), Quality (QUAL), and Low Volatility (USMV)
- **Geographic Analysis**: Compare performance across US (SPY), European (EXSA.DE), and Emerging Markets (EEM)
- **Currency Conversion**: Automatic EUR to USD conversion for European ETFs using live exchange rates
- **Performance Metrics**: Cumulative returns, drawdowns, Sharpe ratios, Sortino ratios, and correlation analysis
- **Professional Visualizations**: Dark-themed charts using matplotlib with matplotx styling
- **Robust Data Handling**: Fallback to realistic mock data if market data unavailable

## Project Structure

```
factor-investing-analyzer/
├── data/                  # Data storage directory
├── output/                # Generated charts and reports
├── src/
│   ├── __init__.py       # Package initialization
│   ├── main.py           # Main orchestrator
│   ├── factors.py        # Data loading with currency conversion
│   ├── analysis.py       # Performance metrics calculation
│   ├── geography.py      # Geographic analysis
│   └── visualizer.py     # Chart generation
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the complete analysis pipeline:

```bash
python src/main.py
```

The analyzer will:
1. Download historical price data from Yahoo Finance
2. Convert EUR-denominated ETFs to USD
3. Calculate comprehensive performance metrics
4. Generate professional visualizations
5. Save all outputs to the `output/` directory

## Configuration

Edit `config.py` to customize:

- **Tickers**: Modify `FACTOR_TICKERS` and `GEOGRAPHY_TICKERS` dictionaries
- **Date Range**: Adjust `START_DATE` and `END_DATE`
- **Analysis Parameters**: Change `RISK_FREE_RATE` or `TRADING_DAYS_PER_YEAR`
- **Visualization Settings**: Customize `FIGURE_SIZE`, `DPI`, and theme

## Output Files

The analyzer generates the following visualizations in the `output/` directory:

### Factor Analysis
- `factor_cumulative_returns.png` - Cumulative performance over time
- `factor_drawdowns.png` - Drawdown analysis
- `factor_correlation_matrix.png` - Factor correlation heatmap
- `factor_performance_summary.png` - Key metrics comparison
- `factor_sharpe_comparison.png` - Sharpe ratio ranking

### Geographic Analysis
- `geography_performance.png` - Regional performance comparison
- `geography_allocation_pie.png` - Regional allocation breakdown
- `geography_correlation_matrix.png` - Regional correlation heatmap
- `geography_sharpe_comparison.png` - Regional Sharpe ratio ranking

## Key Metrics Calculated

- **Total Return**: Overall percentage gain/loss
- **Annualized Return**: Compound annual growth rate (CAGR)
- **Annualized Volatility**: Standard deviation of returns
- **Sharpe Ratio**: Risk-adjusted return metric
- **Sortino Ratio**: Downside risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Correlation Matrix**: Pairwise correlations between assets

## Technical Details

### Object-Oriented Design

The project follows strict OOP principles with clearly separated concerns:

- `FactorDataLoader`: Handles data ingestion, currency conversion, and mock data generation
- `PerformanceAnalyzer`: Calculates all performance and risk metrics
- `GeographyAnalyzer`: Specialized geographic exposure analysis
- `Visualizer`: Creates and saves all charts with consistent styling
- `FactorInvestingAnalyzer`: Main orchestrator coordinating the pipeline

### Currency Conversion

European ETFs (EXSA.DE) are automatically converted from EUR to USD using the EURUSD=X exchange rate. This ensures accurate comparison with USD-denominated assets. If exchange rate data is unavailable, a fallback rate of 1.10 is applied.

### Data Resilience

If yfinance fails to retrieve data (network issues, API changes, etc.), the system automatically generates realistic mock data using geometric Brownian motion. This ensures the analysis pipeline always completes successfully.

## Dependencies

- **yfinance**: Market data retrieval
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **matplotlib**: Chart generation
- **matplotx**: Professional chart themes

## Professional Use

This codebase is designed to be portfolio-ready:

- Type hints throughout for clarity and IDE support
- Comprehensive docstrings for all classes and methods
- PEP 8 compliant code formatting
- Modular design for easy extension and testing
- Production-grade error handling
- Professional documentation

## License

This project is provided as-is for educational and professional portfolio purposes.

## Author

Lucas Caetano

---

**Note**: This analyzer uses real market data. Past performance does not guarantee future results. This tool is for analysis and educational purposes only, not investment advice.
