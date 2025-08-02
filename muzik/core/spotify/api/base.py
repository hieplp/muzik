"""
Base classes and common patterns for Spotify API operations.
"""

from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union

from .auth import SpotifyAuth
from ...config import Config


class BaseSpotifyAPI:
    """Base class for Spotify API operations with common patterns."""

    def __init__(self, config: Config):
        """
        Initialize base Spotify API handler.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.auth = SpotifyAuth(config)

    @contextmanager
    def _api_client(self):
        """
        Context manager for API client with automatic cleanup.
        
        Yields:
            SpotifyAPIClient instance or None if not configured
        """
        api_client = self.auth.get_api_client()
        try:
            yield api_client
        finally:
            if api_client:
                api_client.close()

    def _make_api_call(
            self,
            method: str,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            default_return: Union[List, Dict, None] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        Make an authenticated API call with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            default_return: Default value to return on error
            
        Returns:
            API response data or default_return on error
        """
        if default_return is None:
            default_return = []

        with self._api_client() as api_client:
            if not api_client:
                return default_return

            try:
                response = api_client.make_authenticated_request(method, endpoint, params=params)
                return response.json()
            except Exception:
                return default_return

    def _search_items(
            self,
            query: str,
            search_type: str,
            limit: int = 10,
            transform_func: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for items using Spotify search API.
        
        Args:
            query: Search query
            search_type: Type of search (track, album, artist, playlist)
            limit: Maximum number of results
            transform_func: Function to transform each item
            
        Returns:
            List of transformed search results
        """
        with self._api_client() as api_client:
            if not api_client:
                return []

            try:
                results = api_client.search(query, search_type=search_type, limit=limit)
                items = results.get(f'{search_type}s', {}).get('items', [])

                if transform_func:
                    return [transform_func(item) for item in items]
                return items

            except Exception:
                return []

    def _get_paginated_items(
            self,
            endpoint: str,
            limit: int = 50,
            offset: int = 0,
            max_limit: int = 50,
            transform_func: Optional[callable] = None,
            params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get paginated items from an API endpoint.
        
        Args:
            endpoint: API endpoint
            limit: Maximum number of items
            offset: Offset for pagination
            max_limit: Maximum allowed limit per request
            transform_func: Function to transform each item
            params: Additional query parameters
            
        Returns:
            List of transformed items
        """
        api_params = {
            "limit": min(limit, max_limit),
            "offset": offset
        }

        if params:
            api_params.update(params)

        data = self._make_api_call("GET", endpoint, params=api_params, default_return={})
        if not data:
            return []

        items = data.get('items', [])

        if transform_func:
            return [transform_func(item) for item in items if item]
        return [item for item in items if item]

    def _get_multiple_items(
            self,
            endpoint: str,
            ids: List[str],
            max_ids: int = 50,
            transform_func: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Get multiple items by their IDs.
        
        Args:
            endpoint: API endpoint
            ids: List of item IDs
            max_ids: Maximum number of IDs per request
            transform_func: Function to transform each item
            
        Returns:
            List of transformed items
        """
        if len(ids) > max_ids:
            ids = ids[:max_ids]

        params = {"ids": ",".join(ids)}
        data = self._make_api_call("GET", endpoint, params=params, default_return={})

        if not data:
            return []

        # The response key varies by endpoint type
        items_key = None
        for key in ['tracks', 'albums', 'artists', 'playlists']:
            if key in data:
                items_key = key
                break

        if not items_key:
            return []

        items = data.get(items_key, [])

        if transform_func:
            return [transform_func(item) for item in items if item]
        return [item for item in items if item]


class SpotifyDataTransformer:
    """Common data transformation methods for Spotify API responses."""

    @staticmethod
    def transform_track(track: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw track data into consistent format.
        
        Args:
            track: Raw track data from Spotify API
            
        Returns:
            Transformed track data
        """
        return {
            'id': track['id'],
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'popularity': track.get('popularity', 0),
            'external_url': track['external_urls']['spotify'],
            'preview_url': track.get('preview_url'),
            'explicit': track.get('explicit', False),
            'disc_number': track.get('disc_number', 1),
            'track_number': track.get('track_number', 1)
        }

    @staticmethod
    def transform_album(album: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw album data into consistent format.
        
        Args:
            album: Raw album data from Spotify API
            
        Returns:
            Transformed album data
        """
        return {
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
            'popularity': album.get('popularity', 0)
        }

    @staticmethod
    def transform_artist(artist: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw artist data into consistent format.
        
        Args:
            artist: Raw artist data from Spotify API
            
        Returns:
            Transformed artist data
        """
        return {
            'id': artist['id'],
            'name': artist['name'],
            'genres': artist.get('genres', []),
            'popularity': artist.get('popularity', 0),
            'followers': artist.get('followers', {}).get('total', 0),
            'external_url': artist['external_urls']['spotify'],
            'images': artist.get('images', [])
        }

    @staticmethod
    def transform_playlist(playlist: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw playlist data into consistent format.
        
        Args:
            playlist: Raw playlist data from Spotify API
            
        Returns:
            Transformed playlist data
        """
        return {
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
