from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import Depends, FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.availability_schema import (
    AvailabilityRequest,
    AvailabilityResponse,
    WeeklyAvailabilityBase,
    SpecificAvailabilityBase,
    ScheduledEventBase
)
from app.models import user_schedule
from database import get_db
from sqlalchemy.orm import Session
import pytz
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_timezone(timezone: str) -> bool:
    """Validate if the provided timezone is valid"""
    try:
        pytz.timezone(timezone)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False

def validate_date_format(date_str: str) -> bool:
    """Validate if the date string matches the required format"""
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}

@app.post("/api/available-slots", response_model=AvailabilityResponse)
async def get_available_slots(request: AvailabilityRequest, db: Session = Depends(get_db)):
    try:
        if not request.user_ids:
            raise HTTPException(status_code=400, detail="User IDs list cannot be empty")
            
        if not validate_date_format(request.start_date):
            raise HTTPException(
                status_code=400, 
                detail="Invalid start_date format. Use DD-MM-YYYY format"
            )
            
        if not validate_date_format(request.end_date):
            raise HTTPException(
                status_code=400, 
                detail="Invalid end_date format. Use DD-MM-YYYY format"
            )    
        if not validate_timezone(request.timezone):
            raise HTTPException(
                status_code=400,
                detail="Invalid timezone provided"
            )
        start_date = datetime.strptime(request.start_date, '%d-%m-%Y')
        end_date = datetime.strptime(request.end_date, '%d-%m-%Y')
        target_tz = pytz.timezone(request.timezone)
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if (end_date - start_date).days > 31:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 31 days")
        
        if start_date < datetime.now() - timedelta(days=1):
            raise HTTPException(status_code=400, detail="Start date cannot be in the past")
        try:
            users = db.query(user_schedule.User).filter(
                user_schedule.User.id.in_(request.user_ids)
            ).all()
            
            if not users:
                raise HTTPException(status_code=404, detail="No users found")
                
            if len(users) != len(request.user_ids):
                found_ids = {user.id for user in users}
                missing_ids = [uid for uid in request.user_ids if uid not in found_ids]
                raise HTTPException(
                    status_code=400,
                    detail=f"Users not found: {missing_ids}"
                )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error while fetching users: {str(e)}"
            )
        available_slots: Dict[str, List[str]] = {}
        current_date = start_date
        while current_date <= end_date:
            day_slots = find_common_slots(current_date, users, target_tz, db)
            if day_slots:
                date_key = current_date.strftime('%d-%m-%Y')
                available_slots[date_key] = day_slots
            current_date += timedelta(days=1)

        if not available_slots:
            return {"slots": {}, "message": "No common available slots found"}

        return {"slots": available_slots}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

def find_common_slots(
    date: datetime,
    users: List[user_schedule.User],
    target_tz: pytz.timezone,
    db: Session
) -> List[str]:
    """Find common available time slots for all users on a specific date"""
    try:
        SLOT_DURATION = 30
        all_user_slots = []
        
        for user in users:
            try:
                user_tz = pytz.timezone(user.timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid timezone for user {user.id}: {user.timezone}"
                )
                
            user_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            try:
                weekly_slots = get_weekly_availability(user.id, user_date.weekday(), db)
                specific_slots = get_specific_availability(user.id, user_date, db)
                events = get_scheduled_events(user.id, user_date, db)
            except SQLAlchemyError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error while fetching schedule for user {user.id}: {str(e)}"
                )
            
            available_slots = []
            base_slots = specific_slots if specific_slots else weekly_slots
            
            if not base_slots:
                continue  
                
            for slot in base_slots:
                try:
                    slot_start = datetime.combine(user_date, slot.start_time)
                    slot_end = datetime.combine(user_date, slot.end_time)
                    if slot_start >= slot_end:
                        continue 
                    slot_start = user_tz.localize(slot_start)
                    slot_end = user_tz.localize(slot_end)
                    
                    slot_start = slot_start.astimezone(target_tz)
                    slot_end = slot_end.astimezone(target_tz)
                    current = slot_start
                    while current + timedelta(minutes=SLOT_DURATION) <= slot_end:
                        slot_interval = (
                            current,
                            current + timedelta(minutes=SLOT_DURATION)
                        )
                        available_slots.append(slot_interval)
                        current += timedelta(minutes=SLOT_DURATION)
                except Exception as e:
                    continue  
            for event in events:
                try:
                    event_start = user_tz.localize(event.start_datetime).astimezone(target_tz)
                    event_end = user_tz.localize(event.end_datetime).astimezone(target_tz)
                    
                    available_slots = [
                        slot for slot in available_slots
                        if not (slot[0] < event_end and event_start < slot[1])
                    ]
                except Exception as e:
                    continue 
            
            all_user_slots.append(set((slot[0], slot[1]) for slot in available_slots))
        if not all_user_slots:
            return []
        common_slots = all_user_slots[0]
        for user_slots in all_user_slots[1:]:
            common_slots &= user_slots
        formatted_slots = [
            f"{slot[0].strftime('%I:%M%p').lstrip('0').lower()}-{slot[1].strftime('%I:%M%p').lstrip('0').lower()}"
            for slot in sorted(common_slots)
        ]
        
        return formatted_slots

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding common slots: {str(e)}"
        )

def get_weekly_availability(
    user_id: int,
    day_of_week: int,
    db: Session
) -> List[user_schedule.WeeklyAvailability]:
    """Get weekly availability for a user on a specific day"""
    try:
        if not (0 <= day_of_week <= 6):
            raise ValueError("Invalid day of week")
            
        return db.query(user_schedule.WeeklyAvailability).filter(
            user_schedule.WeeklyAvailability.user_id == user_id,
            user_schedule.WeeklyAvailability.day_of_week == day_of_week
        ).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching weekly availability: {str(e)}"
        )

def get_specific_availability(
    user_id: int,
    date: datetime,
    db: Session
) -> List[user_schedule.SpecificAvailability]:
    """Get specific availability for a user on a specific date"""
    try:
        return db.query(user_schedule.SpecificAvailability).filter(
            user_schedule.SpecificAvailability.user_id == user_id,
            user_schedule.SpecificAvailability.date == date
        ).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching specific availability: {str(e)}"
        )

def get_scheduled_events(
    user_id: int,
    date: datetime,
    db: Session
) -> List[user_schedule.ScheduledEvent]:
    """Get scheduled events for a user on a specific date"""
    try:
        next_date = date + timedelta(days=1)
        return db.query(user_schedule.ScheduledEvent).filter(
            user_schedule.ScheduledEvent.user_id == user_id,
            user_schedule.ScheduledEvent.start_datetime >= date,
            user_schedule.ScheduledEvent.start_datetime < next_date
        ).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching scheduled events: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)