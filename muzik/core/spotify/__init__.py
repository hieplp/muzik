"""
Spotify API integration modules.
"""

from .auth import SpotifyAuth
from .tracks import SpotifyTracks
from .albums import SpotifyAlbums
from .artists import SpotifyArtists
from .playlists import SpotifyPlaylists
from .client import SpotifyClient
from .display import display_tracks_table, display_playlists_table

__all__ = [
    'SpotifyAuth',
    'SpotifyTracks', 
    'SpotifyAlbums',
    'SpotifyArtists',
    'SpotifyPlaylists',
    'SpotifyClient',
    'display_tracks_table',
    'display_playlists_table'
] 