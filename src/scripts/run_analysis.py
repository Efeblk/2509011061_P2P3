"""
Run Advanced Statistical Analysis and Anomaly Detection

This script performs comprehensive statistical analysis including:
- Quartile analysis and box plot statistics
- Distribution analysis (skewness, kurtosis, normality tests)
- Category-wise statistical comparisons (ANOVA)
- Correlation analysis
- Anomaly detection (outliers, suspicious patterns)
- Scientific reporting

Usage:
    python src/scripts/run_analysis.py [--output-format markdown|json] [--save-plots]
"""

import asyncio
import argparse
from pathlib import Path
from loguru import logger

from src.models.event import EventNode
from src.analysis.statistics import StatisticalAnalyzer
from src.analysis.anomaly_detector import AnomalyDetector
from src.analysis.scientific_report import ScientificReporter


async def main():
    """Run comprehensive statistical analysis."""
    parser = argparse.ArgumentParser(description="Run statistical analysis and anomaly detection")
    parser.add_argument(
        "--output-format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format for the report"
    )
    parser.add_argument(
        "--output-file",
        default="STATISTICAL_ANALYSIS_REPORT.md",
        help="Output file path"
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("ADVANCED STATISTICAL ANALYSIS & ANOMALY DETECTION")
    logger.info("=" * 60)

    # Fetch all events from database
    logger.info("Fetching events from database...")
    events = await EventNode.get_all_events()
    logger.info(f"Loaded {len(events)} events")

    if len(events) == 0:
        logger.error("No events found in database")
        return

    # Run statistical analysis
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: Statistical Analysis")
    logger.info("=" * 60)

    analyzer = StatisticalAnalyzer()
    stats_results = await analyzer.analyze_events(events)

    logger.info("✓ Statistical analysis complete")
    logger.info(f"  - Mean price: {stats_results['summary']['price_statistics']['mean']:.2f} TL")
    logger.info(f"  - Median price: {stats_results['summary']['price_statistics']['median']:.2f} TL")
    logger.info(f"  - Categories analyzed: {stats_results['summary']['categories']['total_categories']}")

    # Run anomaly detection
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Anomaly Detection")
    logger.info("=" * 60)

    detector = AnomalyDetector()
    anomaly_results = await detector.detect_anomalies(events)

    logger.info("✓ Anomaly detection complete")
    logger.info(f"  - Total anomalies: {anomaly_results['summary']['total_anomalies']}")
    logger.info(f"  - Price outliers: {anomaly_results['price_outliers']['total_outliers']}")
    logger.info(f"  - Data quality issues: {anomaly_results['data_quality_issues']['total_quality_issues']}")

    # Generate scientific report
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Scientific Report Generation")
    logger.info("=" * 60)

    reporter = ScientificReporter()
    report = reporter.generate_report(stats_results, anomaly_results, args.output_format)

    # Save report
    output_path = Path(args.output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"✓ Report saved to: {output_path}")
    logger.info(f"  - Format: {args.output_format}")
    logger.info(f"  - Size: {len(report):,} characters")

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("ANALYSIS SUMMARY")
    logger.info("=" * 60)

    summary = stats_results['summary']
    logger.info(f"Dataset: {summary['total_events']:,} events")
    logger.info(f"Price range: {summary['price_statistics']['min']:.2f} - {summary['price_statistics']['max']:.2f} TL")
    logger.info(f"Distribution: {stats_results['price_analysis']['distribution_shape']}")
    logger.info(f"Normality: {stats_results['distribution_tests']['conclusion']}")
    logger.info(f"Anomaly rate: {anomaly_results['summary']['anomaly_rate']:.2f}%")
    logger.info(f"Data completeness: {anomaly_results['data_quality_issues']['data_completeness_score']:.1f}%")

    logger.info("\n" + "=" * 60)
    logger.info("ANALYSIS COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"\nView full report: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
