"""
Spotify albums API operations.
"""

from typing import Any, Dict, List, Optional

from ..config import Config
from .auth import SpotifyAuth


class SpotifyAlbums:
    """Handles Spotify album operations."""
    
    def __init__(self, config: Config):
        """
        Initialize Spotify albums handler.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.auth = SpotifyAuth(config)
    
    def search_albums(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for albums on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of album information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            results = api_client.search(query, search_type="album", limit=limit)
            albums = []
            
            for album in results.get('albums', {}).get('items', []):
                album_info = {
                    'id': album['id'],
                    'name': album['name'],
                    'artists': [artist['name'] for artist in album['artists']],
                    'release_date': album.get('release_date', ''),
                    'total_tracks': album.get('total_tracks', 0),
                    'album_type': album.get('album_type', ''),
                    'external_url': album['external_urls']['spotify'],
                    'images': album.get('images', [])
                }
                albums.append(album_info)
            
            api_client.close()
            return albums
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_album(self, album_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific album.
        
        Args:
            album_id: Spotify album ID
            
        Returns:
            Album information or None if not found
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return None
        
        try:
            response = api_client.make_authenticated_request("GET", f"/albums/{album_id}")
            album = response.json()
            
            album_info = {
                'id': album['id'],
                'name': album['name'],
                'artists': [artist['name'] for artist in album['artists']],
                'release_date': album.get('release_date', ''),
                'total_tracks': album.get('total_tracks', 0),
                'album_type': album.get('album_type', ''),
                'external_url': album['external_urls']['spotify'],
                'images': album.get('images', []),
                'genres': album.get('genres', []),
                'label': album.get('label', ''),
                'popularity': album.get('popularity', 0),
                'tracks': []
            }
            
            # Add track information
            for track in album.get('tracks', {}).get('items', []):
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'duration_ms': track['duration_ms'],
                    'track_number': track.get('track_number', 1),
                    'disc_number': track.get('disc_number', 1),
                    'explicit': track.get('explicit', False)
                }
                album_info['tracks'].append(track_info)
            
            api_client.close()
            return album_info
            
        except Exception:
            if api_client:
                api_client.close()
            return None
    
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
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {
                "limit": min(limit, 50),
                "offset": offset
            }
            
            response = api_client.make_authenticated_request("GET", f"/albums/{album_id}/tracks", params=params)
            data = response.json()
            
            tracks = []
            for track in data.get('items', []):
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'duration_ms': track['duration_ms'],
                    'track_number': track.get('track_number', 1),
                    'disc_number': track.get('disc_number', 1),
                    'explicit': track.get('explicit', False),
                    'preview_url': track.get('preview_url'),
                    'external_url': track['external_urls']['spotify']
                }
                tracks.append(track_info)
            
            api_client.close()
            return tracks
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_multiple_albums(self, album_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get information about multiple albums.
        
        Args:
            album_ids: List of Spotify album IDs (max 20)
            
        Returns:
            List of album information
        """
        if len(album_ids) > 20:
            album_ids = album_ids[:20]
        
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {"ids": ",".join(album_ids)}
            response = api_client.make_authenticated_request("GET", "/albums", params=params)
            data = response.json()
            
            albums = []
            for album in data.get('albums', []):
                if album:  # Album might be None if not found
                    album_info = {
                        'id': album['id'],
                        'name': album['name'],
                        'artists': [artist['name'] for artist in album['artists']],
                        'release_date': album.get('release_date', ''),
                        'total_tracks': album.get('total_tracks', 0),
                        'album_type': album.get('album_type', ''),
                        'external_url': album['external_urls']['spotify'],
                        'images': album.get('images', [])
                    }
                    albums.append(album_info)
            
            api_client.close()
            return albums
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
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
            
            response = api_client.make_authenticated_request("GET", "/browse/new-releases", params=params)
            data = response.json()
            
            albums = []
            for album in data.get('albums', {}).get('items', []):
                album_info = {
                    'id': album['id'],
                    'name': album['name'],
                    'artists': [artist['name'] for artist in album['artists']],
                    'release_date': album.get('release_date', ''),
                    'total_tracks': album.get('total_tracks', 0),
                    'album_type': album.get('album_type', ''),
                    'external_url': album['external_urls']['spotify'],
                    'images': album.get('images', [])
                }
                albums.append(album_info)
            
            api_client.close()
            return albums
            
        except Exception:
            if api_client:
                api_client.close()
            return [] 