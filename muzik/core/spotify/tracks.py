"""
Spotify tracks API operations.
"""

from typing import Any, Dict, List, Optional

from ..config import Config
from .auth import SpotifyAuth


class SpotifyTracks:
    """Handles Spotify track operations."""
    
    def __init__(self, config: Config):
        """
        Initialize Spotify tracks handler.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.auth = SpotifyAuth(config)
    
    def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of track information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            results = api_client.search(query, search_type="track", limit=limit)
            tracks = []
            
            for track in results.get('tracks', {}).get('items', []):
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'external_url': track['external_urls']['spotify'],
                    'preview_url': track.get('preview_url')
                }
                tracks.append(track_info)
            
            api_client.close()
            return tracks
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_track(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track information or None if not found
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return None
        
        try:
            response = api_client.make_authenticated_request("GET", f"/tracks/{track_id}")
            track = response.json()
            
            track_info = {
                'id': track['id'],
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity'],
                'external_url': track['external_urls']['spotify'],
                'preview_url': track.get('preview_url'),
                'explicit': track.get('explicit', False),
                'disc_number': track.get('disc_number', 1),
                'track_number': track.get('track_number', 1)
            }
            
            api_client.close()
            return track_info
            
        except Exception:
            if api_client:
                api_client.close()
            return None
    
    def get_multiple_tracks(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get information about multiple tracks.
        
        Args:
            track_ids: List of Spotify track IDs (max 50)
            
        Returns:
            List of track information
        """
        if len(track_ids) > 50:
            track_ids = track_ids[:50]
        
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {"ids": ",".join(track_ids)}
            response = api_client.make_authenticated_request("GET", "/tracks", params=params)
            data = response.json()
            
            tracks = []
            for track in data.get('tracks', []):
                if track:  # Track might be None if not found
                    track_info = {
                        'id': track['id'],
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'album': track['album']['name'],
                        'duration_ms': track['duration_ms'],
                        'popularity': track['popularity'],
                        'external_url': track['external_urls']['spotify'],
                        'preview_url': track.get('preview_url')
                    }
                    tracks.append(track_info)
            
            api_client.close()
            return tracks
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_audio_features(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audio features for a track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Audio features or None if not found
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return None
        
        try:
            response = api_client.make_authenticated_request("GET", f"/audio-features/{track_id}")
            features = response.json()
            
            api_client.close()
            return features
            
        except Exception:
            if api_client:
                api_client.close()
            return None
    
    def get_user_top_tracks(self, limit: int = 20, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        """
        Get user's top tracks.
        
        Args:
            limit: Maximum number of tracks (max 50)
            time_range: Time range (short_term, medium_term, long_term)
            
        Returns:
            List of track information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {
                "limit": min(limit, 50),
                "time_range": time_range
            }
            
            response = api_client.make_authenticated_request("GET", "/me/top/tracks", params=params)
            data = response.json()
            
            tracks = []
            for track in data.get('items', []):
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'external_url': track['external_urls']['spotify']
                }
                tracks.append(track_info)
            
            api_client.close()
            return tracks
            
        except Exception:
            if api_client:
                api_client.close()
            return [] 