"""
Audio/Video Conversion Utilities using FFmpeg
"""
import subprocess
import json
from pathlib import Path
from typing import Optional, Tuple
from app.config import settings
from app.utils.file_manager import generate_unique_filename


def get_media_info(filepath: str) -> Optional[dict]:
    """
    Get media file information using ffprobe
    
    Returns:
        Dictionary with duration, codec info, etc.
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"Error getting media info: {e}")
        return None


def get_duration(filepath: str) -> Optional[int]:
    """Get media duration in seconds"""
    info = get_media_info(filepath)
    if info and 'format' in info:
        duration_str = info['format'].get('duration')
        if duration_str:
            return int(float(duration_str))
    return None


def convert_video_to_audio(
    input_path: str,
    output_format: str = 'mp3',
    audio_codec: str = 'libmp3lame',
    audio_bitrate: str = '192k',
    sample_rate: str = '44100'
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Convert video file to audio using FFmpeg
    
    Args:
        input_path: Path to input video file
        output_format: Output audio format (mp3, wav, etc.)
        audio_codec: Audio codec to use
        audio_bitrate: Audio bitrate
        sample_rate: Audio sample rate
    
    Returns:
        Tuple of (success, output_path, error_message)
    """
    try:
        input_file = Path(input_path)
        if not input_file.exists():
            return False, None, "Input file does not exist"
        
        # Generate output filename
        output_filename = generate_unique_filename(
            f"{input_file.stem}.{output_format}"
        )
        output_path = settings.storage_audio_path / output_filename
        
        # Ensure output directory exists
        settings.storage_audio_path.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-vn',  # No video
            '-acodec', audio_codec,
            '-ab', audio_bitrate,
            '-ar', sample_rate,
            '-y',  # Overwrite output
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, str(output_path), None
        else:
            return False, None, result.stderr
            
    except Exception as e:
        return False, None, str(e)


def extract_audio_segment(
    input_path: str,
    start_time: float,
    duration: float,
    output_format: str = 'wav'
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Extract a segment of audio from a file
    
    Args:
        input_path: Path to input file
        start_time: Start time in seconds
        duration: Duration in seconds
        output_format: Output format
    
    Returns:
        Tuple of (success, output_path, error_message)
    """
    try:
        input_file = Path(input_path)
        output_filename = generate_unique_filename(
            f"{input_file.stem}_segment.{output_format}"
        )
        output_path = settings.storage_audio_path / output_filename
        
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-ss', str(start_time),
            '-t', str(duration),
            '-acodec', 'pcm_s16le' if output_format == 'wav' else 'libmp3lame',
            '-y',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, str(output_path), None
        else:
            return False, None, result.stderr
            
    except Exception as e:
        return False, None, str(e)


def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed and accessible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False
