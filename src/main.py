"""
Main Entry Point for Factor Investing Analyzer.
Orchestrates the complete analysis pipeline.
"""
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from src.factors import FactorDataLoader
from src.analysis import PerformanceAnalyzer
from src.geography import GeographyAnalyzer
from src.visualizer import Visualizer


class FactorInvestingAnalyzer:
    """
    Main orchestrator for factor investing analysis.
    Coordinates data loading, analysis, and visualization.
    """
    
    def __init__(self, start_date: str = None, end_date: str = None):
        """Initialize the analyzer with configuration settings.
        
        Args:
            start_date: Optional start date (DD/MM/YYYY). Defaults to 01/01/2000.
            end_date: Optional end date (DD/MM/YYYY). Defaults to today.
        """
        self.config = Config()
        self.config.ensure_directories()
        
        # Override dates if provided
        if start_date:
            self.config.START_DATE = start_date
        if end_date:
            self.config.END_DATE = end_date
        
        # Initialize components
        self.data_loader = FactorDataLoader(
            start_date=self.config.START_DATE,
            end_date=self.config.END_DATE,
            currency_pair=self.config.CURRENCY_PAIR
        )
        
        self.visualizer = Visualizer(
            output_dir=self.config.OUTPUT_DIR,
            theme=self.config.PLOT_THEME,
            figsize=self.config.FIGURE_SIZE,
            dpi=self.config.DPI
        )
        
        # Data containers
        self.factor_prices = None
        self.factor_returns = None
        self.geography_prices = None
        self.geography_returns = None
        
    def load_data(self) -> None:
        """Load all factor and geography data."""
        print("=" * 70)
        print("LOADING DATA")
        print("=" * 70)
        
        # Load factor data
        print("\nLoading Factor ETF data...")
        self.factor_prices = self.data_loader.load_tickers(
            tickers_dict=self.config.FACTOR_TICKERS,
            usd_tickers=self.config.USD_TICKERS
        )
        self.factor_returns = self.data_loader.get_returns(self.factor_prices)
        print(f"Factor data loaded: {len(self.factor_prices)} days, {len(self.factor_prices.columns)} factors")
        
        # Load geography data
        print("\nLoading Geography ETF data...")
        self.geography_prices = self.data_loader.load_tickers(
            tickers_dict=self.config.GEOGRAPHY_TICKERS,
            usd_tickers=self.config.USD_TICKERS
        )
        self.geography_returns = self.data_loader.get_returns(self.geography_prices)
        print(f"Geography data loaded: {len(self.geography_prices)} days, {len(self.geography_prices.columns)} regions")
        
    def analyze_factors(self) -> None:
        """Perform comprehensive factor analysis."""
        print("\n" + "=" * 70)
        print("FACTOR ANALYSIS")
        print("=" * 70)
        
        # Initialize analyzer
        factor_analyzer = PerformanceAnalyzer(self.factor_returns)
        
        # Calculate metrics
        print("\nCalculating performance metrics...")
        performance_summary = factor_analyzer.get_performance_summary(
            risk_free_rate=self.config.RISK_FREE_RATE,
            trading_days=self.config.TRADING_DAYS_PER_YEAR
        )
        
        print("\n--- Factor Performance Summary ---")
        print(performance_summary.to_string())
        
        # Calculate cumulative returns
        cumulative_returns = factor_analyzer.calculate_cumulative_returns()
        
        # Calculate drawdowns
        drawdowns = factor_analyzer.calculate_drawdowns()
        
        # Calculate correlations
        correlation_matrix = factor_analyzer.calculate_correlation_matrix()
        
        print("\n--- Factor Correlation Matrix ---")
        print(correlation_matrix.to_string())
        
        # Generate visualizations
        print("\nGenerating factor visualizations...")
        
        self.visualizer.plot_cumulative_returns(
            cumulative_returns,
            title="Factor Performance - Cumulative Returns",
            filename="factor_cumulative_returns.png"
        )
        
        self.visualizer.plot_drawdowns(
            drawdowns,
            title="Factor Drawdown Analysis",
            filename="factor_drawdowns.png"
        )
        
        self.visualizer.plot_correlation_matrix(
            correlation_matrix,
            title="Factor Correlation Matrix",
            filename="factor_correlation_matrix.png"
        )
        
        self.visualizer.plot_performance_summary(
            performance_summary,
            title="Factor Performance Metrics",
            filename="factor_performance_summary.png"
        )
        
        # Plot Sharpe ratios comparison
        sharpe_ratios = performance_summary['Sharpe Ratio']
        self.visualizer.plot_comparison_bars(
            sharpe_ratios,
            title="Factor Sharpe Ratios Comparison",
            ylabel="Sharpe Ratio",
            filename="factor_sharpe_comparison.png"
        )
        
    def analyze_geography(self) -> None:
        """Perform comprehensive geographic analysis."""
        print("\n" + "=" * 70)
        print("GEOGRAPHIC ANALYSIS")
        print("=" * 70)
        
        # Initialize analyzer
        geo_analyzer = GeographyAnalyzer(self.geography_prices, self.geography_returns)
        
        # Calculate metrics
        print("\nCalculating geographic metrics...")
        geographic_summary = geo_analyzer.get_geographic_summary(
            risk_free_rate=self.config.RISK_FREE_RATE,
            trading_days=self.config.TRADING_DAYS_PER_YEAR
        )
        
        print("\n--- Geographic Performance Summary ---")
        print(geographic_summary.to_string())
        
        # Get best/worst performers
        performers = geo_analyzer.get_best_worst_performers()
        print(f"\nBest Performer: {performers['best']} (+{performers['best_return']:.2f}%)")
        print(f"Worst Performer: {performers['worst']} ({performers['worst_return']:.2f}%)")
        
        # Calculate regional correlations
        regional_correlations = geo_analyzer.calculate_regional_correlations()
        print("\n--- Regional Correlation Matrix ---")
        print(regional_correlations.to_string())
        
        # Calculate diversification ratio
        div_ratio = geo_analyzer.calculate_diversification_ratio()
        print(f"\nDiversification Ratio: {div_ratio:.2f}")
        print("(Higher values indicate better diversification benefits)")
        
        # Generate visualizations
        print("\nGenerating geographic visualizations...")
        
        # Cumulative performance
        relative_performance = geo_analyzer.calculate_relative_performance()
        self.visualizer.plot_cumulative_returns(
            (relative_performance / 100) - 1,  # Convert back to returns format
            title="Geographic Performance - Normalized (Base 100)",
            filename="geography_performance.png"
        )
        
        # Regional allocation pie chart
        regional_contribution = geo_analyzer.calculate_regional_contribution()
        self.visualizer.plot_pie_chart(
            regional_contribution,
            title="Regional Allocation",
            filename="geography_allocation_pie.png"
        )
        
        # Correlation matrix
        self.visualizer.plot_correlation_matrix(
            regional_correlations,
            title="Regional Correlation Matrix",
            filename="geography_correlation_matrix.png"
        )
        
        # Sharpe ratio comparison
        sharpe_ratios = geographic_summary['Sharpe Ratio']
        self.visualizer.plot_comparison_bars(
            sharpe_ratios,
            title="Regional Sharpe Ratios",
            ylabel="Sharpe Ratio",
            filename="geography_sharpe_comparison.png"
        )
        
    def run(self) -> None:
        """Execute the complete analysis pipeline."""
        try:
            print("\n" + "=" * 70)
            print("FACTOR INVESTING ANALYZER")
            print("=" * 70)
            print(f"Analysis Period: {self.config.START_DATE} to {self.config.END_DATE}")
            print(f"Risk-Free Rate: {self.config.RISK_FREE_RATE * 100:.1f}%")
            print("=" * 70)
            
            # Step 1: Load data
            self.load_data()
            
            # Step 2: Analyze factors
            self.analyze_factors()
            
            # Step 3: Analyze geography
            self.analyze_geography()
            
            # Completion message
            print("\n" + "=" * 70)
            print("ANALYSIS COMPLETE")
            print("=" * 70)
            print(f"\nAll outputs saved to: {self.config.OUTPUT_DIR}")
            print("\nGenerated Files:")
            print("  - Factor cumulative returns chart")
            print("  - Factor drawdown analysis")
            print("  - Factor correlation matrix")
            print("  - Factor performance summary")
            print("  - Factor Sharpe ratio comparison")
            print("  - Geographic performance chart")
            print("  - Geographic allocation pie chart")
            print("  - Geographic correlation matrix")
            print("  - Geographic Sharpe ratio comparison")
            print("\n" + "=" * 70)
            
        except Exception as e:
            print(f"\nERROR: Analysis failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Factor Investing Analyzer - Comprehensive factor and geographic ETF analysis tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py
  python src/main.py --start-date 01/01/2015
  python src/main.py --start-date 01/01/2010 --end-date 31/12/2020
  python src/main.py -s 15/06/2018 -e 15/06/2023

Note: All returns are calculated in EUR (base currency).
      Date format: DD/MM/YYYY (Portuguese format)
        """
    )
    
    parser.add_argument(
        '-s', '--start-date',
        type=str,
        default=None,
        metavar='DD/MM/YYYY',
        help='Start date for analysis (default: 01/01/2000)'
    )
    
    parser.add_argument(
        '-e', '--end-date',
        type=str,
        default=None,
        metavar='DD/MM/YYYY',
        help='End date for analysis (default: today)'
    )
    
    return parser.parse_args()


def validate_date(date_string: str, param_name: str) -> bool:
    """Validate date format.
    
    Args:
        date_string: Date string to validate
        param_name: Parameter name for error messages
        
    Returns:
        True if valid, exits program if invalid
    """
    try:
        datetime.strptime(date_string, "%d/%m/%Y")
        return True
    except ValueError:
        print(f"ERROR: Invalid {param_name} format. Please use DD/MM/YYYY format.")
        print(f"Example: 15/01/2020")
        sys.exit(1)


def main():
    """Main entry point with argument parsing."""
    args = parse_arguments()
    
    # Validate dates if provided
    if args.start_date:
        validate_date(args.start_date, "start date")
    if args.end_date:
        validate_date(args.end_date, "end date")
    
    # Validate date order if both provided
    if args.start_date and args.end_date:
        start = datetime.strptime(args.start_date, "%d/%m/%Y")
        end = datetime.strptime(args.end_date, "%d/%m/%Y")
        if start >= end:
            print("ERROR: Start date must be before end date.")
            sys.exit(1)
    
    # Create and run analyzer with provided dates
    analyzer = FactorInvestingAnalyzer(
        start_date=args.start_date,
        end_date=args.end_date
    )
    analyzer.run()


if __name__ == "__main__":
    main()
