import uuid
from typing import Optional
from datetime import datetime
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Cookie,
    Response,
    BackgroundTasks
)
from sqlalchemy.orm import Session

from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryResponse,
    CompleteStoryNodeResponse,
    CreateStoryRequest
)
from backend.schemas.job import StoryJobResponse

router = APIRouter(
    prefix='/stories',
    tags=['stories'],
)


def get_session_id(session_id: Optional[str] = Cookie(None)):
    """
    Get session ID from cookies.
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@router.post('/create', response_model=StoryJobResponse)
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Create a new story and return the job response.
    """
    response.set_cookie(key='session_id', value=session_id, httponly=True)

    job_id = str(uuid.uuid4())
    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status='pending',
    )
    db.add(job)
    db.commit()

    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )

    return job


def generate_story_task(
    job_id: str,
    theme: str,
    session_id: str
):
    """
    Generate tasks for creating a story based on the theme.
    """
    db = SessionLocal()

    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

        if not job:
            return

        try:
            job.status = 'processing'
            db.commit()

            story = {}  # Placeholder for story generation logic

            job.story_id = 1  # Placeholder for generated story ID
            job.status = 'completed'
            job.completed_at = datetime.now()
            db.commit()
        except Exception as e:
            job.status = 'failed'
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()

    finally:
        db.close()


@router.get('/{story_id}/complete', response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    """
    Get the complete story by its ID.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    complete_story = build_complete_story_tree(db, story)
    return complete_story


def build_complete_story_tree(
        db: Session,
        story: Story
    ) -> CompleteStoryResponse:
    """
    Build a complete story tree from the story object.
    """
    pass