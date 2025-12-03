"""
Unit tests for date parsing utilities.
"""

import pytest
from src.utils.date_parser import parse_turkish_date_range, normalize_date_format


class TestParseTurkishDateRange:
    """Test Turkish date range parsing."""

    def test_single_date(self):
        """Test parsing a single date."""
        result = parse_turkish_date_range("Aralık - 15")
        assert result == ["Aralık 15"]

    def test_date_range_single_month(self):
        """Test parsing a date range within one month."""
        result = parse_turkish_date_range("Aralık - 10 - 16")
        expected = ["Aralık 10", "Aralık 11", "Aralık 12", "Aralık 13", "Aralık 14", "Aralık 15", "Aralık 16"]
        assert result == expected

    def test_date_range_multiple_months(self):
        """Test parsing date ranges across multiple months."""
        result = parse_turkish_date_range("Aralık - 10 - 16 Ocak  - 02 - 08")
        expected = [
            "Aralık 10",
            "Aralık 11",
            "Aralık 12",
            "Aralık 13",
            "Aralık 14",
            "Aralık 15",
            "Aralık 16",
            "Ocak 02",
            "Ocak 03",
            "Ocak 04",
            "Ocak 05",
            "Ocak 06",
            "Ocak 07",
            "Ocak 08",
        ]
        assert result == expected

    def test_date_range_with_leading_zeros(self):
        """Test parsing dates with leading zeros."""
        result = parse_turkish_date_range("Ocak - 01 - 05")
        expected = ["Ocak 01", "Ocak 02", "Ocak 03", "Ocak 04", "Ocak 05"]
        assert result == expected

    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_turkish_date_range("")
        assert result == [""]

    def test_none_input(self):
        """Test parsing None input."""
        result = parse_turkish_date_range(None)
        assert result == [None]

    def test_invalid_format(self):
        """Test parsing invalid format returns original string."""
        invalid = "Some invalid date format"
        result = parse_turkish_date_range(invalid)
        assert result == [invalid]

    def test_all_turkish_months(self):
        """Test parsing works for all Turkish months."""
        months = [
            "Ocak",
            "Şubat",
            "Mart",
            "Nisan",
            "Mayıs",
            "Haziran",
            "Temmuz",
            "Ağustos",
            "Eylül",
            "Ekim",
            "Kasım",
            "Aralık",
        ]

        for month in months:
            result = parse_turkish_date_range(f"{month} - 15")
            assert result == [f"{month} 15"]

    def test_date_range_january(self):
        """Test parsing January date range."""
        result = parse_turkish_date_range("Ocak - 28 - 31")
        expected = ["Ocak 28", "Ocak 29", "Ocak 30", "Ocak 31"]
        assert result == expected

    def test_multiple_ranges(self):
        """Test parsing multiple separate date ranges."""
        result = parse_turkish_date_range("Mart - 05 - 10 Nisan - 15 - 20")
        expected = [
            "Mart 05",
            "Mart 06",
            "Mart 07",
            "Mart 08",
            "Mart 09",
            "Mart 10",
            "Nisan 15",
            "Nisan 16",
            "Nisan 17",
            "Nisan 18",
            "Nisan 19",
            "Nisan 20",
        ]
        assert result == expected


class TestNormalizeDateFormat:
    """Test date format normalization."""

    def test_remove_extra_whitespace(self):
        """Test removing extra whitespace."""
        result = normalize_date_format("Aralık   -   10")
        assert result == "Aralık - 10"

    def test_preserve_single_spaces(self):
        """Test preserving single spaces."""
        result = normalize_date_format("Aralık 10")
        assert result == "Aralık 10"

    def test_empty_string(self):
        """Test normalizing empty string."""
        result = normalize_date_format("")
        assert result == ""

    def test_none_input(self):
        """Test normalizing None input."""
        result = normalize_date_format(None)
        assert result is None

    def test_tabs_and_newlines(self):
        """Test normalizing tabs and newlines."""
        result = normalize_date_format("Aralık\t-\n10")
        assert result == "Aralık - 10"
