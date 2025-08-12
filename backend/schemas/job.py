from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class StoryJobBase(BaseModel):
    """
    Base schema for a story job.
    """
    theme: str


class StoryJobResponse(BaseModel):
    """
    Schema for a story job response.
    """
    job_id: str
    status: str
    created_at: datetime
    story_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        """
        Pydantic configuration.
        """
        from_attributes = True


class StoryJobCreate(StoryJobBase):
    """
    Schema for creating a story job.
    """
    pass