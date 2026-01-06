"""
Advanced Statistical Analysis Module

Provides comprehensive statistical analysis including:
- Quartile analysis and box plot statistics
- Distribution analysis (normal, skewed, kurtosis)
- Correlation analysis between features
- Hypothesis testing for category comparisons
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger
from datetime import datetime


class StatisticalAnalyzer:
    """Advanced statistical analysis for event data."""

    def __init__(self):
        """Initialize the statistical analyzer."""
        self.data = None
        self.results = {}

    async def analyze_events(self, events: List[Any]) -> Dict[str, Any]:
        """
        Perform comprehensive statistical analysis on events.

        Args:
            events: List of EventNode objects

        Returns:
            Dictionary containing all statistical analysis results
        """
        logger.info(f"Starting statistical analysis on {len(events)} events")

        # Convert to pandas DataFrame for easier analysis
        self.data = self._events_to_dataframe(events)

        results = {
            "summary": self._basic_statistics(),
            "price_analysis": self._price_distribution_analysis(),
            "quartile_analysis": self._quartile_analysis(),
            "category_comparison": self._category_statistical_comparison(),
            "temporal_analysis": self._temporal_distribution(),
            "correlation_analysis": self._correlation_analysis(),
            "distribution_tests": self._distribution_normality_tests(),
        }

        self.results = results
        logger.info("Statistical analysis completed")
        return results

    def _events_to_dataframe(self, events: List[Any]) -> pd.DataFrame:
        """Convert event objects to pandas DataFrame."""
        data = []
        for event in events:
            data.append({
                'title': event.title,
                'price': float(event.price) if event.price else 0.0,
                'category': event.category or 'unknown',
                'venue': event.venue or 'unknown',
                'date': event.date,
                'has_description': bool(event.description),
                'description_length': len(event.description) if event.description else 0,
            })

        df = pd.DataFrame(data)

        # Parse dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['hour'] = df['date'].dt.hour

        return df

    def _basic_statistics(self) -> Dict[str, Any]:
        """Calculate basic statistical measures."""
        prices = self.data['price'][self.data['price'] > 0]  # Exclude free events

        return {
            "total_events": len(self.data),
            "price_statistics": {
                "count": len(prices),
                "mean": float(prices.mean()),
                "median": float(prices.median()),
                "std": float(prices.std()),
                "min": float(prices.min()),
                "max": float(prices.max()),
                "variance": float(prices.var()),
                "coefficient_of_variation": float(prices.std() / prices.mean() * 100),
            },
            "free_events": {
                "count": int((self.data['price'] == 0).sum()),
                "percentage": float((self.data['price'] == 0).sum() / len(self.data) * 100),
            },
            "categories": {
                "total_categories": int(self.data['category'].nunique()),
                "distribution": self.data['category'].value_counts().to_dict(),
            },
            "venues": {
                "total_venues": int(self.data['venue'].nunique()),
                "top_10": self.data['venue'].value_counts().head(10).to_dict(),
            },
            "data_quality": {
                "events_with_description": int(self.data['has_description'].sum()),
                "description_coverage": float(self.data['has_description'].sum() / len(self.data) * 100),
                "avg_description_length": float(self.data['description_length'].mean()),
            }
        }

    def _price_distribution_analysis(self) -> Dict[str, Any]:
        """Analyze price distribution characteristics."""
        prices = self.data['price'][self.data['price'] > 0]

        # Calculate skewness and kurtosis
        skewness = stats.skew(prices)
        kurtosis = stats.kurtosis(prices)

        # Determine distribution shape
        if abs(skewness) < 0.5:
            distribution_shape = "approximately symmetric"
        elif skewness > 0:
            distribution_shape = "right-skewed (positively skewed)"
        else:
            distribution_shape = "left-skewed (negatively skewed)"

        # Kurtosis interpretation
        if abs(kurtosis) < 1:
            kurtosis_interpretation = "mesokurtic (normal-like tails)"
        elif kurtosis > 0:
            kurtosis_interpretation = "leptokurtic (heavy tails, peaked)"
        else:
            kurtosis_interpretation = "platykurtic (light tails, flat)"

        return {
            "skewness": float(skewness),
            "kurtosis": float(kurtosis),
            "distribution_shape": distribution_shape,
            "kurtosis_interpretation": kurtosis_interpretation,
            "range": float(prices.max() - prices.min()),
            "interquartile_range": float(prices.quantile(0.75) - prices.quantile(0.25)),
            "modes": prices.mode().tolist() if len(prices.mode()) > 0 else [],
        }

    def _quartile_analysis(self) -> Dict[str, Any]:
        """Perform quartile analysis for box plot statistics."""
        prices = self.data['price'][self.data['price'] > 0]

        q1 = prices.quantile(0.25)
        q2 = prices.quantile(0.50)  # Median
        q3 = prices.quantile(0.75)
        iqr = q3 - q1

        # Calculate whiskers (1.5 * IQR rule)
        lower_whisker = q1 - 1.5 * iqr
        upper_whisker = q3 + 1.5 * iqr

        # Find outliers
        outliers = prices[(prices < lower_whisker) | (prices > upper_whisker)]

        return {
            "quartiles": {
                "q1": float(q1),
                "q2_median": float(q2),
                "q3": float(q3),
            },
            "interquartile_range": float(iqr),
            "whiskers": {
                "lower": float(max(prices.min(), lower_whisker)),
                "upper": float(min(prices.max(), upper_whisker)),
            },
            "outliers": {
                "count": len(outliers),
                "percentage": float(len(outliers) / len(prices) * 100),
                "values": sorted(outliers.tolist()),
            },
            "percentiles": {
                "5th": float(prices.quantile(0.05)),
                "10th": float(prices.quantile(0.10)),
                "25th": float(q1),
                "50th": float(q2),
                "75th": float(q3),
                "90th": float(prices.quantile(0.90)),
                "95th": float(prices.quantile(0.95)),
                "99th": float(prices.quantile(0.99)),
            }
        }

    def _category_statistical_comparison(self) -> Dict[str, Any]:
        """Compare price distributions across categories using statistical tests."""
        categories = self.data['category'].unique()
        category_prices = {}
        category_stats = {}

        # Collect prices by category
        for cat in categories:
            cat_prices = self.data[self.data['category'] == cat]['price']
            cat_prices = cat_prices[cat_prices > 0]  # Exclude free events

            if len(cat_prices) > 0:
                category_prices[cat] = cat_prices
                category_stats[cat] = {
                    "count": len(cat_prices),
                    "mean": float(cat_prices.mean()),
                    "median": float(cat_prices.median()),
                    "std": float(cat_prices.std()),
                    "q1": float(cat_prices.quantile(0.25)),
                    "q3": float(cat_prices.quantile(0.75)),
                }

        # Perform ANOVA test (H0: all categories have same mean price)
        if len(category_prices) > 1:
            price_groups = list(category_prices.values())
            f_stat, p_value = stats.f_oneway(*price_groups)

            anova_result = {
                "f_statistic": float(f_stat),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "interpretation": (
                    "Significant difference in prices across categories (p < 0.05)"
                    if p_value < 0.05
                    else "No significant difference in prices across categories (p >= 0.05)"
                )
            }
        else:
            anova_result = None

        # Pairwise comparisons (most expensive vs cheapest)
        if len(category_stats) >= 2:
            sorted_cats = sorted(category_stats.items(), key=lambda x: x[1]['mean'])
            cheapest_cat, cheapest_stats = sorted_cats[0]
            most_expensive_cat, most_expensive_stats = sorted_cats[-1]

            # T-test between cheapest and most expensive
            t_stat, t_p_value = stats.ttest_ind(
                category_prices[cheapest_cat],
                category_prices[most_expensive_cat]
            )

            pairwise_comparison = {
                "cheapest_category": cheapest_cat,
                "most_expensive_category": most_expensive_cat,
                "price_difference": float(most_expensive_stats['mean'] - cheapest_stats['mean']),
                "t_statistic": float(t_stat),
                "p_value": float(t_p_value),
                "significant": t_p_value < 0.05,
            }
        else:
            pairwise_comparison = None

        return {
            "category_statistics": category_stats,
            "anova_test": anova_result,
            "pairwise_comparison": pairwise_comparison,
        }

    def _temporal_distribution(self) -> Dict[str, Any]:
        """Analyze temporal patterns in events."""
        valid_dates = self.data[self.data['date'].notna()]

        if len(valid_dates) == 0:
            return {"error": "No valid dates found"}

        # Month distribution
        month_dist = valid_dates['month'].value_counts().sort_index().to_dict()

        # Day of week distribution
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_dist = valid_dates['day_of_week'].value_counts().sort_index()
        dow_dist_named = {day_names[i]: int(count) for i, count in dow_dist.items()}

        # Hour distribution (if available)
        hour_dist = valid_dates[valid_dates['hour'].notna()]['hour'].value_counts().sort_index().to_dict()

        return {
            "month_distribution": month_dist,
            "day_of_week_distribution": dow_dist_named,
            "hour_distribution": hour_dist,
            "busiest_month": int(max(month_dist, key=month_dist.get)) if month_dist else None,
            "busiest_day": day_names[int(max(dow_dist.index, key=lambda x: dow_dist[x]))] if len(dow_dist) > 0 else None,
        }

    def _correlation_analysis(self) -> Dict[str, Any]:
        """Analyze correlations between numerical features."""
        # Prepare numerical data
        numerical_data = self.data[[
            'price',
            'description_length',
            'month',
            'day_of_week',
            'hour'
        ]].copy()

        # Remove rows with missing values
        numerical_data = numerical_data.dropna()

        if len(numerical_data) < 2:
            return {"error": "Insufficient data for correlation analysis"}

        # Calculate correlation matrix
        corr_matrix = numerical_data.corr()

        # Find strong correlations (|r| > 0.3)
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.3:
                    strong_correlations.append({
                        "variable_1": corr_matrix.columns[i],
                        "variable_2": corr_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": self._interpret_correlation(corr_value),
                    })

        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
        }

    def _distribution_normality_tests(self) -> Dict[str, Any]:
        """Test if price distribution follows normal distribution."""
        prices = self.data['price'][self.data['price'] > 0]

        if len(prices) < 3:
            return {"error": "Insufficient data for normality tests"}

        # Shapiro-Wilk test (good for n < 5000)
        if len(prices) <= 5000:
            shapiro_stat, shapiro_p = stats.shapiro(prices)
            shapiro_result = {
                "statistic": float(shapiro_stat),
                "p_value": float(shapiro_p),
                "is_normal": shapiro_p > 0.05,
                "interpretation": (
                    "Data follows normal distribution (p > 0.05)"
                    if shapiro_p > 0.05
                    else "Data does NOT follow normal distribution (p <= 0.05)"
                )
            }
        else:
            shapiro_result = {"note": "Skipped (sample too large for Shapiro-Wilk)"}

        # Kolmogorov-Smirnov test against normal distribution
        ks_stat, ks_p = stats.kstest(
            (prices - prices.mean()) / prices.std(),
            'norm'
        )

        ks_result = {
            "statistic": float(ks_stat),
            "p_value": float(ks_p),
            "is_normal": ks_p > 0.05,
            "interpretation": (
                "Data follows normal distribution (p > 0.05)"
                if ks_p > 0.05
                else "Data does NOT follow normal distribution (p <= 0.05)"
            )
        }

        return {
            "shapiro_wilk_test": shapiro_result,
            "kolmogorov_smirnov_test": ks_result,
            "conclusion": (
                "Normal distribution" if ks_p > 0.05
                else "Non-normal distribution (likely right-skewed)"
            )
        }

    @staticmethod
    def _interpret_correlation(r: float) -> str:
        """Interpret correlation coefficient strength."""
        abs_r = abs(r)
        if abs_r >= 0.7:
            strength = "Strong"
        elif abs_r >= 0.4:
            strength = "Moderate"
        elif abs_r >= 0.3:
            strength = "Weak"
        else:
            strength = "Very weak"

        direction = "positive" if r > 0 else "negative"
        return f"{strength} {direction}"

    def get_box_plot_data(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get box plot data for visualization.

        Args:
            category: Optional category to filter by

        Returns:
            Dictionary with box plot statistics
        """
        if category:
            prices = self.data[self.data['category'] == category]['price']
            prices = prices[prices > 0]
        else:
            prices = self.data['price'][self.data['price'] > 0]

        if len(prices) == 0:
            return {}

        q1 = prices.quantile(0.25)
        q2 = prices.quantile(0.50)
        q3 = prices.quantile(0.75)
        iqr = q3 - q1

        lower_whisker = max(prices.min(), q1 - 1.5 * iqr)
        upper_whisker = min(prices.max(), q3 + 1.5 * iqr)

        outliers = prices[(prices < lower_whisker) | (prices > upper_whisker)]

        return {
            "min": float(prices.min()),
            "q1": float(q1),
            "median": float(q2),
            "q3": float(q3),
            "max": float(prices.max()),
            "lower_whisker": float(lower_whisker),
            "upper_whisker": float(upper_whisker),
            "outliers": sorted(outliers.tolist()),
            "mean": float(prices.mean()),
        }
