"""
Media API Router - Handles file uploads, downloads, and management
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.database import get_db
from app.models.media import Media, MediaType, MediaSource
from app.schemas.media import (
    MediaResponse, MediaListResponse, MediaUpdate,
    GDriveDownloadRequest
)
from app.utils.file_manager import (
    save_upload_file, delete_file, validate_file_extension,
    get_file_type, is_video, is_audio
)
from app.utils.audio_converter import (
    get_duration, convert_video_to_audio, check_ffmpeg_installed
)
from app.services.gdrive_downloader import download_from_gdrive, validate_gdrive_link

router = APIRouter()


@router.get("", response_model=MediaListResponse)
async def list_media(
    type: Optional[str] = Query(None, description="Filter by file type (mp4, mp3, etc.)"),
    source: Optional[str] = Query(None, description="Filter by source (upload, gdrive, converted)"),
    processed: Optional[bool] = Query(None, description="Filter by processed status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all media files with optional filtering"""
    query = select(Media)
    
    # Apply filters
    if type:
        try:
            media_type = MediaType(type)
            query = query.where(Media.file_type == media_type)
        except ValueError:
            pass  # Invalid type, ignore filter
    
    if source:
        try:
            media_source = MediaSource(source)
            query = query.where(Media.source == media_source)
        except ValueError:
            pass
    
    if processed is not None:
        query = query.where(Media.is_processed == processed)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Media.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    media_items = result.scalars().all()
    
    return MediaListResponse(
        media=[MediaResponse.model_validate(m) for m in media_items],
        total=total
    )


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific media file by ID"""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return MediaResponse.model_validate(media)


@router.post("/upload", response_model=MediaResponse)
async def upload_media(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a media file (MP4, MP3, WAV, M4A, etc.)"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: MP4, MOV, AVI, MKV, WEBM, MP3, WAV, M4A, FLAC, OGG"
        )
    
    # Save file
    try:
        unique_filename, filepath, file_size = await save_upload_file(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get duration if possible
    duration = get_duration(filepath)
    
    # Determine file type
    file_type = get_file_type(file.filename)
    
    # Create database record
    media = Media(
        filename=unique_filename,
        original_filename=file.filename,
        filepath=filepath,
        file_type=MediaType(file_type) if file_type in [e.value for e in MediaType] else MediaType.MP4,
        source=MediaSource.UPLOAD,
        file_size=file_size,
        duration=duration
    )
    
    db.add(media)
    await db.commit()
    await db.refresh(media)
    
    return MediaResponse.model_validate(media)


@router.post("/gdrive", response_model=MediaResponse)
async def download_from_google_drive(
    request: GDriveDownloadRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Download a media file from Google Drive"""
    # Validate link format
    if not validate_gdrive_link(request.link):
        raise HTTPException(status_code=400, detail="Invalid Google Drive link format")
    
    # Download file
    success, file_info, error = await download_from_gdrive(request.link)
    
    if not success:
        raise HTTPException(status_code=400, detail=error or "Failed to download from Google Drive")
    
    # Get duration
    duration = get_duration(file_info['filepath'])
    
    # Create database record
    file_type = file_info['file_type']
    media = Media(
        filename=file_info['filename'],
        original_filename=file_info['original_filename'],
        filepath=file_info['filepath'],
        file_type=MediaType(file_type) if file_type in [e.value for e in MediaType] else MediaType.MP4,
        source=MediaSource.GDRIVE,
        file_size=file_info['file_size'],
        duration=duration,
        gdrive_link=file_info['gdrive_link']
    )
    
    db.add(media)
    await db.commit()
    await db.refresh(media)
    
    return MediaResponse.model_validate(media)


@router.post("/convert/{media_id}", response_model=MediaResponse)
async def convert_media_to_audio(
    media_id: int,
    format: str = Query("mp3", description="Target audio format"),
    db: AsyncSession = Depends(get_db)
):
    """Convert a video file to audio (MP3)"""
    # Check FFmpeg
    if not check_ffmpeg_installed():
        raise HTTPException(status_code=500, detail="FFmpeg is not installed")
    
    # Get source media
    result = await db.execute(select(Media).where(Media.id == media_id))
    source_media = result.scalar_one_or_none()
    
    if not source_media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if not is_video(source_media.filepath):
        raise HTTPException(status_code=400, detail="Source file is not a video")
    
    # Convert
    success, output_path, error = convert_video_to_audio(
        source_media.filepath,
        output_format=format
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=error or "Conversion failed")
    
    # Get new file info
    import os
    file_size = os.path.getsize(output_path) if output_path else 0
    duration = get_duration(output_path) if output_path else None
    
    # Create new media record for converted file
    from pathlib import Path
    output_filename = Path(output_path).name if output_path else "converted.mp3"
    
    new_media = Media(
        filename=output_filename,
        original_filename=f"{source_media.original_filename}.{format}",
        filepath=output_path,
        file_type=MediaType(format) if format in [e.value for e in MediaType] else MediaType.MP3,
        source=MediaSource.CONVERTED,
        file_size=file_size,
        duration=duration
    )
    
    db.add(new_media)
    await db.commit()
    await db.refresh(new_media)
    
    return MediaResponse.model_validate(new_media)


@router.patch("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: int,
    update: MediaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update media metadata"""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Update fields
    if update.is_processed is not None:
        media.is_processed = update.is_processed
    
    await db.commit()
    await db.refresh(media)
    
    return MediaResponse.model_validate(media)


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a media file"""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Delete physical file
    await delete_file(media.filepath)
    
    # Delete database record
    await db.delete(media)
    await db.commit()
    
    return {"message": "Media deleted successfully"}


@router.delete("/batch")
async def delete_multiple_media(
    ids: List[int] = Query(..., description="List of media IDs to delete"),
    db: AsyncSession = Depends(get_db)
):
    """Delete multiple media files"""
    result = await db.execute(select(Media).where(Media.id.in_(ids)))
    media_items = result.scalars().all()
    
    deleted_count = 0
    for media in media_items:
        await delete_file(media.filepath)
        await db.delete(media)
        deleted_count += 1
    
    await db.commit()
    
    return {"message": f"Deleted {deleted_count} media files"}
