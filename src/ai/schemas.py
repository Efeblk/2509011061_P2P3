from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class EventIntent(str, Enum):
    """User intent categories."""
    BEST_VALUE = "best-value"
    DATE_NIGHT = "date-night"
    THIS_WEEKEND = "this-weekend"
    HIDDEN_GEMS = "hidden-gems"
    SEARCH = "search"

class IntentResponse(BaseModel):
    """Structured response for intent classification."""
    intent: EventIntent = Field(..., description="The classified user intent.")
    confidence: float = Field(..., description="Confidence score between 0 and 1.")
    reasoning: str = Field(..., description="Brief explanation of why this intent was chosen.")

class DateRange(BaseModel):
    """Date range filter."""
    start: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format.")
    end: Optional[str] = Field(None, description="End date in YYYY-MM-DD format.")

class SearchFilters(BaseModel):
    """Structured search filters extracted from query."""
    max_price: Optional[float] = Field(None, description="Maximum price in TL.")
    city: Optional[str] = Field(None, description="City name (e.g., Istanbul, Ankara).")
    category: Optional[str] = Field(None, description="Event category (e.g., Jazz, Theater).")
    date_range: Optional[DateRange] = Field(None, description="Date range for the event.")
    
    class Config:
        extra = "ignore"
