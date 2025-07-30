"""
Spotify tracks API operations.
"""

from typing import Any, Dict, List, Optional

from ...config import Config
from .base import BaseSpotifyAPI, SpotifyDataTransformer


class SpotifyTracks(BaseSpotifyAPI):
    """Handles Spotify track operations."""
    
    def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of track information
        """
        return self._search_items(
            query=query,
            search_type="track",
            limit=limit,
            transform_func=SpotifyDataTransformer.transform_track
        )
    
    def get_track(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track information or None if not found
        """
        data = self._make_api_call("GET", f"/tracks/{track_id}", default_return=None)
        if not data:
            return None
        
        return SpotifyDataTransformer.transform_track(data)
    
    def get_multiple_tracks(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get information about multiple tracks.
        
        Args:
            track_ids: List of Spotify track IDs (max 50)
            
        Returns:
            List of track information
        """
        return self._get_multiple_items(
            endpoint="/tracks",
            ids=track_ids,
            max_ids=50,
            transform_func=SpotifyDataTransformer.transform_track
        )
    
    def get_audio_features(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audio features for a track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Audio features or None if not found
        """
        return self._make_api_call("GET", f"/audio-features/{track_id}", default_return=None)
    
    def get_user_top_tracks(self, limit: int = 20, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        """
        Get user's top tracks.
        
        Args:
            limit: Maximum number of tracks (max 50)
            time_range: Time range (short_term, medium_term, long_term)
            
        Returns:
            List of track information
        """
        params = {"time_range": time_range}
        
        return self._get_paginated_items(
            endpoint="/me/top/tracks",
            limit=limit,
            max_limit=50,
            params=params,
            transform_func=SpotifyDataTransformer.transform_track
        ) 