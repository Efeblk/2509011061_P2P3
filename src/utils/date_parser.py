"""
Date parsing utilities for Turkish event dates.
"""

import re
from typing import List
from datetime import datetime


def parse_turkish_date_range(date_string: str) -> List[str]:
    """
    Parse Turkish date range strings and return list of individual dates.

    Examples:
        "Aralık - 10 - 16" -> ["2024 Aralık 10", "2024 Aralık 11", ..., "2024 Aralık 16"]
        "Aralık - 10 - 16 Ocak - 02 - 08" -> ["2024 Aralık 10", ..., "2025 Ocak 08"]
        "Aralık - 15" -> ["2024 Aralık 15"]
        "10 Aralık 2025" -> ["2025 Aralık 10"]

    Args:
        date_string: Turkish date string with ranges

    Returns:
        List of individual date strings with year
    """
    if not date_string or not date_string.strip():
        return [date_string]

    # Turkish month names mapping (both full and abbreviated forms)
    turkish_months = {
        # Full names
        "Ocak": 1,
        "Şubat": 2,
        "Mart": 3,
        "Nisan": 4,
        "Mayıs": 5,
        "Haziran": 6,
        "Temmuz": 7,
        "Ağustos": 8,
        "Eylül": 9,
        "Ekim": 10,
        "Kasım": 11,
        "Aralık": 12,
        # Abbreviated forms
        "Oca": 1,
        "Şub": 2,
        "Mar": 3,
        "Nis": 4,
        "May": 5,
        "Haz": 6,
        "Tem": 7,
        "Ağu": 8,
        "Eyl": 9,
        "Eki": 10,
        "Kas": 11,
        "Ara": 12,
    }

    # Map abbreviated to full month names for output consistency
    month_full_names = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
        5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
        9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
    }

    # IMPROVEMENT: Extract year from date string if present
    year = None
    year_provided = False  # Track if year was explicitly provided in input
    year_match = re.search(r'\b(20\d{2})\b', date_string)
    if year_match:
        year = int(year_match.group(1))
        year_provided = True
        # Remove the year from the string to avoid duplication
        date_string = date_string.replace(year_match.group(0), '').strip()
    else:
        # Default to current year, but account for year rollover
        current_date = datetime.now()
        year = current_date.year

    dates = []

    # Pattern: "Month - StartDay - EndDay" or "Month - Day" or "Day Month"
    # Examples: "Aralık - 10 - 16", "Ocak - 02 - 08", "Aralık - 15", "28 Kasım"
    parts = date_string.split()

    i = 0
    while i < len(parts):
        # Pattern 1: Look for "Month" followed by day(s)
        if parts[i] in turkish_months:
            month = parts[i]

            # Skip separator
            if i + 1 < len(parts) and parts[i + 1] == "-":
                i += 2
            else:
                i += 1

            # Get start day
            if i < len(parts):
                try:
                    start_day = int(parts[i])
                    i += 1

                    # Check if there's a range (another separator and end day)
                    end_day = start_day
                    if i < len(parts) and parts[i] == "-":
                        i += 1
                        if i < len(parts):
                            try:
                                end_day = int(parts[i])
                                i += 1
                            except ValueError:
                                # Not a number, backtrack
                                i -= 1

                    # Generate all dates in range with year
                    # IMPROVEMENT: Handle year rollover (e.g., Dec 2024 -> Jan 2025)
                    current_month_num = turkish_months[month]
                    month_full = month_full_names[current_month_num]  # Use full name for consistency

                    for day in range(start_day, end_day + 1):
                        # If we're parsing January-March and current real month is Nov-Dec,
                        # assume the event is next year (but only if year wasn't provided in input)
                        event_year = year
                        if not year_provided and current_month_num <= 3 and datetime.now().month >= 11:
                            event_year = year + 1

                        dates.append(f"{event_year} {month_full} {day:02d}")

                except ValueError:
                    # Not a valid day number, skip
                    pass

        # Pattern 2: Look for "Day Month" format (e.g., "28 Kasım")
        elif i + 1 < len(parts):
            try:
                day = int(parts[i])
                if parts[i + 1] in turkish_months:
                    month = parts[i + 1]
                    current_month_num = turkish_months[month]
                    month_full = month_full_names[current_month_num]

                    # Handle year rollover (but only if year wasn't provided in input)
                    event_year = year
                    if not year_provided and current_month_num <= 3 and datetime.now().month >= 11:
                        event_year = year + 1

                    dates.append(f"{event_year} {month_full} {day:02d}")
                    i += 2  # Skip both day and month
                    continue
            except ValueError:
                pass
            i += 1
        else:
            i += 1

    # If no dates were parsed, return original string
    return dates if dates else [date_string]


def extract_date_from_title(title: str) -> str:
    """
    Extract date from event title if present.

    Examples:
        "5 Aralık Konseri" -> "2024 Aralık 05"
        "19 Aralık Konseri Antalya" -> "2024 Aralık 19"
        "DenizBank Konserleri 30 Ocak" -> "2025 Ocak 30"
        "DenizBank Konserleri 8 Aralık 2025" -> "2025 Aralık 08"

    Args:
        title: Event title

    Returns:
        Extracted date string with year or empty string if not found
    """
    if not title:
        return ""

    # Turkish month names mapping (both full and abbreviated forms)
    turkish_months = {
        # Full names
        "Ocak": 1,
        "Şubat": 2,
        "Mart": 3,
        "Nisan": 4,
        "Mayıs": 5,
        "Haziran": 6,
        "Temmuz": 7,
        "Ağustos": 8,
        "Eylül": 9,
        "Ekim": 10,
        "Kasım": 11,
        "Aralık": 12,
        # Abbreviated forms
        "Oca": 1,
        "Şub": 2,
        "Mar": 3,
        "Nis": 4,
        "May": 5,
        "Haz": 6,
        "Tem": 7,
        "Ağu": 8,
        "Eyl": 9,
        "Eki": 10,
        "Kas": 11,
        "Ara": 12,
    }

    # Map month numbers to full names for output consistency
    month_full_names = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
        5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
        9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
    }

    # IMPROVEMENT: Extract year if present
    year = None
    year_match = re.search(r'\b(20\d{2})\b', title)
    if year_match:
        year = int(year_match.group(1))
    else:
        year = datetime.now().year

    # Pattern 1: "DD Month" or "D Month" (5 Aralık, 19 Aralık, 30 Ocak, 28 Şub)
    for month, month_num in turkish_months.items():
        month_full = month_full_names[month_num]  # Use full name for consistency

        # Try "number month" pattern
        pattern1 = r"(\d{1,2})\s+" + month
        match = re.search(pattern1, title, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            # Handle year rollover
            event_year = year
            if month_num <= 3 and datetime.now().month >= 11:
                event_year = year + 1
            return f"{event_year} {month_full} {day:02d}"

        # Try "month number" pattern (less common but possible)
        pattern2 = month + r"\s+(\d{1,2})"
        match = re.search(pattern2, title, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            # Handle year rollover
            event_year = year
            if month_num <= 3 and datetime.now().month >= 11:
                event_year = year + 1
            return f"{event_year} {month_full} {day:02d}"

    return ""


def normalize_date_format(date_string: str) -> str:
    """
    Normalize date format for consistency.

    Args:
        date_string: Date string to normalize

    Returns:
        Normalized date string
    """
    if not date_string:
        return date_string

    # Remove extra whitespace
    normalized = " ".join(date_string.split())

    return normalized
