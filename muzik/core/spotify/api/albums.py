"""
Spotify albums API operations.
"""

from typing import Any, Dict, List, Optional

from ...config import Config
from .base import BaseSpotifyAPI, SpotifyDataTransformer


class SpotifyAlbums(BaseSpotifyAPI):
    """Handles Spotify album operations."""
    
    def search_albums(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for albums on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of album information
        """
        return self._search_items(
            query=query,
            search_type="album",
            limit=limit,
            transform_func=SpotifyDataTransformer.transform_album
        )
    
    def get_album(self, album_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific album.
        
        Args:
            album_id: Spotify album ID
            
        Returns:
            Album information or None if not found
        """
        data = self._make_api_call("GET", f"/albums/{album_id}", default_return=None)
        if not data:
            return None
        
        album_info = SpotifyDataTransformer.transform_album(data)
        
        # Add track information for detailed album view
        album_info['tracks'] = []
        for track in data.get('tracks', {}).get('items', []):
            track_info = {
                'id': track['id'],
                'name': track['name'],
                'duration_ms': track['duration_ms'],
                'track_number': track.get('track_number', 1),
                'disc_number': track.get('disc_number', 1),
                'explicit': track.get('explicit', False)
            }
            album_info['tracks'].append(track_info)
        
        return album_info
    
    def get_album_tracks(self, album_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get tracks from a specific album.
        
        Args:
            album_id: Spotify album ID
            limit: Maximum number of tracks
            offset: Offset for pagination
            
        Returns:
            List of track information
        """
        def transform_album_track(track: Dict[str, Any]) -> Dict[str, Any]:
            """Transform album track data."""
            return {
                'id': track['id'],
                'name': track['name'],
                'duration_ms': track['duration_ms'],
                'track_number': track.get('track_number', 1),
                'disc_number': track.get('disc_number', 1),
                'explicit': track.get('explicit', False),
                'preview_url': track.get('preview_url'),
                'external_url': track['external_urls']['spotify']
            }
        
        return self._get_paginated_items(
            endpoint=f"/albums/{album_id}/tracks",
            limit=limit,
            max_limit=50,
            offset=offset,
            transform_func=transform_album_track
        )
    
    def get_multiple_albums(self, album_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get information about multiple albums.
        
        Args:
            album_ids: List of Spotify album IDs (max 20)
            
        Returns:
            List of album information
        """
        return self._get_multiple_items(
            endpoint="/albums",
            ids=album_ids,
            max_ids=20,
            transform_func=SpotifyDataTransformer.transform_album
        )
    
    def get_new_releases(self, limit: int = 20, offset: int = 0, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get new album releases.
        
        Args:
            limit: Maximum number of albums
            offset: Offset for pagination
            country: Country code for market-specific releases
            
        Returns:
            List of album information
        """
        params = {}
        if country:
            params["country"] = country
        
        data = self._make_api_call(
            "GET", 
            "/browse/new-releases", 
            params={**params, "limit": min(limit, 50), "offset": offset},
            default_return={}
        )
        
        if not data:
            return []
        
        albums = data.get('albums', {}).get('items', [])
        return [SpotifyDataTransformer.transform_album(album) for album in albums] 