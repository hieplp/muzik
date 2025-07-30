"""
Spotify API integration modules.
"""

# Import from API subdirectory
from .api import (
    SpotifyAuth,
    SpotifyTracks,
    SpotifyAlbums,
    SpotifyArtists,
    SpotifyPlaylists,
    SpotifyClient,
    BaseSpotifyAPI,
    SpotifyDataTransformer
)

# Import from display subdirectory
from .display import (
    display_tracks_table,
    display_playlists_table,
    display_track_details,
    display_playlist_details,
    display_album_details,
    display_artist_details,
    SpotifyStreamer
)

__all__ = [
    # API classes
    'SpotifyAuth',
    'SpotifyTracks', 
    'SpotifyAlbums',
    'SpotifyArtists',
    'SpotifyPlaylists',
    'SpotifyClient',
    'BaseSpotifyAPI',
    'SpotifyDataTransformer',
    # Display functions
    'display_tracks_table',
    'display_playlists_table',
    'display_track_details',
    'display_playlist_details',
    'display_album_details',
    'display_artist_details',
    'SpotifyStreamer'
] 