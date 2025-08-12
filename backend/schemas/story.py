from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel


class StoryOptionsSchema(BaseModel):
    """
    Schema for story options.
    """
    text: str
    node_id: Optional[int] = None


class StoryNodeBase(BaseModel):
    """
    Base schema for a story node.
    """
    content: str
    is_ending: bool = False
    is_winning_ending: bool = False


class CompleteStoryNodeResponse(StoryNodeBase):
    """
    Schema for a complete story node response.
    """
    id: int
    options: List[StoryOptionsSchema] = []

    class Config:
        """
        Pydantic configuration.
        """
        from_attributes = True


class StoryBase(BaseModel):
    """
    Base schema for a story.
    """
    title: str
    session_id: Optional[str] = None

    class Config:
        """
        Pydantic configuration.
        """
        from_attributes = True


class CreateStoryRequest(BaseModel):
    """
    Schema for creating a story request.
    """
    theme: str


class CompleteStoryResponse(StoryBase):
    """
    Schema for a complete story response.
    """
    id: int
    created_at: datetime
    root_node: CompleteStoryNodeResponse
    all_nodes: Dict[int, CompleteStoryNodeResponse]

    class Config:
        """
        Pydantic configuration.
        """
        from_attributes = True