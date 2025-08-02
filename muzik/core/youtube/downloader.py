"""
YouTube audio downloader using yt-dlp.
"""

import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import yt_dlp

    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False


class YoutubeDownloader:
    """Handles YouTube audio downloading and streaming."""

    def __init__(self):
        """Initialize the YouTube downloader."""
        self.temp_dir = Path(tempfile.gettempdir()) / "muzik_streams"
        self.temp_dir.mkdir(exist_ok=True)

    def search_and_download(self, track_name: str, artists: str) -> Optional[str]:
        """
        Search YouTube for a track and download audio to temporary file.
        
        Args:
            track_name: Name of the track
            artists: Artist names
            
        Returns:
            Path to downloaded audio file or None if failed
        """
        if not YTDLP_AVAILABLE:
            return None

        try:
            # Create search query
            search_query = f"{track_name} {artists}"

            # Generate temp filename
            safe_filename = "".join(
                c for c in f"{track_name}_{artists}" if c.isalnum() or c in (' ', '-', '_')).rstrip()
            temp_file = self.temp_dir / f"{safe_filename}.%(ext)s"

            # Configure yt-dlp options for downloading
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
                'outtmpl': str(temp_file),
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'default_search': 'ytsearch1:',  # Search YouTube, get first result
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',  # Convert to WAV for pygame compatibility
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search and download
                search_results = ydl.extract_info(search_query, download=True)

                if search_results and 'entries' in search_results and search_results['entries']:
                    video_info = search_results['entries'][0]
                    if video_info:
                        # Find the downloaded file
                        expected_file = self.temp_dir / f"{safe_filename}.wav"
                        if expected_file.exists():
                            return str(expected_file)

                        # Try other possible extensions
                        for ext in ['.m4a', '.webm', '.mp3', '.ogg']:
                            alt_file = self.temp_dir / f"{safe_filename}{ext}"
                            if alt_file.exists():
                                return str(alt_file)

        except Exception as e:
            print(f"Download error: {e}")

        return None

    def get_video_info(self, track_name: str, artists: str) -> Optional[Dict[str, Any]]:
        """
        Get video information without downloading.
        
        Args:
            track_name: Name of the track
            artists: Artist names
            
        Returns:
            Video information dictionary or None if failed
        """
        if not YTDLP_AVAILABLE:
            return None

        try:
            search_query = f"{track_name} {artists}"

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'default_search': 'ytsearch1:',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(search_query, download=False)

                if search_results and 'entries' in search_results and search_results['entries']:
                    return search_results['entries'][0]

        except Exception:
            pass

        return None

    def cleanup_temp_files(self):
        """Clean up temporary downloaded files."""
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
        except Exception:
            pass

    def __del__(self):
        """Cleanup on object destruction."""
        self.cleanup_temp_files()
