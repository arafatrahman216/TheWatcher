from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, List

class WebsiteCreate(BaseModel):
    url: HttpUrl
    name: str

class WebsiteResponse(BaseModel):
    id: int
    url: str
    name: str
    created_at: datetime = Field(..., description="UTC timestamp")
    is_active: bool
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z' if v else None
        }

class UptimeCheckResponse(BaseModel):
    id: int
    website_id: int
    timestamp: datetime = Field(..., description="UTC timestamp")
    status_code: Optional[int]
    response_time: Optional[float]
    is_up: bool
    error_message: Optional[str]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z' if v else None
        }

class UptimeStatsResponse(BaseModel):
    uptime_percentage: float
    total_checks: int
    successful_checks: int
    average_response_time: Optional[float]
    last_check: Optional[datetime] = Field(None, description="UTC timestamp")
    incidents: List[UptimeCheckResponse]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z' if v else None
        }
