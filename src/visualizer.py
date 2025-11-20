"""
Visualization Module.
Creates professional charts using matplotlib with matplotx github dark theme.
"""
from pathlib import Path
from typing import Optional, List, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    import matplotx
    MATPLOTX_AVAILABLE = True
except ImportError:
    MATPLOTX_AVAILABLE = False
    print("Warning: matplotx not available. Using default matplotlib style.")


class Visualizer:
    """
    Creates and saves publication-quality visualizations.
    Applies matplotx github dark theme for consistent styling.
    """
    
    def __init__(
        self,
        output_dir: Path,
        theme: str = "dark",
        figsize: Tuple[int, int] = (12, 8),
        dpi: int = 300
    ):
        """
        Initialize the visualizer with style settings.
        
        Args:
            output_dir: Directory to save plots
            theme: Theme name ('dark' or 'light')
            figsize: Figure size in inches (width, height)
            dpi: Resolution for saved images
        """
        self.output_dir: Path = Path(output_dir)
        self.theme: str = theme
        self.figsize: Tuple[int, int] = figsize
        self.dpi: int = dpi
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Apply theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """Apply matplotx github theme if available."""
        if MATPLOTX_AVAILABLE:
            try:
                plt.style.use(matplotx.styles.github[self.theme])
            except Exception as e:
                print(f"Warning: Could not apply matplotx theme. Using default. Error: {e}")
                plt.style.use('dark_background' if self.theme == 'dark' else 'default')
        else:
            plt.style.use('dark_background' if self.theme == 'dark' else 'default')
    
    def plot_cumulative_returns(
        self,
        cumulative_returns: pd.DataFrame,
        title: str = "Cumulative Returns",
        filename: str = "cumulative_returns.png"
    ) -> None:
        """
        Plot cumulative returns over time.
        
        Args:
            cumulative_returns: DataFrame with cumulative returns
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot each series
        for column in cumulative_returns.columns:
            ax.plot(
                cumulative_returns.index,
                cumulative_returns[column] * 100,
                label=column,
                linewidth=2
            )
        
        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cumulative Return (%)', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='best', frameon=True, fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add zero line
        ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
        
        plt.tight_layout()
        self._save_figure(fig, filename)
        plt.close(fig)
    
    def plot_drawdowns(
        self,
        drawdowns: pd.DataFrame,
        title: str = "Drawdown Analysis",
        filename: str = "drawdowns.png"
    ) -> None:
        """
        Plot drawdown series for all assets.
        
        Args:
            drawdowns: DataFrame with drawdown values
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot each series
        for column in drawdowns.columns:
            ax.fill_between(
                drawdowns.index,
                drawdowns[column] * 100,
                0,
                alpha=0.3,
                label=column
            )
            ax.plot(
                drawdowns.index,
                drawdowns[column] * 100,
                linewidth=1.5
            )
        
        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='lower left', frameon=True, fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        self._save_figure(fig, filename)
        plt.close(fig)
    
    def plot_correlation_matrix(
        self,
        correlation_matrix: pd.DataFrame,
        title: str = "Correlation Matrix",
        filename: str = "correlation_matrix.png"
    ) -> None:
        """
        Plot correlation matrix as a heatmap.
        
        Args:
            correlation_matrix: DataFrame with correlations
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        im = ax.imshow(correlation_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(correlation_matrix.columns)))
        ax.set_yticks(np.arange(len(correlation_matrix.index)))
        ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
        ax.set_yticklabels(correlation_matrix.index)
        
        # Add correlation values as text
        for i in range(len(correlation_matrix.index)):
            for j in range(len(correlation_matrix.columns)):
                value = correlation_matrix.iloc[i, j]
                text = ax.text(
                    j, i, f'{value:.2f}',
                    ha='center', va='center',
                    color='black' if abs(value) > 0.5 else 'white',
                    fontsize=10, fontweight='bold'
                )
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation', rotation=270, labelpad=20, fontsize=12)
        
        # Formatting
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._save_figure(fig, filename)
        plt.close(fig)
    
    def plot_performance_summary(
        self,
        summary: pd.DataFrame,
        title: str = "Performance Summary",
        filename: str = "performance_summary.png"
    ) -> None:
        """
        Plot performance metrics as a grouped bar chart.
        
        Args:
            summary: DataFrame with performance metrics
            title: Chart title
            filename: Output filename
        """
        # Select key metrics for visualization
        metrics_to_plot = [
            'Annualized Return',
            'Annualized Volatility',
            'Sharpe Ratio'
        ]
        
        # Filter available metrics
        available_metrics = [m for m in metrics_to_plot if m in summary.columns]
        
        if not available_metrics:
            print("Warning: No suitable metrics found for plotting.")
            return
        
        n_metrics = len(available_metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(6 * n_metrics, 6))
        
        if n_metrics == 1:
            axes = [axes]
        
        for idx, metric in enumerate(available_metrics):
            ax = axes[idx]
            data = summary[metric] * 100 if 'Return' in metric or 'Volatility' in metric else summary[metric]
            
            bars = ax.bar(range(len(data)), data, alpha=0.8)
            
            # Color bars
            colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(data)))
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            
            # Formatting
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(data.index, rotation=45, ha='right')
            ax.set_ylabel(metric + (' (%)' if 'Return' in metric or 'Volatility' in metric else ''))
            ax.set_title(metric, fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y', linestyle='--')
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, data)):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2., height,
                    f'{value:.2f}',
                    ha='center', va='bottom', fontsize=9
                )
        
        fig.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        self._save_figure(fig, filename)
        plt.close(fig)
    
    def plot_pie_chart(
        self,
        data: pd.Series,
        title: str = "Allocation",
        filename: str = "allocation_pie.png"
    ) -> None:
        """
        Plot pie chart with labels in list format (legend).
        As per requirements: no labels on slices, use legend instead.
        
        Args:
            data: Series with values to plot
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create pie chart without labels on slices
        colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
        wedges, texts, autotexts = ax.pie(
            data.values,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 11, 'weight': 'bold'}
        )
        
        # Create legend with labels in list format
        legend_labels = [f'{label}: {value:.2f}%' for label, value in zip(data.index, data.values)]
        ax.legend(
            wedges,
            legend_labels,
            title=title,
            loc='center left',
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=10,
            frameon=True
        )
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._save_figure(fig, filename)
        plt.close(fig)
    
    def plot_comparison_bars(
        self,
        data: pd.Series,
        title: str = "Comparison",
        ylabel: str = "Value",
        filename: str = "comparison_bars.png"
    ) -> None:
        """
        Plot horizontal bar chart for easy comparison.
        
        Args:
            data: Series with values to plot
            title: Chart title
            ylabel: Y-axis label
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Sort data for better visualization
        data_sorted = data.sort_values(ascending=True)
        
        # Create horizontal bars
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(data_sorted)))
        bars = ax.barh(range(len(data_sorted)), data_sorted.values, color=colors, alpha=0.8)
        
        # Formatting
        ax.set_yticks(range(len(data_sorted)))
        ax.set_yticklabels(data_sorted.index)
        ax.set_xlabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, data_sorted.values)):
            width = bar.get_width()
            ax.text(
                width, bar.get_y() + bar.get_height() / 2.,
                f'{value:.2f}',
                ha='left', va='center', fontsize=9, fontweight='bold'
            )
        
        plt.tight_layout()
        self._save_figure(fig, filename)
        plt.close(fig)
    
    def _save_figure(self, fig: plt.Figure, filename: str) -> None:
        """
        Save figure to output directory.
        
        Args:
            fig: Matplotlib figure object
            filename: Output filename
        """
        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=self.dpi, bbox_inches='tight', facecolor='auto')
        print(f"Saved: {output_path}")
