from pydantic import BaseModel
from datetime import datetime, time
from typing import Dict, List, Optional

class AvailabilityRequest(BaseModel):
    user_ids: List[int]
    start_date: str  # Format: dd-mm-yyyy
    end_date: str    # Format: dd-mm-yyyy
    timezone: str

class AvailabilityResponse(BaseModel):
    slots: Dict[str, List[str]]

class WeeklyAvailabilityBase(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time

class SpecificAvailabilityBase(BaseModel):
    date: datetime
    start_time: time
    end_time: time

class ScheduledEventBase(BaseModel):
    start_datetime: datetime
    end_datetime: datetime

    class Config:
        from_attributes = True
