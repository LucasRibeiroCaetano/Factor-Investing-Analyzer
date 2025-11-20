"""
Configuration file for Factor Investing Analyzer.
Defines all constants, tickers, date ranges, and settings.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class Config:
    """Centralized configuration for the Factor Investing Analyzer."""
    
    # Project Paths
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    OUTPUT_DIR: Path = BASE_DIR / "output"
    
    # Factor ETF Tickers
    FACTOR_TICKERS: Dict[str, str] = {
        "Value": "VLUE",
        "Momentum": "MTUM",
        "Quality": "QUAL",
        "Low Volatility": "USMV"
    }
    
    # Geography ETF Tickers
    GEOGRAPHY_TICKERS: Dict[str, str] = {
        "US Market": "SPY",
        "Europe": "EXSA.DE",  # EUR-denominated, requires conversion
        "Emerging Markets": "EEM"
    }
    
    # Currency Conversion
    CURRENCY_PAIR: str = "EURUSD=X"
    EUR_TICKERS: List[str] = ["EXSA.DE"]  # Tickers that need EUR to USD conversion
    
    # Date Range for Analysis
    START_DATE: str = "2018-01-01"
    END_DATE: str = datetime.now().strftime("%Y-%m-%d")
    
    # Visualization Settings
    PLOT_THEME: str = "dark"  # matplotx github theme
    FIGURE_SIZE: tuple = (12, 8)
    DPI: int = 300
    SAVE_FORMAT: str = "png"
    
    # Analysis Settings
    RISK_FREE_RATE: float = 0.02  # Annual risk-free rate (2%)
    TRADING_DAYS_PER_YEAR: int = 252
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
