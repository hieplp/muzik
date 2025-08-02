"""
Spotify API module - handles all Spotify API operations.
"""

from .albums import SpotifyAlbums
from .artists import SpotifyArtists
from .auth import SpotifyAuth
from .base import BaseSpotifyAPI, SpotifyDataTransformer
from .client import SpotifyClient
from .playlists import SpotifyPlaylists
from .tracks import SpotifyTracks

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
