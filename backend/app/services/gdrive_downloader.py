"""
Google Drive Download Service
"""
import re
import os
from pathlib import Path
from typing import Optional, Tuple
from app.config import settings
from app.utils.file_manager import generate_unique_filename, get_storage_path


def extract_file_id(gdrive_link: str) -> Optional[str]:
    """
    Extract file ID from various Google Drive link formats
    
    Supported formats:
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/open?id=FILE_ID
    - https://drive.google.com/uc?id=FILE_ID
    """
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'[?&]id=([a-zA-Z0-9_-]+)',
        r'/folders/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, gdrive_link)
        if match:
            return match.group(1)
    
    return None


async def download_from_gdrive(
    gdrive_link: str,
    destination_folder: Optional[Path] = None
) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Download a file from Google Drive using service account
    
    Args:
        gdrive_link: Google Drive shareable link
        destination_folder: Optional custom destination folder
    
    Returns:
        Tuple of (success, file_info, error_message)
        file_info contains: filename, filepath, file_size, file_type
    """
    try:
        # Check if service account is configured
        service_account_file = settings.google_service_account_file
        if not service_account_file or not Path(service_account_file).exists():
            return False, None, "Google Drive service account not configured"
        
        # Extract file ID
        file_id = extract_file_id(gdrive_link)
        if not file_id:
            return False, None, "Could not extract file ID from link"
        
        # Import Google API client
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaIoBaseDownload
            import io
        except ImportError:
            return False, None, "Google API client not installed"
        
        # Authenticate with service account
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        # Build Drive service
        service = build('drive', 'v3', credentials=credentials)
        
        # Get file metadata
        file_metadata = service.files().get(
            fileId=file_id,
            fields='name,mimeType,size'
        ).execute()
        
        original_filename = file_metadata.get('name', f'gdrive_{file_id}')
        file_size = int(file_metadata.get('size', 0))
        mime_type = file_metadata.get('mimeType', '')
        
        # Determine file type
        file_ext = Path(original_filename).suffix.lower()
        if file_ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
            file_type = file_ext.lstrip('.')
        elif file_ext in ['.mp3', '.wav', '.m4a', '.flac']:
            file_type = file_ext.lstrip('.')
        else:
            # Try to guess from mime type
            if 'video' in mime_type:
                file_type = 'mp4'
            elif 'audio' in mime_type:
                file_type = 'mp3'
            else:
                file_type = 'mp4'  # Default to video
        
        # Generate unique filename
        unique_filename = generate_unique_filename(original_filename)
        
        # Determine storage path
        if destination_folder is None:
            destination_folder = get_storage_path(file_type)
        
        destination_folder.mkdir(parents=True, exist_ok=True)
        filepath = destination_folder / unique_filename
        
        # Download file
        request = service.files().get_media(fileId=file_id)
        
        with open(filepath, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        
        return True, {
            'filename': unique_filename,
            'original_filename': original_filename,
            'filepath': str(filepath),
            'file_size': file_size,
            'file_type': file_type,
            'gdrive_link': gdrive_link
        }, None
        
    except Exception as e:
        return False, None, str(e)


def validate_gdrive_link(link: str) -> bool:
    """Validate if the link is a valid Google Drive link"""
    return bool(extract_file_id(link))
