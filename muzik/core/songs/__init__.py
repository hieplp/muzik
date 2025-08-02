"""
Songs management functionality.
"""

from .library import show_personal_library, add_to_library, remove_from_library
from .management import create_playlist, delete_playlist, export_playlist
from .playlists import show_spotify_playlists, manage_playlists
from .search import search_spotify_tracks, search_by_title, search_by_author, search_by_singer
from ..menu import show_songs_menu

__all__ = [
    'show_songs_menu',
    'search_spotify_tracks',
    'search_by_title',
    'search_by_author',
    'search_by_singer',
    'show_spotify_playlists',
    'manage_playlists',
    'show_personal_library',
    'add_to_library',
    'remove_from_library',
    'create_playlist',
    'delete_playlist',
    'export_playlist'
]
