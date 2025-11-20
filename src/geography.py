"""
Geography Analysis Module.
Analyzes geographic exposure and regional performance metrics.
"""
from typing import Dict, Tuple
import pandas as pd
import numpy as np


class GeographyAnalyzer:
    """
    Analyzes geographic investment exposure.
    Processes regional ETF data and calculates comparative metrics.
    """
    
    def __init__(self, prices: pd.DataFrame, returns: pd.DataFrame):
        """
        Initialize the geography analyzer.
        
        Args:
            prices: DataFrame containing price data for geographic ETFs
            returns: DataFrame containing return data for geographic ETFs
        """
        self.prices: pd.DataFrame = prices
        self.returns: pd.DataFrame = returns
        
    def calculate_relative_performance(self) -> pd.DataFrame:
        """
        Calculate cumulative performance relative to a base of 100.
        
        Returns:
            DataFrame with normalized performance (base 100)
        """
        normalized = (self.prices / self.prices.iloc[0]) * 100
        return normalized
    
    def calculate_regional_correlations(self) -> pd.DataFrame:
        """
        Calculate correlation matrix between geographic regions.
        
        Returns:
            DataFrame with pairwise correlations
        """
        return self.returns.corr()
    
    def calculate_regional_contribution(self) -> pd.Series:
        """
        Calculate each region's contribution to overall portfolio.
        Based on final values, returns as percentages.
        
        Returns:
            Series with percentage allocations
        """
        final_values = self.prices.iloc[-1]
        total_value = final_values.sum()
        contributions = (final_values / total_value) * 100
        
        return contributions
    
    def get_best_worst_performers(self) -> Dict[str, str]:
        """
        Identify best and worst performing regions over the period.
        
        Returns:
            Dictionary with 'best' and 'worst' region names
        """
        total_returns = (self.prices.iloc[-1] / self.prices.iloc[0] - 1) * 100
        
        best_region = total_returns.idxmax()
        worst_region = total_returns.idxmin()
        
        return {
            'best': best_region,
            'best_return': total_returns[best_region],
            'worst': worst_region,
            'worst_return': total_returns[worst_region]
        }
    
    def calculate_regional_volatility(self, annualization_factor: int = 252) -> pd.Series:
        """
        Calculate annualized volatility for each region.
        
        Args:
            annualization_factor: Number of trading days per year
            
        Returns:
            Series with annualized volatilities
        """
        return self.returns.std() * np.sqrt(annualization_factor)
    
    def calculate_risk_adjusted_returns(
        self,
        risk_free_rate: float = 0.02,
        trading_days: int = 252
    ) -> pd.DataFrame:
        """
        Calculate risk-adjusted metrics for each region.
        
        Args:
            risk_free_rate: Annual risk-free rate
            trading_days: Number of trading days per year
            
        Returns:
            DataFrame with risk-adjusted metrics
        """
        # Calculate annualized returns
        n_years = len(self.returns) / trading_days
        total_return = (self.prices.iloc[-1] / self.prices.iloc[0]) - 1
        annualized_return = (1 + total_return) ** (1 / n_years) - 1
        
        # Calculate annualized volatility
        annualized_vol = self.returns.std() * np.sqrt(trading_days)
        
        # Calculate Sharpe ratio
        sharpe = (annualized_return - risk_free_rate) / annualized_vol
        
        risk_adjusted = pd.DataFrame({
            'Annualized Return': annualized_return,
            'Annualized Volatility': annualized_vol,
            'Sharpe Ratio': sharpe,
            'Return/Risk': annualized_return / annualized_vol
        })
        
        return risk_adjusted
    
    def analyze_drawdown_by_region(self) -> pd.DataFrame:
        """
        Calculate maximum drawdown for each geographic region.
        
        Returns:
            DataFrame with drawdown analysis
        """
        drawdowns = pd.DataFrame(index=self.prices.index)
        max_drawdowns = {}
        
        for region in self.prices.columns:
            # Calculate running maximum
            running_max = self.prices[region].expanding().max()
            
            # Calculate drawdown
            drawdown = (self.prices[region] - running_max) / running_max
            drawdowns[region] = drawdown
            
            # Store maximum drawdown
            max_drawdowns[region] = drawdown.min()
        
        return pd.Series(max_drawdowns, name='Max Drawdown')
    
    def get_geographic_summary(
        self,
        risk_free_rate: float = 0.02,
        trading_days: int = 252
    ) -> pd.DataFrame:
        """
        Generate comprehensive geographic performance summary.
        
        Args:
            risk_free_rate: Annual risk-free rate
            trading_days: Number of trading days per year
            
        Returns:
            DataFrame with all key geographic metrics
        """
        # Calculate metrics
        total_return = (self.prices.iloc[-1] / self.prices.iloc[0] - 1) * 100
        risk_adjusted = self.calculate_risk_adjusted_returns(risk_free_rate, trading_days)
        max_dd = self.analyze_drawdown_by_region()
        
        # Combine into summary
        summary = pd.DataFrame({
            'Total Return (%)': total_return,
            'Annualized Return (%)': risk_adjusted['Annualized Return'] * 100,
            'Annualized Volatility (%)': risk_adjusted['Annualized Volatility'] * 100,
            'Sharpe Ratio': risk_adjusted['Sharpe Ratio'],
            'Max Drawdown (%)': max_dd * 100
        })
        
        return summary
    
    def calculate_diversification_ratio(self) -> float:
        """
        Calculate portfolio diversification ratio.
        Higher values indicate better diversification.
        
        Returns:
            Diversification ratio (weighted avg volatility / portfolio volatility)
        """
        # Equal weight portfolio
        weights = np.array([1.0 / len(self.returns.columns)] * len(self.returns.columns))
        
        # Individual volatilities
        individual_vols = self.returns.std().values
        
        # Portfolio returns
        portfolio_returns = (self.returns * weights).sum(axis=1)
        portfolio_vol = portfolio_returns.std()
        
        # Weighted average of individual volatilities
        weighted_avg_vol = np.dot(weights, individual_vols)
        
        # Diversification ratio
        div_ratio = weighted_avg_vol / portfolio_vol
        
        return div_ratio
