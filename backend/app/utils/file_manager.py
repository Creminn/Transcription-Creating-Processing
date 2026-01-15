"""
File Management Utilities
"""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
from app.config import settings


ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
ALLOWED_EXTENSIONS = ALLOWED_VIDEO_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    return Path(filename).suffix.lower()


def get_file_type(filename: str) -> str:
    """Determine file type from extension"""
    ext = get_file_extension(filename)
    if ext in ALLOWED_VIDEO_EXTENSIONS:
        return ext.lstrip('.')
    elif ext in ALLOWED_AUDIO_EXTENSIONS:
        return ext.lstrip('.')
    return 'unknown'


def is_video(filename: str) -> bool:
    """Check if file is a video"""
    return get_file_extension(filename) in ALLOWED_VIDEO_EXTENSIONS


def is_audio(filename: str) -> bool:
    """Check if file is an audio file"""
    return get_file_extension(filename) in ALLOWED_AUDIO_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving extension"""
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    safe_name = Path(original_filename).stem[:50]  # Limit base name length
    # Remove special characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in '-_')
    return f"{safe_name}_{unique_id}{ext}"


def get_storage_path(file_type: str) -> Path:
    """Get storage path based on file type"""
    if file_type in ['mp4', 'mov', 'avi', 'mkv', 'webm']:
        return settings.storage_videos_path
    return settings.storage_audio_path


async def save_upload_file(
    upload_file: UploadFile,
    destination_folder: Optional[Path] = None
) -> Tuple[str, str, int]:
    """
    Save an uploaded file to storage
    
    Returns:
        Tuple of (unique_filename, filepath, file_size)
    """
    original_filename = upload_file.filename or "unnamed_file"
    unique_filename = generate_unique_filename(original_filename)
    file_type = get_file_type(original_filename)
    
    if destination_folder is None:
        destination_folder = get_storage_path(file_type)
    
    # Ensure directory exists
    destination_folder.mkdir(parents=True, exist_ok=True)
    
    filepath = destination_folder / unique_filename
    
    # Save file
    file_size = 0
    async with aiofiles.open(filepath, 'wb') as f:
        while content := await upload_file.read(1024 * 1024):  # 1MB chunks
            file_size += len(content)
            await f.write(content)
    
    return unique_filename, str(filepath), file_size


async def delete_file(filepath: str) -> bool:
    """Delete a file from storage"""
    try:
        path = Path(filepath)
        if path.exists():
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def validate_file_extension(filename: str) -> bool:
    """Validate if file has an allowed extension"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """Validate if file size is within limits"""
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    return file_size <= max_size_bytes
