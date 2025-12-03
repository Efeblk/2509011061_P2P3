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
        "Aralık - 10 - 16" -> ["Aralık 10", "Aralık 11", ..., "Aralık 16"]
        "Aralık - 10 - 16 Ocak - 02 - 08" -> ["Aralık 10", ..., "Aralık 16", "Ocak 02", ..., "Ocak 08"]
        "Aralık - 15" -> ["Aralık 15"]

    Args:
        date_string: Turkish date string with ranges

    Returns:
        List of individual date strings
    """
    if not date_string or not date_string.strip():
        return [date_string]

    # Turkish month names mapping
    turkish_months = {
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
    }

    dates = []

    # Pattern: "Month - StartDay - EndDay" or "Month - Day"
    # Examples: "Aralık - 10 - 16", "Ocak - 02 - 08", "Aralık - 15"
    parts = date_string.split()

    i = 0
    while i < len(parts):
        # Look for month name
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

                    # Generate all dates in range
                    for day in range(start_day, end_day + 1):
                        dates.append(f"{month} {day:02d}")

                except ValueError:
                    # Not a valid day number, skip
                    pass
        else:
            i += 1

    # If no dates were parsed, return original string
    return dates if dates else [date_string]


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
