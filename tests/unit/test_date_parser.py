"""
Unit tests for date parsing utilities.
"""

import pytest
from unittest.mock import patch
from datetime import datetime
from src.utils.date_parser import parse_turkish_date_range, normalize_date_format


class TestParseTurkishDateRange:
    """Test Turkish date range parsing."""

    @patch('src.utils.date_parser.datetime')
    def test_single_date(self, mock_datetime):
        """Test parsing a single date."""
        mock_datetime.now.return_value = datetime(2026, 1, 7)
        result = parse_turkish_date_range("Aralık - 15")
        assert result == ["2026 Aralık 15"]

    @patch('src.utils.date_parser.datetime')
    def test_date_range_single_month(self, mock_datetime):
        """Test parsing a date range within one month."""
        mock_datetime.now.return_value = datetime(2026, 1, 7)
        result = parse_turkish_date_range("Aralık - 10 - 16")
        expected = ["2026 Aralık 10", "2026 Aralık 11", "2026 Aralık 12", "2026 Aralık 13", "2026 Aralık 14", "2026 Aralık 15", "2026 Aralık 16"]
        assert result == expected

    @patch('src.utils.date_parser.datetime')
    def test_date_range_multiple_months(self, mock_datetime):
        """Test parsing date ranges across multiple months."""
        mock_datetime.now.return_value = datetime(2026, 1, 7)
        result = parse_turkish_date_range("Aralık - 10 - 16 Ocak  - 02 - 08")
        expected = [
            "2026 Aralık 10",
            "2026 Aralık 11",
            "2026 Aralık 12",
            "2026 Aralık 13",
            "2026 Aralık 14",
            "2026 Aralık 15",
            "2026 Aralık 16",
            "2026 Ocak 02",
            "2026 Ocak 03",
            "2026 Ocak 04",
            "2026 Ocak 05",
            "2026 Ocak 06",
            "2026 Ocak 07",
            "2026 Ocak 08",
        ]
        assert result == expected

    @patch('src.utils.date_parser.datetime')
    def test_date_range_with_leading_zeros(self, mock_datetime):
        """Test parsing dates with leading zeros."""
        mock_datetime.now.return_value = datetime(2026, 1, 7)
        result = parse_turkish_date_range("Ocak - 01 - 05")
        expected = ["2026 Ocak 01", "2026 Ocak 02", "2026 Ocak 03", "2026 Ocak 04", "2026 Ocak 05"]
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

    @patch('src.utils.date_parser.datetime')
    def test_all_turkish_months(self, mock_datetime):
        """Test parsing works for all Turkish months."""
        mock_datetime.now.return_value = datetime(2026, 1, 7)
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
            assert result == [f"2026 {month} 15"]

    @patch('src.utils.date_parser.datetime')
    def test_date_range_january(self, mock_datetime):
        """Test parsing January date range."""
        mock_datetime.now.return_value = datetime(2026, 1, 7)
        result = parse_turkish_date_range("Ocak - 28 - 31")
        expected = ["2026 Ocak 28", "2026 Ocak 29", "2026 Ocak 30", "2026 Ocak 31"]
        assert result == expected

    @patch('src.utils.date_parser.datetime')
    def test_multiple_ranges(self, mock_datetime):
        """Test parsing multiple separate date ranges."""
        mock_datetime.now.return_value = datetime(2026, 1, 7)
        result = parse_turkish_date_range("Mart - 05 - 10 Nisan - 15 - 20")
        expected = [
            "2026 Mart 05",
            "2026 Mart 06",
            "2026 Mart 07",
            "2026 Mart 08",
            "2026 Mart 09",
            "2026 Mart 10",
            "2026 Nisan 15",
            "2026 Nisan 16",
            "2026 Nisan 17",
            "2026 Nisan 18",
            "2026 Nisan 19",
            "2026 Nisan 20",
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
