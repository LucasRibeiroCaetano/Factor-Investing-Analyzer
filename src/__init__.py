"""
Factor Investing Analyzer Package.
Production-grade tools for analyzing factor and geographic investment strategies.
"""

__version__ = "1.0.0"
__author__ = "Quantitative Developer"

from src.factors import FactorDataLoader
from src.analysis import PerformanceAnalyzer
from src.geography import GeographyAnalyzer
from src.visualizer import Visualizer

__all__ = [
    "FactorDataLoader",
    "PerformanceAnalyzer",
    "GeographyAnalyzer",
    "Visualizer"
]
