"""
Spotify artists API operations.
"""

from typing import Any, Dict, List, Optional

from ..config import Config
from .auth import SpotifyAuth


class SpotifyArtists:
    """Handles Spotify artist operations."""
    
    def __init__(self, config: Config):
        """
        Initialize Spotify artists handler.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.auth = SpotifyAuth(config)
    
    def search_artists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for artists on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of artist information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            results = api_client.search(query, search_type="artist", limit=limit)
            artists = []
            
            for artist in results.get('artists', {}).get('items', []):
                artist_info = {
                    'id': artist['id'],
                    'name': artist['name'],
                    'genres': artist.get('genres', []),
                    'popularity': artist.get('popularity', 0),
                    'followers': artist.get('followers', {}).get('total', 0),
                    'external_url': artist['external_urls']['spotify'],
                    'images': artist.get('images', [])
                }
                artists.append(artist_info)
            
            api_client.close()
            return artists
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_artist(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific artist.
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            Artist information or None if not found
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return None
        
        try:
            response = api_client.make_authenticated_request("GET", f"/artists/{artist_id}")
            artist = response.json()
            
            artist_info = {
                'id': artist['id'],
                'name': artist['name'],
                'genres': artist.get('genres', []),
                'popularity': artist.get('popularity', 0),
                'followers': artist.get('followers', {}).get('total', 0),
                'external_url': artist['external_urls']['spotify'],
                'images': artist.get('images', [])
            }
            
            api_client.close()
            return artist_info
            
        except Exception:
            if api_client:
                api_client.close()
            return None
    
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
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {
                "limit": min(limit, 50),
                "offset": offset
            }
            
            if include_groups:
                params["include_groups"] = include_groups
            if market:
                params["market"] = market
            
            response = api_client.make_authenticated_request("GET", f"/artists/{artist_id}/albums", params=params)
            data = response.json()
            
            albums = []
            for album in data.get('items', []):
                album_info = {
                    'id': album['id'],
                    'name': album['name'],
                    'album_type': album.get('album_type', ''),
                    'release_date': album.get('release_date', ''),
                    'total_tracks': album.get('total_tracks', 0),
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
    
    def get_artist_top_tracks(self, artist_id: str, market: str = "US") -> List[Dict[str, Any]]:
        """
        Get top tracks for a specific artist.
        
        Args:
            artist_id: Spotify artist ID
            market: Market (country code)
            
        Returns:
            List of track information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {"market": market}
            response = api_client.make_authenticated_request("GET", f"/artists/{artist_id}/top-tracks", params=params)
            data = response.json()
            
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
            
            api_client.close()
            return tracks
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_related_artists(self, artist_id: str) -> List[Dict[str, Any]]:
        """
        Get artists related to a specific artist.
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            List of related artist information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            response = api_client.make_authenticated_request("GET", f"/artists/{artist_id}/related-artists")
            data = response.json()
            
            artists = []
            for artist in data.get('artists', []):
                artist_info = {
                    'id': artist['id'],
                    'name': artist['name'],
                    'genres': artist.get('genres', []),
                    'popularity': artist.get('popularity', 0),
                    'followers': artist.get('followers', {}).get('total', 0),
                    'external_url': artist['external_urls']['spotify'],
                    'images': artist.get('images', [])
                }
                artists.append(artist_info)
            
            api_client.close()
            return artists
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_multiple_artists(self, artist_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get information about multiple artists.
        
        Args:
            artist_ids: List of Spotify artist IDs (max 50)
            
        Returns:
            List of artist information
        """
        if len(artist_ids) > 50:
            artist_ids = artist_ids[:50]
        
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {"ids": ",".join(artist_ids)}
            response = api_client.make_authenticated_request("GET", "/artists", params=params)
            data = response.json()
            
            artists = []
            for artist in data.get('artists', []):
                if artist:  # Artist might be None if not found
                    artist_info = {
                        'id': artist['id'],
                        'name': artist['name'],
                        'genres': artist.get('genres', []),
                        'popularity': artist.get('popularity', 0),
                        'followers': artist.get('followers', {}).get('total', 0),
                        'external_url': artist['external_urls']['spotify'],
                        'images': artist.get('images', [])
                    }
                    artists.append(artist_info)
            
            api_client.close()
            return artists
            
        except Exception:
            if api_client:
                api_client.close()
            return []
    
    def get_user_top_artists(self, limit: int = 20, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        """
        Get user's top artists.
        
        Args:
            limit: Maximum number of artists (max 50)
            time_range: Time range (short_term, medium_term, long_term)
            
        Returns:
            List of artist information
        """
        api_client = self.auth.get_api_client()
        if not api_client:
            return []
        
        try:
            params = {
                "limit": min(limit, 50),
                "time_range": time_range
            }
            
            response = api_client.make_authenticated_request("GET", "/me/top/artists", params=params)
            data = response.json()
            
            artists = []
            for artist in data.get('items', []):
                artist_info = {
                    'id': artist['id'],
                    'name': artist['name'],
                    'genres': artist.get('genres', []),
                    'popularity': artist.get('popularity', 0),
                    'followers': artist.get('followers', {}).get('total', 0),
                    'external_url': artist['external_urls']['spotify']
                }
                artists.append(artist_info)
            
            api_client.close()
            return artists
            
        except Exception:
            if api_client:
                api_client.close()
            return [] 