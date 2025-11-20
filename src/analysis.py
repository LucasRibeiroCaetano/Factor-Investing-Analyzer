"""
Performance Analysis Module.
Calculates key performance metrics including returns, drawdowns, and correlations.
"""
from typing import Dict, Tuple
import pandas as pd
import numpy as np


class PerformanceAnalyzer:
    """
    Analyzes investment performance metrics.
    Calculates cumulative returns, maximum drawdowns, and correlation matrices.
    """
    
    def __init__(self, returns: pd.DataFrame):
        """
        Initialize the performance analyzer.
        
        Args:
            returns: DataFrame containing daily returns for each asset
        """
        self.returns: pd.DataFrame = returns
        self.prices: pd.DataFrame = self._returns_to_prices(returns)
        
    @staticmethod
    def _returns_to_prices(returns: pd.DataFrame, initial_value: float = 100.0) -> pd.DataFrame:
        """
        Convert returns to normalized price series.
        
        Args:
            returns: DataFrame with daily returns
            initial_value: Starting value for price normalization
            
        Returns:
            DataFrame with normalized prices
        """
        return initial_value * (1 + returns).cumprod()
    
    def calculate_cumulative_returns(self) -> pd.DataFrame:
        """
        Calculate cumulative returns for all assets.
        
        Returns:
            DataFrame with cumulative returns (as decimals, not percentages)
        """
        cumulative_returns = (1 + self.returns).cumprod() - 1
        return cumulative_returns
    
    def calculate_drawdowns(self) -> pd.DataFrame:
        """
        Calculate drawdown series for all assets.
        Drawdown = (Current Price - Peak Price) / Peak Price
        
        Returns:
            DataFrame with drawdown values (negative percentages)
        """
        drawdowns = pd.DataFrame(index=self.prices.index)
        
        for column in self.prices.columns:
            # Calculate running maximum (peak)
            running_max = self.prices[column].expanding().max()
            
            # Calculate drawdown
            drawdown = (self.prices[column] - running_max) / running_max
            drawdowns[column] = drawdown
            
        return drawdowns
    
    def calculate_max_drawdown(self) -> pd.Series:
        """
        Calculate maximum drawdown for each asset.
        
        Returns:
            Series with maximum drawdown values
        """
        drawdowns = self.calculate_drawdowns()
        return drawdowns.min()
    
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation matrix of returns.
        
        Returns:
            DataFrame containing pairwise correlations
        """
        return self.returns.corr()
    
    def calculate_annualized_return(self, trading_days: int = 252) -> pd.Series:
        """
        Calculate annualized return for each asset.
        
        Args:
            trading_days: Number of trading days per year
            
        Returns:
            Series with annualized returns
        """
        total_days = len(self.returns)
        total_return = (1 + self.returns).prod() - 1
        years = total_days / trading_days
        
        annualized = (1 + total_return) ** (1 / years) - 1
        return annualized
    
    def calculate_annualized_volatility(self, trading_days: int = 252) -> pd.Series:
        """
        Calculate annualized volatility (standard deviation) for each asset.
        
        Args:
            trading_days: Number of trading days per year
            
        Returns:
            Series with annualized volatilities
        """
        return self.returns.std() * np.sqrt(trading_days)
    
    def calculate_sharpe_ratio(
        self,
        risk_free_rate: float = 0.02,
        trading_days: int = 252
    ) -> pd.Series:
        """
        Calculate Sharpe ratio for each asset.
        Sharpe = (Annualized Return - Risk Free Rate) / Annualized Volatility
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
            trading_days: Number of trading days per year
            
        Returns:
            Series with Sharpe ratios
        """
        ann_return = self.calculate_annualized_return(trading_days)
        ann_vol = self.calculate_annualized_volatility(trading_days)
        
        sharpe = (ann_return - risk_free_rate) / ann_vol
        return sharpe
    
    def calculate_sortino_ratio(
        self,
        risk_free_rate: float = 0.02,
        trading_days: int = 252
    ) -> pd.Series:
        """
        Calculate Sortino ratio for each asset.
        Only considers downside volatility (negative returns).
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
            trading_days: Number of trading days per year
            
        Returns:
            Series with Sortino ratios
        """
        ann_return = self.calculate_annualized_return(trading_days)
        
        # Calculate downside deviation (only negative returns)
        downside_returns = self.returns[self.returns < 0]
        downside_std = downside_returns.std()
        downside_vol = downside_std * np.sqrt(trading_days)
        
        sortino = (ann_return - risk_free_rate) / downside_vol
        return sortino
    
    def get_performance_summary(
        self,
        risk_free_rate: float = 0.02,
        trading_days: int = 252
    ) -> pd.DataFrame:
        """
        Generate comprehensive performance summary for all assets.
        
        Args:
            risk_free_rate: Annual risk-free rate
            trading_days: Number of trading days per year
            
        Returns:
            DataFrame with all key performance metrics
        """
        summary = pd.DataFrame({
            'Total Return': self.calculate_cumulative_returns().iloc[-1],
            'Annualized Return': self.calculate_annualized_return(trading_days),
            'Annualized Volatility': self.calculate_annualized_volatility(trading_days),
            'Sharpe Ratio': self.calculate_sharpe_ratio(risk_free_rate, trading_days),
            'Sortino Ratio': self.calculate_sortino_ratio(risk_free_rate, trading_days),
            'Max Drawdown': self.calculate_max_drawdown()
        })
        
        return summary
    
    def get_rolling_metrics(
        self,
        window: int = 252,
        metric: str = 'volatility'
    ) -> pd.DataFrame:
        """
        Calculate rolling window metrics.
        
        Args:
            window: Rolling window size in days
            metric: Metric to calculate ('volatility', 'sharpe', 'return')
            
        Returns:
            DataFrame with rolling metric values
        """
        if metric == 'volatility':
            return self.returns.rolling(window=window).std() * np.sqrt(252)
        elif metric == 'return':
            return self.returns.rolling(window=window).mean() * 252
        elif metric == 'sharpe':
            rolling_return = self.returns.rolling(window=window).mean() * 252
            rolling_vol = self.returns.rolling(window=window).std() * np.sqrt(252)
            return rolling_return / rolling_vol
        else:
            raise ValueError(f"Unknown metric: {metric}")
