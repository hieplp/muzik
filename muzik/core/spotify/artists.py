"""
Spotify artists API operations.
"""

from typing import Any, Dict, List, Optional

from ..config import Config
from .base import BaseSpotifyAPI, SpotifyDataTransformer


class SpotifyArtists(BaseSpotifyAPI):
    """Handles Spotify artist operations."""
    
    def search_artists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for artists on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of artist information
        """
        return self._search_items(
            query=query,
            search_type="artist",
            limit=limit,
            transform_func=SpotifyDataTransformer.transform_artist
        )
    
    def get_artist(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific artist.
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            Artist information or None if not found
        """
        data = self._make_api_call("GET", f"/artists/{artist_id}", default_return=None)
        if not data:
            return None
        
        return SpotifyDataTransformer.transform_artist(data)
    
    def get_artist_albums(
        self, 
        artist_id: str, 
        include_groups: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get albums for a specific artist.
        
        Args:
            artist_id: Spotify artist ID
            include_groups: Album types to include (album, single, appears_on, compilation)
            limit: Maximum number of albums
            offset: Offset for pagination
            market: Market (country code)
            
        Returns:
            List of album information
        """
        params = {}
        if include_groups:
            params["include_groups"] = include_groups
        if market:
            params["market"] = market
        
        def transform_artist_album(album: Dict[str, Any]) -> Dict[str, Any]:
            """Transform artist album data."""
            return {
                'id': album['id'],
                'name': album['name'],
                'album_type': album.get('album_type', ''),
                'release_date': album.get('release_date', ''),
                'total_tracks': album.get('total_tracks', 0),
                'external_url': album['external_urls']['spotify'],
                'images': album.get('images', [])
            }
        
        return self._get_paginated_items(
            endpoint=f"/artists/{artist_id}/albums",
            limit=limit,
            max_limit=50,
            offset=offset,
            params=params,
            transform_func=transform_artist_album
        )
    
    def get_artist_top_tracks(self, artist_id: str, market: str = "US") -> List[Dict[str, Any]]:
        """
        Get top tracks for a specific artist.
        
        Args:
            artist_id: Spotify artist ID
            market: Market (country code)
            
        Returns:
            List of track information
        """
        data = self._make_api_call(
            "GET", 
            f"/artists/{artist_id}/top-tracks", 
            params={"market": market},
            default_return={}
        )
        
        if not data:
            return []
        
        tracks = []
        for track in data.get('tracks', []):
            track_info = {
                'id': track['id'],
                'name': track['name'],
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity'],
                'external_url': track['external_urls']['spotify'],
                'preview_url': track.get('preview_url')
            }
            tracks.append(track_info)
        
        return tracks
    
    def get_related_artists(self, artist_id: str) -> List[Dict[str, Any]]:
        """
        Get artists related to a specific artist.
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            List of related artist information
        """
        data = self._make_api_call(
            "GET", 
            f"/artists/{artist_id}/related-artists",
            default_return={}
        )
        
        if not data:
            return []
        
        artists = data.get('artists', [])
        return [SpotifyDataTransformer.transform_artist(artist) for artist in artists]
    
    def get_multiple_artists(self, artist_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get information about multiple artists.
        
        Args:
            artist_ids: List of Spotify artist IDs (max 50)
            
        Returns:
            List of artist information
        """
        return self._get_multiple_items(
            endpoint="/artists",
            ids=artist_ids,
            max_ids=50,
            transform_func=SpotifyDataTransformer.transform_artist
        )
    
    def get_user_top_artists(self, limit: int = 20, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        """
        Get user's top artists.
        
        Args:
            limit: Maximum number of artists (max 50)
            time_range: Time range (short_term, medium_term, long_term)
            
        Returns:
            List of artist information
        """
        params = {"time_range": time_range}
        
        return self._get_paginated_items(
            endpoint="/me/top/artists",
            limit=limit,
            max_limit=50,
            params=params,
            transform_func=SpotifyDataTransformer.transform_artist
        ) 