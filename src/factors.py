"""
Factor Data Loader Module.
Handles data ingestion from Yahoo Finance with currency conversion and fallback mock data.
"""
import warnings
from typing import Dict, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    warnings.warn("yfinance not available. Will use mock data.")


class FactorDataLoader:
    """
    Loads and processes factor and geography ETF data.
    Handles EUR to USD conversion for European ETFs.
    Provides fallback mock data if yfinance fails.
    """
    
    def __init__(self, start_date: str, end_date: str, currency_pair: str = "EURUSD=X"):
        """
        Initialize the data loader.
        
        Args:
            start_date: Start date for data retrieval (DD/MM/YYYY)
            end_date: End date for data retrieval (DD/MM/YYYY)
            currency_pair: Currency pair ticker for conversion (default: EURUSD=X)
        """
        # Convert Portuguese date format (DD/MM/YYYY) to ISO format (YYYY-MM-DD) for yfinance
        self.start_date: str = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.end_date: str = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.currency_pair: str = currency_pair
        self.usd_eur_rate: Optional[pd.Series] = None
        
    def _fetch_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Fetch data from Yahoo Finance for a single ticker.
        
        Args:
            ticker: Stock/ETF ticker symbol
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        if not YFINANCE_AVAILABLE:
            return None
            
        try:
            data = yf.download(
                ticker,
                start=self.start_date,
                end=self.end_date,
                progress=False,
                auto_adjust=False  # Changed to False to get consistent column structure
            )
            
            if data.empty:
                warnings.warn(f"No data retrieved for {ticker}")
                return None
            
            # Handle multi-level columns from yfinance
            if isinstance(data.columns, pd.MultiIndex):
                # Drop the ticker level if present
                data.columns = data.columns.droplevel(1)
                
            return data
            
        except Exception as e:
            warnings.warn(f"Failed to fetch {ticker}: {str(e)}")
            return None
    
    def _load_currency_conversion(self) -> bool:
        """
        Load USD/EUR exchange rate for currency conversion.
        Inverts EUR/USD rate to get USD/EUR.
        
        Returns:
            True if successful, False otherwise
        """
        currency_data = self._fetch_data(self.currency_pair)
        
        if currency_data is not None and 'Close' in currency_data.columns:
            # Invert EUR/USD to get USD/EUR rate
            self.usd_eur_rate = 1.0 / currency_data['Close']
            return True
        else:
            # Fallback: use constant conversion rate (1 USD = 0.91 EUR)
            warnings.warn(f"Failed to load {self.currency_pair}, using constant rate 0.91")
            return False
    
    def _convert_usd_to_eur(self, usd_prices: pd.Series, ticker: str) -> pd.Series:
        """
        Convert USD-denominated prices to EUR.
        
        Args:
            usd_prices: Price series in USD
            ticker: Ticker symbol for logging
            
        Returns:
            Price series converted to EUR
        """
        if self.usd_eur_rate is not None:
            # Align dates and forward-fill missing rates
            aligned_rate = self.usd_eur_rate.reindex(usd_prices.index, method='ffill')
            return usd_prices * aligned_rate
        else:
            # Use constant conversion rate as fallback (1 USD = 0.91 EUR)
            return usd_prices * 0.91
    
    def load_tickers(self, tickers_dict: Dict[str, str], usd_tickers: List[str]) -> pd.DataFrame:
        """Load and process ticker data with currency conversion to EUR base."""
        # Load currency conversion rate first
        self._load_currency_conversion()
        
        price_data = {}
        
        for name, ticker in tickers_dict.items():
            try:
                # Fetch data
                data = self._fetch_data(ticker)
                
                if data is None or data.empty:
                    print(f"Warning: No data for {name} ({ticker}), using mock data")
                    price_data[name] = self._generate_mock_data(name)
                    continue
                
                # Get adjusted close prices
                if 'Adj Close' in data.columns:
                    prices = data['Adj Close']
                elif 'Close' in data.columns:
                    prices = data['Close']
                else:
                    print(f"Warning: No price column found for {name} ({ticker}), using mock data")
                    price_data[name] = self._generate_mock_data(name)
                    continue
                
                # Ensure we have a Series, not a DataFrame
                if isinstance(prices, pd.DataFrame):
                    if prices.shape[1] == 1:
                        prices = prices.iloc[:, 0]
                    else:
                        print(f"Warning: Multiple columns found for {name} ({ticker}), using first column")
                        prices = prices.iloc[:, 0]
                
                # Ensure the Series has a name
                prices.name = name
                
                # Convert USD tickers to EUR
                if ticker in usd_tickers:
                    prices = self._convert_usd_to_eur(prices, ticker)
                    prices.name = name  # Restore name after conversion
                
                price_data[name] = prices
                
            except Exception as e:
                print(f"Warning: Failed to load {name} ({ticker}): {str(e)}")
                print(f"Using mock data for {name}")
                price_data[name] = self._generate_mock_data(name)
                continue
        
        if not price_data:
            raise ValueError("No ticker data was successfully loaded")
        
        # Create DataFrame and handle any alignment issues
        df = pd.DataFrame(price_data)
        df = df.dropna(how='all')  # Remove rows where all values are NaN
        
        return df
    
    def _generate_mock_data(self, name: str) -> pd.Series:
        """
        Generate realistic mock price data for fallback scenarios.
        Uses geometric Brownian motion to simulate realistic returns.
        
        Args:
            name: Name of the asset (for seeding randomness)
            
        Returns:
            Series with simulated price data
        """
        # Parse dates (already in ISO format internally)
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        
        # Generate date range (business days)
        date_range = pd.bdate_range(start=start, end=end)
        n_days = len(date_range)
        
        # Set seed based on name for reproducibility
        np.random.seed(hash(name) % (2**32))
        
        # Geometric Brownian Motion parameters
        initial_price = 100.0
        drift = 0.0002  # Daily drift (~5% annual)
        volatility = 0.01  # Daily volatility (~16% annual)
        
        # Generate returns
        returns = np.random.normal(drift, volatility, n_days)
        
        # Calculate prices
        price_series = initial_price * np.exp(np.cumsum(returns))
        
        return pd.Series(price_series, index=date_range, name=name)
    
    def get_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily returns from price data.
        
        Args:
            prices: DataFrame with price data
            
        Returns:
            DataFrame with daily returns
        """
        return prices.pct_change().dropna()
