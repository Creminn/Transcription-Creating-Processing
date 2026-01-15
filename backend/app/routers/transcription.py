"""
Transcription API Router - Handles transcription generation and management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.database import get_db
from app.models.transcription import Transcription, TranscriptionSource
from app.models.media import Media
from app.schemas.transcription import (
    TranscriptionResponse, TranscriptionListResponse,
    TranscriptionPaste, TranscriptionGenerateRequest
)
from app.services.transcription.transcription_service import (
    transcribe, transcribe_parallel, get_available_models
)

router = APIRouter()


@router.get("", response_model=TranscriptionListResponse)
async def list_transcriptions(
    source: Optional[str] = Query(None, description="Filter by source (model, pasted)"),
    media_id: Optional[int] = Query(None, description="Filter by media ID"),
    search: Optional[str] = Query(None, description="Search in title or content"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all transcriptions with optional filtering"""
    query = select(Transcription)
    
    # Apply filters
    if source:
        try:
            source_type = TranscriptionSource(source)
            query = query.where(Transcription.source_type == source_type)
        except ValueError:
            pass
    
    if media_id:
        query = query.where(Transcription.media_id == media_id)
    
    if search:
        query = query.where(
            (Transcription.title.ilike(f"%{search}%")) |
            (Transcription.content.ilike(f"%{search}%"))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Transcription.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    transcriptions = result.scalars().all()
    
    return TranscriptionListResponse(
        transcriptions=[TranscriptionResponse.model_validate(t) for t in transcriptions],
        total=total
    )


@router.get("/models")
async def get_transcription_models():
    """Get available transcription models"""
    return {"models": get_available_models()}


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific transcription by ID"""
    result = await db.execute(
        select(Transcription).where(Transcription.id == transcription_id)
    )
    transcription = result.scalar_one_or_none()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return TranscriptionResponse.model_validate(transcription)


@router.post("/generate", response_model=List[TranscriptionResponse])
async def generate_transcriptions(
    request: TranscriptionGenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Generate transcriptions for selected media files"""
    if not request.media_ids:
        raise HTTPException(status_code=400, detail="No media IDs provided")
    
    # Get media files
    result = await db.execute(
        select(Media).where(Media.id.in_(request.media_ids))
    )
    media_items = result.scalars().all()
    
    if not media_items:
        raise HTTPException(status_code=404, detail="No media files found")
    
    # Get file paths
    audio_paths = [m.filepath for m in media_items]
    
    # Run transcription
    results = await transcribe_parallel(
        audio_paths,
        model=request.model,
        language=request.language,
        prioritize_audio=True
    )
    
    # Create transcription records
    transcriptions = []
    media_by_path = {m.filepath: m for m in media_items}
    
    for result_item in results:
        if result_item['success']:
            media = media_by_path.get(result_item['path'])
            if media:
                # Count words
                word_count = len(result_item['text'].split()) if result_item['text'] else 0
                
                transcription = Transcription(
                    media_id=media.id,
                    title=f"Transcription of {media.original_filename}",
                    content=result_item['text'],
                    model_used=request.model,
                    source_type=TranscriptionSource.MODEL,
                    language=request.language,
                    duration_seconds=media.duration,
                    word_count=word_count
                )
                db.add(transcription)
                transcriptions.append(transcription)
                
                # Mark media as processed
                media.is_processed = True
    
    await db.commit()
    
    # Refresh to get IDs
    for t in transcriptions:
        await db.refresh(t)
    
    return [TranscriptionResponse.model_validate(t) for t in transcriptions]


@router.post("/paste", response_model=TranscriptionResponse)
async def paste_transcription(
    request: TranscriptionPaste,
    db: AsyncSession = Depends(get_db)
):
    """Create a transcription from pasted text"""
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Transcription content cannot be empty")
    
    # Count words
    word_count = len(request.content.split())
    
    transcription = Transcription(
        title=request.title,
        content=request.content,
        source_type=TranscriptionSource.PASTED,
        language=request.language,
        word_count=word_count
    )
    
    db.add(transcription)
    await db.commit()
    await db.refresh(transcription)
    
    return TranscriptionResponse.model_validate(transcription)


@router.delete("/{transcription_id}")
async def delete_transcription(
    transcription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a transcription"""
    result = await db.execute(
        select(Transcription).where(Transcription.id == transcription_id)
    )
    transcription = result.scalar_one_or_none()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    await db.delete(transcription)
    await db.commit()
    
    return {"message": "Transcription deleted successfully"}


@router.delete("/batch")
async def delete_multiple_transcriptions(
    ids: List[int] = Query(..., description="List of transcription IDs to delete"),
    db: AsyncSession = Depends(get_db)
):
    """Delete multiple transcriptions"""
    result = await db.execute(
        select(Transcription).where(Transcription.id.in_(ids))
    )
    transcriptions = result.scalars().all()
    
    deleted_count = 0
    for t in transcriptions:
        await db.delete(t)
        deleted_count += 1
    
    await db.commit()
    
    return {"message": f"Deleted {deleted_count} transcriptions"}
