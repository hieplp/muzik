"""
Main Spotify client that combines all modules.
"""

from .albums import SpotifyAlbums
from .artists import SpotifyArtists
from .auth import SpotifyAuth
from .playlists import SpotifyPlaylists
from .tracks import SpotifyTracks
from ...config import Config


class SpotifyClient:
    """Main Spotify client that combines all functionality."""

    def __init__(self, config: Config):
        """
        Initialize Spotify client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.auth = SpotifyAuth(config)
        self.tracks = SpotifyTracks(config)
        self.albums = SpotifyAlbums(config)
        self.artists = SpotifyArtists(config)
        self.playlists = SpotifyPlaylists(config)

    def is_configured(self) -> bool:
        """
        Check if Spotify API is properly configured.
        
        Returns:
            True if configured, False otherwise
        """
        return self.auth.is_configured()

    def get_status(self) -> dict:
        """
        Get Spotify API configuration status.
        
        Returns:
            Dictionary with configuration status
        """
        return self.auth.get_status()

    def test_connection(self) -> tuple[bool, str]:
        """
        Test Spotify API connection.
        
        Returns:
            Tuple of (success, error_message)
        """
        return self.auth.test_connection()


# Legacy compatibility - maintain backward compatibility with existing code
class SpotifyAPI(SpotifyClient):
    """Legacy SpotifyAPI class for backward compatibility."""

    def __init__(self, config: Config):
        """Initialize with legacy interface."""
        super().__init__(config)
        # Add legacy method aliases
        self.search_tracks = self.tracks.search_tracks
        self.get_user_playlists = self.playlists.get_user_playlists
        self.get_playlist_tracks = self.playlists.get_playlist_tracks
        self.get_user_top_tracks = self.tracks.get_user_top_tracks
