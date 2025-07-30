"""
Spotify playlists API operations.
"""

from typing import Any, Dict, List, Optional

from ..config import Config
from .base import BaseSpotifyAPI, SpotifyDataTransformer


class SpotifyPlaylists(BaseSpotifyAPI):
    """Handles Spotify playlist operations."""
    
    def search_playlists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for playlists on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of playlist information
        """
        return self._search_items(
            query=query,
            search_type="playlist",
            limit=limit,
            transform_func=SpotifyDataTransformer.transform_playlist
        )
    
    def get_user_playlists(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get current user's playlists.
        
        Args:
            limit: Maximum number of playlists
            offset: Offset for pagination
            
        Returns:
            List of playlist information
        """
        return self._get_paginated_items(
            endpoint="/me/playlists",
            limit=limit,
            max_limit=50,
            offset=offset,
            transform_func=SpotifyDataTransformer.transform_playlist
        )
    
    def get_playlist(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            Playlist information or None if not found
        """
        data = self._make_api_call("GET", f"/playlists/{playlist_id}", default_return=None)
        if not data:
            return None
        
        return SpotifyDataTransformer.transform_playlist(data)
    
    def get_playlist_tracks(self, playlist_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get tracks from a specific playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            limit: Maximum number of tracks
            offset: Offset for pagination
            
        Returns:
            List of track information
        """
        def transform_playlist_track(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            """Transform playlist track item."""
            track = item.get('track')
            if not track or track.get('type') != 'track':  # Skip episodes and other non-track items
                return None
            
            return {
                'id': track['id'],
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'popularity': track.get('popularity', 0),
                'external_url': track['external_urls']['spotify'],
                'preview_url': track.get('preview_url'),
                'added_at': item.get('added_at', ''),
                'added_by': item.get('added_by', {}).get('id', '') if item.get('added_by') else ''
            }
        
        data = self._make_api_call(
            "GET", 
            f"/playlists/{playlist_id}/tracks",
            params={"limit": min(limit, 100), "offset": offset},
            default_return={}
        )
        
        if not data:
            return []
        
        tracks = []
        for item in data.get('items', []):
            transformed = transform_playlist_track(item)
            if transformed:
                tracks.append(transformed)
        
        return tracks
    
    def get_featured_playlists(self, limit: int = 20, offset: int = 0, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get featured playlists.
        
        Args:
            limit: Maximum number of playlists
            offset: Offset for pagination
            country: Country code for market-specific playlists
            
        Returns:
            List of playlist information
        """
        params = {}
        if country:
            params["country"] = country
        
        data = self._make_api_call(
            "GET", 
            "/browse/featured-playlists",
            params={**params, "limit": min(limit, 50), "offset": offset},
            default_return={}
        )
        
        if not data:
            return []
        
        playlists = data.get('playlists', {}).get('items', [])
        return [SpotifyDataTransformer.transform_playlist(playlist) for playlist in playlists]
    
    def get_category_playlists(self, category_id: str, limit: int = 20, offset: int = 0, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get playlists for a specific category.
        
        Args:
            category_id: Spotify category ID
            limit: Maximum number of playlists
            offset: Offset for pagination
            country: Country code for market-specific playlists
            
        Returns:
            List of playlist information
        """
        params = {}
        if country:
            params["country"] = country
        
        data = self._make_api_call(
            "GET", 
            f"/browse/categories/{category_id}/playlists",
            params={**params, "limit": min(limit, 50), "offset": offset},
            default_return={}
        )
        
        if not data:
            return []
        
        playlists = data.get('playlists', {}).get('items', [])
        return [SpotifyDataTransformer.transform_playlist(playlist) for playlist in playlists] 