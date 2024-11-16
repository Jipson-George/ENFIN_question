
from sqlalchemy import  Column, Integer, String, DateTime, ForeignKey, Time
from sqlalchemy.orm import  relationship
from datetime import time
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    timezone = Column(String)
    name = Column(String)
    weekly_availability = relationship("WeeklyAvailability", back_populates="user")
    specific_availability = relationship("SpecificAvailability", back_populates="user")
    scheduled_events = relationship("ScheduledEvent", back_populates="user")

class WeeklyAvailability(Base):
    __tablename__ = "weekly_availability"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_of_week = Column(Integer)  # 0-6 for Monday-Sunday
    start_time = Column(Time)
    end_time = Column(Time)
    user = relationship("User", back_populates="weekly_availability")

class SpecificAvailability(Base):
    __tablename__ = "specific_availability"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    start_time = Column(Time)
    end_time = Column(Time)
    user = relationship("User", back_populates="specific_availability")

class ScheduledEvent(Base):
    __tablename__ = "scheduled_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    user = relationship("User", back_populates="scheduled_events")