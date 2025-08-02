"""
Core functionality for the Muzik application.
"""

from .about import show_about_menu
from .application import show_application_menu
from .config import Config
from .logger import setup_logger
from .menu import Menu, MenuItem, show_main_menu, create_simple_menu, show_songs_menu
from .settings import show_settings_menu
# Import console functions from settings (temporary location)
from .settings.menu import configure_spotify_tokens, show_spotify_status
# Import new Spotify modules
from .spotify import (
    SpotifyAuth, SpotifyTracks, SpotifyAlbums, SpotifyArtists,
    SpotifyPlaylists, SpotifyClient
)
from .spotify.api.auth import validate_spotify_config
# Import legacy compatibility
from .spotify.api.client import SpotifyAPI
from .spotify.display import display_tracks_table, display_playlists_table

__all__ = [
    "Config",
    "setup_logger",
    "Menu",
    "MenuItem",
    "show_main_menu",
    "create_simple_menu",
    "show_songs_menu",
    "show_settings_menu",
    "show_application_menu",
    "show_about_menu",
    # New Spotify modules
    "SpotifyAuth",
    "SpotifyTracks",
    "SpotifyAlbums",
    "SpotifyArtists",
    "SpotifyPlaylists",
    "SpotifyClient",
    "display_tracks_table",
    "display_playlists_table",
    # Legacy compatibility
    "SpotifyAPI",
    "validate_spotify_config",
    # Console functions (temporary location in settings)
    "configure_spotify_tokens",
    "show_spotify_status",
]
