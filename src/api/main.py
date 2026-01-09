from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import List, Dict, Any
import numpy as np
from src.models.event import EventNode
from src.analysis.statistics import StatisticalAnalyzer
from src.analysis.anomaly_detector import AnomalyDetector

app = FastAPI(title="EventGraph API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "EventGraph API is running 🚀"}

@app.get("/stats")
async def get_stats():
    """Get high-level statistics."""
    events = await EventNode.get_all_events()
    total = len(events)
    prices = [e.price for e in events if e.price and e.price > 0]
    
    return {
        "total_events": total,
        "mean_price": float(np.mean(prices)) if prices else 0,
        "median_price": float(np.median(prices)) if prices else 0,
        "total_venues": len(set(e.venue for e in events if e.venue))
    }

@app.get("/categories")
async def get_category_data():
    """Get category distribution for bar charts."""
    events = await EventNode.get_all_events()
    from collections import Counter
    counts = Counter(e.category for e in events if e.category)
    
    # Format for Recharts: [{name: 'Music', value: 120}, ...]
    data = [{"name": k, "value": v} for k, v in counts.most_common(10)]
    return data

@app.get("/prices")
async def get_price_analysis():
    """Get average price per category for area charts."""
    events = await EventNode.get_all_events()
    from collections import Counter
    
    # Calculate means
    categories = {}
    for e in events:
        if e.category and e.price and e.price > 0:
            if e.category not in categories:
                categories[e.category] = []
            categories[e.category].append(e.price)
    
    # Format: [{name: 'Music', price: 450}, ...]
    data = []
    for cat, prices in categories.items():
        data.append({"name": cat, "price": int(np.mean(prices))})
    
    # Sort by price descending
    data.sort(key=lambda x: x["price"], reverse=True)
    return data[:10]  # Top 10

@app.get("/distribution")
async def get_price_distribution():
    """Get raw price list for box plots (or histogram bins)."""
    events = await EventNode.get_all_events()
    prices = [e.price for e in events if e.price and e.price > 0]

    # Return bins for histogram to reduce payload size?
    # Or just raw values if not too huge. 18k items is fine.
    # Let's return stats for box plot to save bandwidth.
    if not prices:
        return {"min": 0, "q1": 0, "median": 0, "q3": 0, "max": 0}

    p = np.array(prices)
    return {
        "min": float(np.min(p)),
        "q1": float(np.percentile(p, 25)),
        "median": float(np.median(p)),
        "q3": float(np.percentile(p, 75)),
        "max": float(np.max(p)),
        "raw": [float(x) for x in np.random.choice(p, size=min(len(p), 500), replace=False)] # Sample 500 for scatter
    }


@app.get("/featured")
async def get_featured_events():
    """Get featured events: cheapest, medium, and premium with AI summaries."""
    from src.database.connection import db_connection
    
    try:
        # Get cheapest non-free events with AI summaries
        cheapest_query = """
        MATCH (e:Event)-[:HAS_AI_SUMMARY]->(s:AISummary)
        WHERE e.price > 0
        RETURN e.title, e.price, e.venue, e.category, e.date, s.summary, s.quality_score
        ORDER BY e.price ASC
        LIMIT 3
        """
        
        # Get medium priced events (around median)
        medium_query = """
        MATCH (e:Event)-[:HAS_AI_SUMMARY]->(s:AISummary)
        WHERE e.price >= 400 AND e.price <= 700
        RETURN e.title, e.price, e.venue, e.category, e.date, s.summary, s.quality_score
        ORDER BY s.quality_score DESC
        LIMIT 3
        """
        
        # Get premium/highest priced events
        premium_query = """
        MATCH (e:Event)-[:HAS_AI_SUMMARY]->(s:AISummary)
        WHERE e.price > 0
        RETURN e.title, e.price, e.venue, e.category, e.date, s.summary, s.quality_score
        ORDER BY e.price DESC
        LIMIT 3
        """
        
        def format_event(row):
            return {
                "title": row[0] or "Unknown Event",
                "price": row[1] or 0,
                "venue": row[2] or "TBA",
                "category": row[3] or "Etkinlik",
                "date": row[4] or "",
                "summary": row[5][:200] + "..." if row[5] and len(row[5]) > 200 else (row[5] or ""),
                "quality_score": row[6] or 0
            }
        
        cheapest_result = db_connection.execute_query(cheapest_query)
        medium_result = db_connection.execute_query(medium_query)
        premium_result = db_connection.execute_query(premium_query)
        
        return {
            "cheapest": [format_event(row) for row in cheapest_result.result_set] if cheapest_result.result_set else [],
            "medium": [format_event(row) for row in medium_result.result_set] if medium_result.result_set else [],
            "premium": [format_event(row) for row in premium_result.result_set] if premium_result.result_set else [],
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "cheapest": [], "medium": [], "premium": []}


@app.get("/scatter")
async def get_scatter_data():
    """Get price vs AI quality score data for scatter plot."""
    from src.database.connection import db_connection
    
    try:
        # Get events with AI summaries (sample for performance)
        query = """
        MATCH (e:Event)-[:HAS_AI_SUMMARY]->(s:AISummary)
        WHERE e.price > 0 AND s.quality_score IS NOT NULL
        RETURN e.price, s.quality_score, e.category
        LIMIT 500
        """
        
        result = db_connection.execute_query(query)
        
        if not result.result_set:
            return []
        
        # Format for Recharts scatter
        data = []
        for row in result.result_set:
            data.append({
                "price": float(row[0]) if row[0] else 0,
                "quality": int(row[1]) if row[1] else 0,
                "category": row[2] or "Other"
            })
        
        return data
    except Exception as e:
        import traceback
        traceback.print_exc()
        return []

@app.get("/analysis/full")
async def get_full_analysis():
    """Get comprehensive statistical analysis."""
    try:
        events = await EventNode.get_all_events()

        # Run statistical analysis (these are async methods)
        analyzer = StatisticalAnalyzer()
        stats_results = await analyzer.analyze_events(events)

        # Run anomaly detection (this is async)
        detector = AnomalyDetector()
        anomaly_results = await detector.detect_anomalies(events)

        # Format response for frontend
        return {
            "summary": {
                "total_events": int(stats_results["summary"]["total_events"]),
                "mean_price": float(round(stats_results["summary"]["price_statistics"]["mean"], 2)),
                "median_price": float(round(stats_results["summary"]["price_statistics"]["median"], 2)),
                "std_dev": float(round(stats_results["summary"]["price_statistics"]["std"], 2)),
                "min_price": float(round(stats_results["summary"]["price_statistics"]["min"], 2)),
                "max_price": float(round(stats_results["summary"]["price_statistics"]["max"], 2)),
                "total_categories": int(stats_results["summary"]["categories"]["total_categories"]),
                "total_venues": int(stats_results["summary"]["venues"]["total_venues"]),
            },
            "distribution": {
                "shape": str(stats_results["price_analysis"]["distribution_shape"]),
                "skewness": float(round(stats_results["price_analysis"]["skewness"], 3)),
                "kurtosis": float(round(stats_results["price_analysis"]["kurtosis"], 3)),
                "q1": float(round(stats_results["quartile_analysis"]["quartiles"]["q1"], 2)),
                "q3": float(round(stats_results["quartile_analysis"]["quartiles"]["q3"], 2)),
                "iqr": float(round(stats_results["quartile_analysis"]["interquartile_range"], 2)),
            },
            "anomalies": {
                "total": int(anomaly_results["summary"]["total_anomalies"]),
                "rate": float(round(anomaly_results["summary"]["anomaly_rate"], 2)),
                "price_outliers": int(anomaly_results["price_outliers"]["total_outliers"]),
            },
            "normality": {
                "is_normal": bool(stats_results["distribution_tests"]["kolmogorov_smirnov_test"].get("is_normal", False)),
                "conclusion": str(stats_results["distribution_tests"]["conclusion"])
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/analysis/categories")
async def get_category_analysis():
    """Get detailed category-wise analysis."""
    import math

    def safe_float(value, default=0.0):
        """Convert to float, handling NaN and None."""
        if value is None:
            return default
        try:
            f = float(value)
            return default if math.isnan(f) or math.isinf(f) else round(f, 2)
        except (TypeError, ValueError):
            return default

    try:
        events = await EventNode.get_all_events()
        analyzer = StatisticalAnalyzer()
        stats_results = await analyzer.analyze_events(events)

        # Format category data for charts
        category_data = []
        for cat_name, cat_stats in stats_results["category_comparison"]["category_statistics"].items():
            category_data.append({
                "name": str(cat_name),
                "count": int(cat_stats["count"]),
                "mean_price": safe_float(cat_stats.get("mean")),
                "median_price": safe_float(cat_stats.get("median")),
                "min_price": safe_float(cat_stats.get("q1")),
                "max_price": safe_float(cat_stats.get("q3")),
                "std_dev": safe_float(cat_stats.get("std"))
            })

        # Sort by count descending
        category_data.sort(key=lambda x: x["count"], reverse=True)

        return category_data
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/analysis/timeline")
async def get_timeline_analysis():
    """Get event distribution over time."""
    events = await EventNode.get_all_events()
    from collections import Counter
    import datetime

    # Group by month
    date_counts = Counter()
    for e in events:
        if e.date:
            try:
                # Parse date and get month
                if isinstance(e.date, str):
                    date_obj = datetime.datetime.fromisoformat(e.date.replace('Z', '+00:00'))
                else:
                    date_obj = e.date
                month_key = date_obj.strftime("%Y-%m")
                date_counts[month_key] += 1
            except:
                pass

    # Format for charts
    timeline = [{"month": k, "count": v} for k, v in sorted(date_counts.items())]
    return timeline[:12]  # Last 12 months


@app.get("/analysis/advanced")
async def get_advanced_analysis():
    """Get advanced statistical analysis for dashboard."""
    import datetime
    import re
    from collections import Counter, defaultdict
    
    # Turkish month mapping
    TURKISH_MONTHS = {
        'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4,
        'mayıs': 5, 'haziran': 6, 'temmuz': 7, 'ağustos': 8,
        'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
    }
    
    def parse_turkish_date(date_str):
        """Parse Turkish date like '2026 Mayıs 23' or '23 Mayıs 2026'."""
        if not date_str:
            return None
        date_str = str(date_str).lower().strip()
        
        # Try ISO format first
        try:
            return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
        
        # Try Turkish format: "2026 Mayıs 23" or "23 Mayıs 2026"
        for month_name, month_num in TURKISH_MONTHS.items():
            if month_name in date_str:
                # Extract numbers
                numbers = re.findall(r'\d+', date_str)
                if len(numbers) >= 2:
                    # Determine year and day
                    nums = [int(n) for n in numbers]
                    if nums[0] > 1000:  # "2026 Mayıs 23"
                        year, day = nums[0], nums[1] if len(nums) > 1 else 1
                    else:  # "23 Mayıs 2026"
                        day, year = nums[0], nums[1] if nums[1] > 1000 else 2026
                    try:
                        return datetime.datetime(year, month_num, day)
                    except:
                        pass
        return None
    
    try:
        events = await EventNode.get_all_events()
        
        # 1. Time series: Events by week
        week_counts = Counter()
        week_prices = defaultdict(list)
        for e in events:
            if e.date:
                date_obj = parse_turkish_date(e.date)
                if date_obj:
                    week_key = date_obj.strftime("%Y-W%W")
                    week_counts[week_key] += 1
                    if e.price and e.price > 0:
                        week_prices[week_key].append(e.price)
        
        time_series = []
        for week in sorted(week_counts.keys())[-16:]:  # Last 16 weeks
            avg_price = np.mean(week_prices[week]) if week_prices[week] else 0
            time_series.append({
                "week": week,
                "events": week_counts[week],
                "avg_price": round(avg_price, 0)
            })
        
        # 2. Day of week distribution with price
        dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        dow_counts = defaultdict(int)
        dow_prices = defaultdict(list)
        
        for e in events:
            if e.date:
                date_obj = parse_turkish_date(e.date)
                if date_obj:
                    dow = date_obj.weekday()
                    dow_counts[dow] += 1
                    if e.price and e.price > 0:
                        dow_prices[dow].append(e.price)
        
        day_of_week = []
        for i in range(7):
            avg_price = np.mean(dow_prices[i]) if dow_prices[i] else 0
            day_of_week.append({
                "day": dow_names[i],
                "events": dow_counts[i],
                "avg_price": round(avg_price, 0)
            })
        
        # 3. Price segmentation (manual clustering for simplicity)
        prices = [e.price for e in events if e.price and e.price > 0]
        if prices:
            p_arr = np.array(prices)
            segments = {
                "budget": {"range": "0-300 TL", "count": int(np.sum(p_arr <= 300)), "avg": round(float(np.mean(p_arr[p_arr <= 300])), 0) if np.sum(p_arr <= 300) > 0 else 0},
                "mid_range": {"range": "301-800 TL", "count": int(np.sum((p_arr > 300) & (p_arr <= 800))), "avg": round(float(np.mean(p_arr[(p_arr > 300) & (p_arr <= 800)])), 0) if np.sum((p_arr > 300) & (p_arr <= 800)) > 0 else 0},
                "premium": {"range": "801-2000 TL", "count": int(np.sum((p_arr > 800) & (p_arr <= 2000))), "avg": round(float(np.mean(p_arr[(p_arr > 800) & (p_arr <= 2000)])), 0) if np.sum((p_arr > 800) & (p_arr <= 2000)) > 0 else 0},
                "luxury": {"range": "2000+ TL", "count": int(np.sum(p_arr > 2000)), "avg": round(float(np.mean(p_arr[p_arr > 2000])), 0) if np.sum(p_arr > 2000) > 0 else 0},
            }
            price_segments = [
                {"name": "Budget", "value": segments["budget"]["count"], "avg": segments["budget"]["avg"], "range": segments["budget"]["range"]},
                {"name": "Mid-Range", "value": segments["mid_range"]["count"], "avg": segments["mid_range"]["avg"], "range": segments["mid_range"]["range"]},
                {"name": "Premium", "value": segments["premium"]["count"], "avg": segments["premium"]["avg"], "range": segments["premium"]["range"]},
                {"name": "Luxury", "value": segments["luxury"]["count"], "avg": segments["luxury"]["avg"], "range": segments["luxury"]["range"]},
            ]
        else:
            price_segments = []
        
        # 4. Category-Price correlation (simplified)
        category_prices = defaultdict(list)
        for e in events:
            if e.category and e.price and e.price > 0:
                category_prices[e.category].append(e.price)
        
        correlation_data = []
        for cat, prices_list in sorted(category_prices.items(), key=lambda x: -len(x[1]))[:10]:
            correlation_data.append({
                "category": cat,
                "count": len(prices_list),
                "mean": round(np.mean(prices_list), 0),
                "median": round(np.median(prices_list), 0),
                "std": round(np.std(prices_list), 0),
                "min": round(np.min(prices_list), 0),
                "max": round(np.max(prices_list), 0),
            })
        
        return {
            "time_series": time_series,
            "day_of_week": day_of_week,
            "price_segments": price_segments,
            "category_correlation": correlation_data,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.get("/progress")
async def get_progress():
    """Get live progress for monitoring scrape/enrich jobs."""
    from src.database.connection import db_connection

    try:
        # Count total events
        event_result = db_connection.execute_query("MATCH (e:Event) RETURN count(e) as count")
        total_events = event_result.result_set[0][0] if event_result.result_set else 0

        # Count AI summaries
        summary_result = db_connection.execute_query("MATCH (s:AISummary) RETURN count(s) as count")
        total_summaries = summary_result.result_set[0][0] if summary_result.result_set else 0

        # Count events with dates
        date_result = db_connection.execute_query(
            "MATCH (e:Event) WHERE e.date IS NOT NULL AND e.date <> '' RETURN count(e) as count"
        )
        events_with_dates = date_result.result_set[0][0] if date_result.result_set else 0

        # Count events with specific categories (not 'Etkinlik')
        category_result = db_connection.execute_query(
            "MATCH (e:Event) WHERE e.category IS NOT NULL AND e.category <> '' AND e.category <> 'Etkinlik' RETURN count(e) as count"
        )
        events_with_categories = category_result.result_set[0][0] if category_result.result_set else 0

        # Get latest AI summary with event info (distinct titles)
        latest_result = db_connection.execute_query(
            "MATCH (e:Event)-[:HAS_AI_SUMMARY]->(s:AISummary) RETURN DISTINCT e.title, s.quality_score, e.category ORDER BY s.updated_at DESC LIMIT 3"
        )
        latest_summaries = []
        if latest_result.result_set:
            for row in latest_result.result_set:
                title = row[0] if row[0] else "Unknown Event"
                latest_summaries.append({
                    "title": title[:50] + "..." if len(title) > 50 else title,
                    "quality_score": row[1] if row[1] else "?",
                    "category": row[2] if row[2] else "Etkinlik"
                })

        # Calculate percentages
        summary_pct = (total_summaries / total_events * 100) if total_events > 0 else 0
        date_pct = (events_with_dates / total_events * 100) if total_events > 0 else 0
        category_pct = (events_with_categories / total_events * 100) if total_events > 0 else 0

        return {
            "total_events": int(total_events),
            "total_summaries": int(total_summaries),
            "summary_percentage": round(summary_pct, 1),
            "events_with_dates": int(events_with_dates),
            "date_percentage": round(date_pct, 1),
            "events_with_categories": int(events_with_categories),
            "category_percentage": round(category_pct, 1),
            "latest_summaries": latest_summaries,
            "remaining": int(total_events - total_summaries),
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "total_events": 0, "total_summaries": 0}
