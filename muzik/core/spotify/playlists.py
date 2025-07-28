"""
Spotify playlists API operations.
"""

from typing import Any, Dict, List, Optional

from ..config import Config
from .auth import SpotifyAuth


class SpotifyPlaylists:
    """Handles Spotify playlist operations."""
    
    def __init__(self, config: Config):
        """
        Initialize Spotify playlists handler.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.auth = SpotifyAuth(config)
    
    def search_playlists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for playlists on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of playlist information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            results = api_client.search(query, search_type="playlist", limit=limit)
            playlists = []
            
            for playlist in results.get('playlists', {}).get('items', []):
                playlist_info = {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist.get('description', ''),
                    'tracks_count': playlist['tracks']['total'],
                    'public': playlist.get('public', False),
                    'collaborative': playlist.get('collaborative', False),
                    'owner': playlist['owner']['display_name'] if playlist.get('owner') else '',
                    'external_url': playlist['external_urls']['spotify'],
                    'images': playlist.get('images', [])
                }
                playlists.append(playlist_info)
            
            api_client.close()
            return playlists
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_user_playlists(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get current user's playlists.
        
        Args:
            limit: Maximum number of playlists
            offset: Offset for pagination
            
        Returns:
            List of playlist information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {
                "limit": min(limit, 50),
                "offset": offset
            }
            
            response = api_client.make_authenticated_request("GET", "/me/playlists", params=params)
            data = response.json()
            
            playlists = []
            for playlist in data.get('items', []):
                playlist_info = {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist.get('description', ''),
                    'tracks_count': playlist['tracks']['total'],
                    'public': playlist.get('public', False),
                    'collaborative': playlist.get('collaborative', False),
                    'owner': playlist['owner']['display_name'] if playlist.get('owner') else '',
                    'external_url': playlist['external_urls']['spotify'],
                    'images': playlist.get('images', [])
                }
                playlists.append(playlist_info)
            
            api_client.close()
            return playlists
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_playlist(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            Playlist information or None if not found
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return None
        
        try:
            response = api_client.make_authenticated_request("GET", f"/playlists/{playlist_id}")
            playlist = response.json()
            
            playlist_info = {
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'tracks_count': playlist['tracks']['total'],
                'public': playlist.get('public', False),
                'collaborative': playlist.get('collaborative', False),
                'owner': playlist['owner']['display_name'] if playlist.get('owner') else '',
                'external_url': playlist['external_urls']['spotify'],
                'images': playlist.get('images', []),
                'followers': playlist.get('followers', {}).get('total', 0)
            }
            
            api_client.close()
            return playlist_info
            
        except Exception:
            if api_client:
                api_client.close()
            return None
    
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
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {
                "limit": min(limit, 100),
                "offset": offset
            }
            
            response = api_client.make_authenticated_request("GET", f"/playlists/{playlist_id}/tracks", params=params)
            data = response.json()
            
            tracks = []
            for item in data.get('items', []):
                track = item.get('track')
                if track and track.get('type') == 'track':  # Skip episodes and other non-track items
                    track_info = {
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
                    tracks.append(track_info)
            
            api_client.close()
            return tracks
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
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
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {
                "limit": min(limit, 50),
                "offset": offset
            }
            
            if country:
                params["country"] = country
            
            response = api_client.make_authenticated_request("GET", "/browse/featured-playlists", params=params)
            data = response.json()
            
            playlists = []
            for playlist in data.get('playlists', {}).get('items', []):
                playlist_info = {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist.get('description', ''),
                    'tracks_count': playlist['tracks']['total'],
                    'public': playlist.get('public', False),
                    'owner': playlist['owner']['display_name'] if playlist.get('owner') else '',
                    'external_url': playlist['external_urls']['spotify'],
                    'images': playlist.get('images', [])
                }
                playlists.append(playlist_info)
            
            api_client.close()
            return playlists
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
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
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {
                "limit": min(limit, 50),
                "offset": offset
            }
            
            if country:
                params["country"] = country
            
            response = api_client.make_authenticated_request("GET", f"/browse/categories/{category_id}/playlists", params=params)
            data = response.json()
            
            playlists = []
            for playlist in data.get('playlists', {}).get('items', []):
                playlist_info = {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist.get('description', ''),
                    'tracks_count': playlist['tracks']['total'],
                    'public': playlist.get('public', False),
                    'owner': playlist['owner']['display_name'] if playlist.get('owner') else '',
                    'external_url': playlist['external_urls']['spotify'],
                    'images': playlist.get('images', [])
                }
                playlists.append(playlist_info)
            
            api_client.close()
            return playlists
            
        except Exception:
            if api_client:
                api_client.close()
            return [] 