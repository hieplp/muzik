"""
Spotify display module - handles all Spotify-related display and UI operations.
"""

from .details import (
    display_track_details,
    display_playlist_details,
    display_album_details,
    display_artist_details
)
from .streaming import SpotifyStreamer
from .tables import display_tracks_table, display_playlists_table

__all__ = [
    'display_tracks_table',
    'display_playlists_table',
    'display_track_details',
    'display_playlist_details',
    'display_album_details',
    'display_artist_details',
    'SpotifyStreamer'
]
