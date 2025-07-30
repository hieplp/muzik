"""
Spotify API module - handles all Spotify API operations.
"""

from .auth import SpotifyAuth
from .tracks import SpotifyTracks
from .albums import SpotifyAlbums
from .artists import SpotifyArtists
from .playlists import SpotifyPlaylists
from .client import SpotifyClient
from .base import BaseSpotifyAPI, SpotifyDataTransformer

__all__ = [
    'SpotifyAuth',
    'SpotifyTracks',
    'SpotifyAlbums', 
    'SpotifyArtists',
    'SpotifyPlaylists',
    'SpotifyClient',
    'BaseSpotifyAPI',
    'SpotifyDataTransformer'
] 