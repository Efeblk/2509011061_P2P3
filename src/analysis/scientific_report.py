"""
Scientific Reporting Module

Generates comprehensive scientific reports with:
- Statistical summaries with confidence intervals
- Hypothesis testing results
- Data visualizations
- Interpretation and conclusions
"""

import json
from typing import Dict, List, Any
from datetime import datetime
from loguru import logger


class ScientificReporter:
    """Generate scientific analysis reports."""

    def __init__(self):
        """Initialize reporter."""
        self.stats_results = None
        self.anomaly_results = None

    def generate_report(
        self,
        stats_results: Dict[str, Any],
        anomaly_results: Dict[str, Any],
        output_format: str = "markdown"
    ) -> str:
        """
        Generate comprehensive scientific report.

        Args:
            stats_results: Statistical analysis results
            anomaly_results: Anomaly detection results
            output_format: Output format ('markdown' or 'json')

        Returns:
            Formatted report string
        """
        self.stats_results = stats_results
        self.anomaly_results = anomaly_results

        if output_format == "json":
            return self._generate_json_report()
        else:
            return self._generate_markdown_report()

    def _generate_markdown_report(self) -> str:
        """Generate markdown formatted scientific report."""
        report = []

        # Header
        report.append("# Scientific Analysis Report")
        report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n**Dataset Size**: {self.stats_results['summary']['total_events']:,} events")
        report.append("\n---\n")

        # Executive Summary
        report.append(self._section_executive_summary())

        # Statistical Analysis
        report.append(self._section_statistical_analysis())

        # Anomaly Detection
        report.append(self._section_anomaly_detection())

        # Conclusions
        report.append(self._section_conclusions())

        return "\n".join(report)

    def _section_executive_summary(self) -> str:
        """Generate executive summary section."""
        summary = self.stats_results['summary']
        price_stats = summary['price_statistics']

        lines = [
            "## Executive Summary\n",
            "### Dataset Overview",
            f"- **Total Events**: {summary['total_events']:,}",
            f"- **Priced Events**: {price_stats['count']:,} ({price_stats['count']/summary['total_events']*100:.1f}%)",
            f"- **Free Events**: {summary['free_events']['count']:,} ({summary['free_events']['percentage']:.1f}%)",
            f"- **Categories**: {summary['categories']['total_categories']}",
            f"- **Venues**: {summary['venues']['total_venues']:,}",
            "",
            "### Price Distribution",
            f"- **Mean Price**: {price_stats['mean']:.2f} TL",
            f"- **Median Price**: {price_stats['median']:.2f} TL",
            f"- **Price Range**: {price_stats['min']:.2f} - {price_stats['max']:.2f} TL",
            f"- **Standard Deviation**: {price_stats['std']:.2f} TL",
            f"- **Coefficient of Variation**: {price_stats['coefficient_of_variation']:.1f}%",
            "",
        ]

        # Interpretation
        cv = price_stats['coefficient_of_variation']
        if cv > 100:
            lines.append("**Interpretation**: Price distribution shows **high variability** (CV > 100%), indicating significant price differences across events.")
        elif cv > 50:
            lines.append("**Interpretation**: Price distribution shows **moderate variability** (CV: 50-100%).")
        else:
            lines.append("**Interpretation**: Price distribution is **relatively consistent** (CV < 50%).")

        lines.append("")
        return "\n".join(lines)

    def _section_statistical_analysis(self) -> str:
        """Generate statistical analysis section."""
        lines = [
            "## Statistical Analysis\n",
            "### 1. Quartile Analysis (Box Plot Statistics)",
            "",
        ]

        quartiles = self.stats_results['quartile_analysis']
        lines.extend([
            "**Quartiles**:",
            f"- Q1 (25th percentile): {quartiles['quartiles']['q1']:.2f} TL",
            f"- Q2 (50th percentile / Median): {quartiles['quartiles']['q2_median']:.2f} TL",
            f"- Q3 (75th percentile): {quartiles['quartiles']['q3']:.2f} TL",
            f"- **Interquartile Range (IQR)**: {quartiles['interquartile_range']:.2f} TL",
            "",
            "**Whiskers** (1.5 × IQR rule):",
            f"- Lower: {quartiles['whiskers']['lower']:.2f} TL",
            f"- Upper: {quartiles['whiskers']['upper']:.2f} TL",
            "",
            "**Outliers**:",
            f"- Count: {quartiles['outliers']['count']} ({quartiles['outliers']['percentage']:.1f}%)",
            f"- Values: {', '.join([f'{v:.2f}' for v in quartiles['outliers']['values'][:10]])}{'...' if len(quartiles['outliers']['values']) > 10 else ''}",
            "",
            "**Key Percentiles**:",
            f"- 5th: {quartiles['percentiles']['5th']:.2f} TL",
            f"- 10th: {quartiles['percentiles']['10th']:.2f} TL",
            f"- 90th: {quartiles['percentiles']['90th']:.2f} TL",
            f"- 95th: {quartiles['percentiles']['95th']:.2f} TL",
            f"- 99th: {quartiles['percentiles']['99th']:.2f} TL",
            "",
        ])

        # Distribution Analysis
        lines.append("### 2. Distribution Analysis\n")
        dist = self.stats_results['price_analysis']
        lines.extend([
            f"**Skewness**: {dist['skewness']:.3f}",
            f"- **Interpretation**: Distribution is {dist['distribution_shape']}",
            "",
            f"**Kurtosis**: {dist['kurtosis']:.3f}",
            f"- **Interpretation**: Distribution is {dist['kurtosis_interpretation']}",
            "",
            f"**Range**: {dist['range']:.2f} TL",
            f"**Interquartile Range**: {dist['interquartile_range']:.2f} TL",
            "",
        ])

        # Normality Tests
        lines.append("### 3. Normality Tests\n")
        norm_tests = self.stats_results['distribution_tests']

        if 'shapiro_wilk_test' in norm_tests and 'note' not in norm_tests['shapiro_wilk_test']:
            shapiro = norm_tests['shapiro_wilk_test']
            lines.extend([
                "**Shapiro-Wilk Test**:",
                f"- Statistic: {shapiro['statistic']:.6f}",
                f"- P-value: {shapiro['p_value']:.6f}",
                f"- **Result**: {shapiro['interpretation']}",
                "",
            ])

        ks = norm_tests['kolmogorov_smirnov_test']
        lines.extend([
            "**Kolmogorov-Smirnov Test**:",
            f"- Statistic: {ks['statistic']:.6f}",
            f"- P-value: {ks['p_value']:.6f}",
            f"- **Result**: {ks['interpretation']}",
            "",
            f"**Conclusion**: {norm_tests['conclusion']}",
            "",
        ])

        # Category Comparison
        lines.append("### 4. Category Comparison (ANOVA)\n")
        cat_comp = self.stats_results['category_comparison']

        if cat_comp['anova_test']:
            anova = cat_comp['anova_test']
            lines.extend([
                "**One-Way ANOVA Test** (H₀: All categories have equal mean prices)",
                f"- F-statistic: {anova['f_statistic']:.4f}",
                f"- P-value: {anova['p_value']:.6f}",
                f"- **Significant**: {'Yes' if anova['significant'] else 'No'} (α = 0.05)",
                f"- **Interpretation**: {anova['interpretation']}",
                "",
            ])

        if cat_comp['pairwise_comparison']:
            pair = cat_comp['pairwise_comparison']
            lines.extend([
                "**Pairwise Comparison** (Cheapest vs Most Expensive Category):",
                f"- Cheapest: **{pair['cheapest_category']}**",
                f"- Most Expensive: **{pair['most_expensive_category']}**",
                f"- Price Difference: {pair['price_difference']:.2f} TL",
                f"- T-statistic: {pair['t_statistic']:.4f}",
                f"- P-value: {pair['p_value']:.6f}",
                f"- **Significant**: {'Yes' if pair['significant'] else 'No'}",
                "",
            ])

        # Category Statistics Table
        lines.append("**Category Price Statistics**:\n")
        lines.append("| Category | Count | Mean | Median | Std Dev | Q1 | Q3 |")
        lines.append("|----------|-------|------|--------|---------|----|----|")

        for cat, stats in sorted(cat_comp['category_statistics'].items(), key=lambda x: x[1]['mean'], reverse=True):
            lines.append(
                f"| {cat} | {stats['count']} | {stats['mean']:.2f} | {stats['median']:.2f} | "
                f"{stats['std']:.2f} | {stats['q1']:.2f} | {stats['q3']:.2f} |"
            )

        lines.append("")
        return "\n".join(lines)

    def _section_anomaly_detection(self) -> str:
        """Generate anomaly detection section."""
        lines = [
            "## Anomaly Detection\n",
            "### Overview",
            "",
        ]

        summary = self.anomaly_results['summary']
        lines.extend([
            f"**Total Anomalies Detected**: {summary['total_anomalies']:,}",
            f"**Anomaly Rate**: {summary['anomaly_rate']:.2f}%",
            "",
            "**By Severity**:",
        ])

        for severity, count in summary['by_severity'].items():
            lines.append(f"- {severity.capitalize()}: {count:,}")

        lines.append("\n**By Type**:")
        for atype, count in sorted(summary['by_type'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {atype.replace('_', ' ').title()}: {count:,}")

        lines.append("")

        # Price Outliers
        lines.append("### 1. Price Outliers\n")
        outliers = self.anomaly_results['price_outliers']
        lines.extend([
            f"**Total Price Outliers**: {outliers['total_outliers']} ({outliers['percentage']:.1f}%)",
            "",
            "**Detection Bounds**:",
            f"- Lower: {outliers['bounds']['lower']:.2f} TL",
            f"- Upper: {outliers['bounds']['upper']:.2f} TL",
            "",
            f"**Expensive Outliers**: {outliers['expensive_outliers']['count']}",
            "",
            "**Top 10 Most Expensive Outliers**:",
            "",
            "| Event | Price | Category | Z-Score |",
            "|-------|-------|----------|---------|",
        ])

        for item in outliers['expensive_outliers']['top_10'][:10]:
            lines.append(
                f"| {item['title'][:40]}... | {item['price']:.2f} TL | {item['category']} | {item['z_score']:.2f} |"
            )

        lines.append("")

        # Data Quality Issues
        lines.append("### 2. Data Quality Issues\n")
        quality = self.anomaly_results['data_quality_issues']
        lines.extend([
            f"**Data Completeness Score**: {quality['data_completeness_score']:.1f}%",
            "",
            "**Missing Data**:",
            f"- Missing Description: {quality['missing_description']['count']:,} ({quality['missing_description']['percentage']:.1f}%)",
            f"- Missing Venue: {quality['missing_venue']['count']:,} ({quality['missing_venue']['percentage']:.1f}%)",
            f"- Missing Category: {quality['missing_category']['count']:,} ({quality['missing_category']['percentage']:.1f}%)",
            f"- Missing Date: {quality['missing_date']['count']:,} ({quality['missing_date']['percentage']:.1f}%)",
            "",
        ])

        # Temporal Anomalies
        lines.append("### 3. Temporal Anomalies\n")
        temporal = self.anomaly_results['temporal_anomalies']
        if 'anomalies' in temporal and len(temporal) == 1:
            # No valid dates found
            lines.append("**Note**: No temporal anomalies detected (no valid dates)\n")
        elif 'past_events' in temporal and 'far_future_events' in temporal:
            lines.extend([
                f"**Total Temporal Anomalies**: {temporal.get('total_anomalies', 0):,}",
                f"**Past Events**: {temporal['past_events']['count']:,} ({temporal['past_events']['percentage']:.1f}%)",
                f"**Far Future Events**: {temporal['far_future_events']['count']:,}",
                f"**Unusual Hours**: {temporal['unusual_hours']['count']:,}",
                "",
            ])
        else:
            lines.append("**Note**: Temporal anomaly detection incomplete\n")

        # Potential Duplicates
        lines.append("### 4. Potential Duplicate Detection\n")
        dupes = self.anomaly_results['duplicate_detection']
        lines.extend([
            f"**Potential Duplicates Found**: {dupes['total_potential_duplicates']}",
            f"**High Confidence**: {dupes['high_confidence']}",
            "",
        ])

        return "\n".join(lines)

    def _section_conclusions(self) -> str:
        """Generate conclusions section."""
        lines = [
            "## Conclusions\n",
            "### Key Findings\n",
        ]

        # Statistical conclusions
        price_stats = self.stats_results['summary']['price_statistics']
        dist = self.stats_results['price_analysis']

        lines.append("**1. Price Distribution**")
        if dist['skewness'] > 1:
            lines.append("- The price distribution is **strongly right-skewed**, indicating a concentration of lower-priced events with a long tail of expensive outliers.")
        elif dist['skewness'] > 0.5:
            lines.append("- The price distribution is **moderately right-skewed**, suggesting more affordable events with some expensive options.")
        else:
            lines.append("- The price distribution is **relatively symmetric**.")

        lines.append("")
        lines.append("**2. Category Analysis**")
        cat_comp = self.stats_results['category_comparison']
        if cat_comp['anova_test'] and cat_comp['anova_test']['significant']:
            lines.append("- **Significant price differences** exist across event categories (p < 0.05).")
            if cat_comp['pairwise_comparison']:
                pair = cat_comp['pairwise_comparison']
                lines.append(f"- {pair['most_expensive_category']} events cost significantly more than {pair['cheapest_category']} events.")
        else:
            lines.append("- No significant price differences detected across categories.")

        lines.append("")
        lines.append("**3. Data Quality**")
        quality = self.anomaly_results['data_quality_issues']
        completeness = quality['data_completeness_score']
        if completeness >= 90:
            lines.append(f"- **Excellent data quality** (Completeness: {completeness:.1f}%)")
        elif completeness >= 75:
            lines.append(f"- **Good data quality** (Completeness: {completeness:.1f}%)")
        elif completeness >= 60:
            lines.append(f"- **Fair data quality** (Completeness: {completeness:.1f}%)")
        else:
            lines.append(f"- **Poor data quality** (Completeness: {completeness:.1f}%) - significant missing data detected.")

        lines.append("")
        lines.append("**4. Anomalies**")
        outlier_pct = self.anomaly_results['price_outliers']['percentage']
        lines.append(f"- {outlier_pct:.1f}% of events are statistical outliers")
        lines.append(f"- {self.anomaly_results['summary']['total_anomalies']:,} total anomalies detected across all categories")

        lines.append("")
        lines.append("### Recommendations\n")
        lines.append("1. **Investigate price outliers** - Verify extremely expensive events for data entry errors")
        lines.append("2. **Improve data collection** - Focus on missing descriptions and venue information")
        lines.append("3. **Review temporal anomalies** - Remove or update past events")
        lines.append("4. **Handle duplicates** - Review and merge potential duplicate events")

        lines.append("")
        return "\n".join(lines)

    def _generate_json_report(self) -> str:
        """Generate JSON formatted report."""
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "dataset_size": self.stats_results['summary']['total_events'],
            },
            "statistical_analysis": self.stats_results,
            "anomaly_detection": self.anomaly_results,
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    def save_report(self, filepath: str, format: str = "markdown"):
        """
        Save report to file.

        Args:
            filepath: Output file path
            format: Report format ('markdown' or 'json')
        """
        if self.stats_results is None or self.anomaly_results is None:
            raise ValueError("No results to save. Generate report first.")

        content = self.generate_report(self.stats_results, self.anomaly_results, format)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Report saved to: {filepath}")
