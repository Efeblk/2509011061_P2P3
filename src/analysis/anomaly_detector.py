"""
Anomaly Detection Module

Detects anomalies and suspicious patterns in event data:
- Price outliers (unusually expensive/cheap events)
- Suspicious data patterns
- Data quality issues
- Temporal anomalies
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Tuple
from loguru import logger
from datetime import datetime, timedelta
from collections import Counter


class AnomalyDetector:
    """Detect anomalies and suspicious patterns in event data."""

    def __init__(self):
        """Initialize anomaly detector."""
        self.data = None
        self.anomalies = []

    async def detect_anomalies(self, events: List[Any]) -> Dict[str, Any]:
        """
        Detect all types of anomalies in event data.

        Args:
            events: List of EventNode objects

        Returns:
            Dictionary containing detected anomalies
        """
        logger.info(f"Starting anomaly detection on {len(events)} events")

        # Convert to pandas DataFrame
        self.data = self._events_to_dataframe(events)

        results = {
            "price_outliers": self._detect_price_outliers(),
            "suspicious_prices": self._detect_suspicious_prices(),
            "temporal_anomalies": self._detect_temporal_anomalies(),
            "data_quality_issues": self._detect_data_quality_issues(),
            "duplicate_detection": self._detect_potential_duplicates(),
            "venue_anomalies": self._detect_venue_anomalies(),
            "summary": self._create_anomaly_summary(),
        }

        logger.info(f"Detected {len(self.anomalies)} total anomalies")
        return results

    def _events_to_dataframe(self, events: List[Any]) -> pd.DataFrame:
        """Convert event objects to pandas DataFrame."""
        data = []
        for event in events:
            data.append({
                'uuid': event.uuid,
                'title': event.title,
                'price': float(event.price) if event.price else 0.0,
                'category': event.category or 'unknown',
                'venue': event.venue or 'unknown',
                'date': event.date,
                'url': event.url,
                'description': event.description or '',
                'description_length': len(event.description) if event.description else 0,
            })

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        return df

    def _detect_price_outliers(self) -> Dict[str, Any]:
        """
        Detect price outliers using multiple methods:
        1. IQR method (box plot outliers)
        2. Z-score method (statistical outliers)
        3. Modified Z-score (robust to extreme outliers)
        """
        prices = self.data[self.data['price'] > 0].copy()

        if len(prices) == 0:
            return {"outliers": []}

        # Method 1: IQR method (1.5 * IQR rule)
        q1 = prices['price'].quantile(0.25)
        q3 = prices['price'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        iqr_outliers = prices[(prices['price'] < lower_bound) | (prices['price'] > upper_bound)]

        # Method 2: Z-score method (|z| > 3)
        z_scores = np.abs(stats.zscore(prices['price']))
        z_outliers = prices[z_scores > 3]

        # Method 3: Modified Z-score using MAD (Median Absolute Deviation)
        median = prices['price'].median()
        mad = np.median(np.abs(prices['price'] - median))
        modified_z_scores = 0.6745 * (prices['price'] - median) / mad
        modified_z_outliers = prices[np.abs(modified_z_scores) > 3.5]

        # Combine all methods (union of outliers)
        all_outlier_uuids = set(iqr_outliers['uuid']) | set(z_outliers['uuid']) | set(modified_z_outliers['uuid'])
        all_outliers = prices[prices['uuid'].isin(all_outlier_uuids)]

        # Categorize outliers
        expensive_outliers = all_outliers[all_outliers['price'] > upper_bound].sort_values('price', ascending=False)
        cheap_outliers = all_outliers[all_outliers['price'] < lower_bound].sort_values('price')

        # Record anomalies
        for _, event in expensive_outliers.iterrows():
            self.anomalies.append({
                "type": "price_outlier_expensive",
                "severity": "high" if event['price'] > q3 + 3 * iqr else "medium",
                "event_uuid": event['uuid'],
                "event_title": event['title'],
                "price": event['price'],
                "reason": f"Price {event['price']:.2f} TL significantly higher than typical (Q3: {q3:.2f} TL)",
            })

        return {
            "total_outliers": len(all_outliers),
            "percentage": float(len(all_outliers) / len(prices) * 100),
            "bounds": {
                "lower": float(lower_bound),
                "upper": float(upper_bound),
            },
            "expensive_outliers": {
                "count": len(expensive_outliers),
                "top_10": [
                    {
                        "title": row['title'],
                        "price": float(row['price']),
                        "category": row['category'],
                        "venue": row['venue'],
                        "z_score": float((row['price'] - prices['price'].mean()) / prices['price'].std()),
                    }
                    for _, row in expensive_outliers.head(10).iterrows()
                ]
            },
            "cheap_outliers": {
                "count": len(cheap_outliers),
                "examples": [
                    {
                        "title": row['title'],
                        "price": float(row['price']),
                        "category": row['category'],
                        "reason": "Suspiciously low price"
                    }
                    for _, row in cheap_outliers.head(10).iterrows()
                ]
            },
            "detection_methods": {
                "iqr_method": len(iqr_outliers),
                "z_score_method": len(z_outliers),
                "modified_z_score_method": len(modified_z_outliers),
            }
        }

    def _detect_suspicious_prices(self) -> Dict[str, Any]:
        """Detect suspicious price patterns."""
        suspicious = []

        # Suspiciously round numbers (e.g., 1000, 2000, 5000)
        round_prices = self.data[
            (self.data['price'] > 0) &
            (self.data['price'] % 1000 == 0) &
            (self.data['price'] >= 1000)
        ]

        for _, event in round_prices.iterrows():
            suspicious.append({
                "type": "suspiciously_round_price",
                "severity": "low",
                "event_uuid": event['uuid'],
                "event_title": event['title'],
                "price": event['price'],
                "reason": f"Price is a suspiciously round number ({event['price']:.0f} TL)",
            })

        # Prices ending in .99 or .00 (psychological pricing)
        decimal_prices = self.data[self.data['price'] > 0].copy()
        decimal_prices['decimal_part'] = (decimal_prices['price'] % 1 * 100).round()
        psychological_prices = decimal_prices[decimal_prices['decimal_part'].isin([0, 99])]

        # Zero-price events in paid categories
        free_in_paid_category = self.data[
            (self.data['price'] == 0) &
            (~self.data['category'].isin(['seminar', 'workshop', 'conference']))
        ]

        for _, event in free_in_paid_category.head(20).iterrows():
            suspicious.append({
                "type": "free_event_in_paid_category",
                "severity": "low",
                "event_uuid": event['uuid'],
                "event_title": event['title'],
                "price": 0.0,
                "category": event['category'],
                "reason": f"Free event in typically paid category ({event['category']})",
            })

        self.anomalies.extend(suspicious)

        return {
            "total_suspicious": len(suspicious),
            "round_prices": {
                "count": len(round_prices),
                "examples": round_prices[['title', 'price', 'category']].head(10).to_dict('records'),
            },
            "psychological_pricing": {
                "count": len(psychological_prices),
                "percentage": float(len(psychological_prices) / len(decimal_prices) * 100),
            },
            "free_in_paid_category": {
                "count": len(free_in_paid_category),
                "examples": free_in_paid_category[['title', 'category', 'venue']].head(10).to_dict('records'),
            }
        }

    def _detect_temporal_anomalies(self) -> Dict[str, Any]:
        """Detect temporal anomalies in event dates."""
        valid_dates = self.data[self.data['date'].notna()].copy()

        if len(valid_dates) == 0:
            return {"anomalies": []}

        now = pd.Timestamp.now()
        anomalies = []

        # Events in the past
        past_events = valid_dates[valid_dates['date'] < now]
        if len(past_events) > 0:
            for _, event in past_events.head(20).iterrows():
                anomalies.append({
                    "type": "past_event",
                    "severity": "medium",
                    "event_uuid": event['uuid'],
                    "event_title": event['title'],
                    "date": str(event['date']),
                    "reason": f"Event date is in the past ({event['date'].strftime('%Y-%m-%d')})",
                })

        # Events too far in the future (> 1 year)
        future_threshold = now + pd.Timedelta(days=365)
        far_future = valid_dates[valid_dates['date'] > future_threshold]
        if len(far_future) > 0:
            for _, event in far_future.head(20).iterrows():
                anomalies.append({
                    "type": "far_future_event",
                    "severity": "low",
                    "event_uuid": event['uuid'],
                    "event_title": event['title'],
                    "date": str(event['date']),
                    "reason": f"Event is more than 1 year in the future ({event['date'].strftime('%Y-%m-%d')})",
                })

        # Events on unusual times (3 AM - 6 AM)
        valid_dates['hour'] = valid_dates['date'].dt.hour
        unusual_hours = valid_dates[valid_dates['hour'].between(3, 6)]
        if len(unusual_hours) > 0:
            for _, event in unusual_hours.head(20).iterrows():
                anomalies.append({
                    "type": "unusual_time",
                    "severity": "low",
                    "event_uuid": event['uuid'],
                    "event_title": event['title'],
                    "time": event['date'].strftime('%H:%M'),
                    "reason": f"Event scheduled at unusual hour ({event['date'].strftime('%H:%M')})",
                })

        self.anomalies.extend(anomalies)

        return {
            "total_anomalies": len(anomalies),
            "past_events": {
                "count": len(past_events),
                "percentage": float(len(past_events) / len(valid_dates) * 100),
            },
            "far_future_events": {
                "count": len(far_future),
                "examples": far_future[['title', 'date']].head(10).to_dict('records'),
            },
            "unusual_hours": {
                "count": len(unusual_hours),
                "examples": unusual_hours[['title', 'date']].head(10).to_dict('records'),
            }
        }

    def _detect_data_quality_issues(self) -> Dict[str, Any]:
        """Detect data quality issues and missing information."""
        issues = []

        # Missing descriptions
        no_description = self.data[self.data['description_length'] == 0]
        issues_count = len(no_description)

        # Very short descriptions (< 50 chars)
        short_description = self.data[
            (self.data['description_length'] > 0) &
            (self.data['description_length'] < 50)
        ]

        # Missing venue
        no_venue = self.data[(self.data['venue'] == 'unknown') | (self.data['venue'] == '')]

        # Missing category
        no_category = self.data[(self.data['category'] == 'unknown') | (self.data['category'] == '')]

        # Missing dates
        no_date = self.data[self.data['date'].isna()]

        # Record quality issues
        for _, event in no_description.head(50).iterrows():
            issues.append({
                "type": "missing_description",
                "severity": "medium",
                "event_uuid": event['uuid'],
                "event_title": event['title'],
                "reason": "Event has no description",
            })

        self.anomalies.extend(issues)

        return {
            "total_quality_issues": issues_count + len(short_description) + len(no_venue) + len(no_category) + len(no_date),
            "missing_description": {
                "count": len(no_description),
                "percentage": float(len(no_description) / len(self.data) * 100),
            },
            "short_description": {
                "count": len(short_description),
                "percentage": float(len(short_description) / len(self.data) * 100),
                "examples": short_description[['title', 'description', 'description_length']].head(5).to_dict('records'),
            },
            "missing_venue": {
                "count": len(no_venue),
                "percentage": float(len(no_venue) / len(self.data) * 100),
            },
            "missing_category": {
                "count": len(no_category),
                "percentage": float(len(no_category) / len(self.data) * 100),
            },
            "missing_date": {
                "count": len(no_date),
                "percentage": float(len(no_date) / len(self.data) * 100),
            },
            "data_completeness_score": float(
                100 - (
                    (len(no_description) + len(no_venue) + len(no_category) + len(no_date)) /
                    (len(self.data) * 4) * 100
                )
            ),
        }

    def _detect_potential_duplicates(self) -> Dict[str, Any]:
        """Detect potential duplicate events using fuzzy matching."""
        from difflib import SequenceMatcher

        duplicates = []
        processed = set()

        # Group by date for efficiency
        for date, group in self.data.groupby(self.data['date'].dt.date):
            if pd.isna(date):
                continue

            events_list = group.to_dict('records')

            for i, event1 in enumerate(events_list):
                if event1['uuid'] in processed:
                    continue

                for event2 in events_list[i + 1:]:
                    if event2['uuid'] in processed:
                        continue

                    # Calculate similarity
                    similarity = SequenceMatcher(
                        None,
                        event1['title'].lower(),
                        event2['title'].lower()
                    ).ratio()

                    # Same venue and high title similarity
                    if similarity > 0.8 and event1['venue'] == event2['venue']:
                        duplicates.append({
                            "type": "potential_duplicate",
                            "severity": "high" if similarity > 0.95 else "medium",
                            "event1": {
                                "uuid": event1['uuid'],
                                "title": event1['title'],
                                "price": event1['price'],
                            },
                            "event2": {
                                "uuid": event2['uuid'],
                                "title": event2['title'],
                                "price": event2['price'],
                            },
                            "similarity": float(similarity),
                            "reason": f"Highly similar titles ({similarity * 100:.1f}% match) at same venue on same date",
                        })
                        processed.add(event2['uuid'])

        self.anomalies.extend(duplicates)

        return {
            "total_potential_duplicates": len(duplicates),
            "high_confidence": len([d for d in duplicates if d['severity'] == 'high']),
            "examples": duplicates[:20],
        }

    def _detect_venue_anomalies(self) -> Dict[str, Any]:
        """Detect anomalies related to venues."""
        # Venues with only one event
        venue_counts = self.data['venue'].value_counts()
        single_event_venues = venue_counts[venue_counts == 1]

        # Venues with extreme price variance
        venue_price_stats = self.data[self.data['price'] > 0].groupby('venue')['price'].agg(['mean', 'std', 'count'])
        high_variance_venues = venue_price_stats[
            (venue_price_stats['std'] / venue_price_stats['mean'] > 1.0) &
            (venue_price_stats['count'] >= 5)
        ].sort_values('std', ascending=False)

        return {
            "single_event_venues": {
                "count": len(single_event_venues),
                "percentage": float(len(single_event_venues) / len(venue_counts) * 100),
            },
            "high_price_variance_venues": {
                "count": len(high_variance_venues),
                "top_10": [
                    {
                        "venue": venue,
                        "mean_price": float(stats['mean']),
                        "std_dev": float(stats['std']),
                        "coefficient_of_variation": float(stats['std'] / stats['mean'] * 100),
                        "event_count": int(stats['count']),
                    }
                    for venue, stats in high_variance_venues.head(10).iterrows()
                ]
            }
        }

    def _create_anomaly_summary(self) -> Dict[str, Any]:
        """Create summary of all detected anomalies."""
        severity_counts = Counter(a['severity'] for a in self.anomalies)
        type_counts = Counter(a['type'] for a in self.anomalies)

        return {
            "total_anomalies": len(self.anomalies),
            "by_severity": dict(severity_counts),
            "by_type": dict(type_counts),
            "anomaly_rate": float(len(self.anomalies) / len(self.data) * 100) if len(self.data) > 0 else 0,
            "top_anomalies": sorted(
                self.anomalies,
                key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['severity']],
                reverse=True
            )[:50]
        }

    def get_anomaly_score(self, event_uuid: str) -> float:
        """
        Calculate anomaly score for a specific event (0-100).

        Args:
            event_uuid: Event UUID

        Returns:
            Anomaly score (higher = more anomalous)
        """
        event_anomalies = [a for a in self.anomalies if a.get('event_uuid') == event_uuid]

        if not event_anomalies:
            return 0.0

        severity_weights = {'high': 40, 'medium': 20, 'low': 10}
        score = sum(severity_weights[a['severity']] for a in event_anomalies)

        return min(score, 100.0)
