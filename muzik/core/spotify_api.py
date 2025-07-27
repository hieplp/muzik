"""
Spotify API integration utilities.
"""

import os
from typing import Dict, List, Optional, Any

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import Config
from .spotify_config import validate_spotify_config

console = Console()


class SpotifyAPI:
    """Spotify API client wrapper."""
    
    def __init__(self, config: Config) -> None:
        """
        Initialize Spotify API client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.sp = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Spotify client."""
        if not validate_spotify_config(self.config):
            console.print("[red]Spotify API is not properly configured[/red]")
            return
        
        try:
            client_id = self.config.get("spotify.client_id")
            client_secret = self.config.get("spotify.client_secret")
            redirect_uri = self.config.get("spotify.redirect_uri", "http://localhost:8888/callback")
            
            # Initialize with OAuth
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope="user-library-read playlist-read-private user-top-read"
                )
            )
            
            console.print("[green]✓ Spotify API client initialized successfully![/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Error initializing Spotify client: {e}[/red]")
            self.sp = None
    
    def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of track information
        """
        if not self.sp:
            console.print("[red]Spotify client not initialized[/red]")
            return []
        
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'external_url': track['external_urls']['spotify'],
                    'preview_url': track['preview_url']
                }
                tracks.append(track_info)
            
            return tracks
            
        except Exception as e:
            console.print(f"[red]Error searching tracks: {e}[/red]")
            return []
    
    def get_user_playlists(self) -> List[Dict[str, Any]]:
        """
        Get user's playlists.
        
        Returns:
            List of playlist information
        """
        if not self.sp:
            console.print("[red]Spotify client not initialized[/red]")
            return []
        
        try:
            playlists = self.sp.current_user_playlists()
            playlist_list = []
            
            for playlist in playlists['items']:
                playlist_info = {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist.get('description', ''),
                    'tracks_count': playlist['tracks']['total'],
                    'public': playlist['public'],
                    'external_url': playlist['external_urls']['spotify']
                }
                playlist_list.append(playlist_info)
            
            return playlist_list
            
        except Exception as e:
            console.print(f"[red]Error getting playlists: {e}[/red]")
            return []
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Get tracks from a specific playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            List of track information
        """
        if not self.sp:
            console.print("[red]Spotify client not initialized[/red]")
            return []
        
        try:
            results = self.sp.playlist_tracks(playlist_id)
            tracks = []
            
            for item in results['items']:
                track = item['track']
                if track:
                    track_info = {
                        'id': track['id'],
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'album': track['album']['name'],
                        'duration_ms': track['duration_ms'],
                        'added_at': item['added_at']
                    }
                    tracks.append(track_info)
            
            return tracks
            
        except Exception as e:
            console.print(f"[red]Error getting playlist tracks: {e}[/red]")
            return []
    
    def get_user_top_tracks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get user's top tracks.
        
        Args:
            limit: Maximum number of tracks
            
        Returns:
            List of track information
        """
        if not self.sp:
            console.print("[red]Spotify client not initialized[/red]")
            return []
        
        try:
            results = self.sp.current_user_top_tracks(limit=limit)
            tracks = []
            
            for track in results['items']:
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
            
            return tracks
            
        except Exception as e:
            console.print(f"[red]Error getting top tracks: {e}[/red]")
            return []


def display_tracks_table(tracks: List[Dict[str, Any]], title: str = "Tracks") -> None:
    """
    Display tracks in a formatted table.
    
    Args:
        tracks: List of track dictionaries
        title: Table title
    """
    if not tracks:
        console.print("[yellow]No tracks found[/yellow]")
        return
    
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("#", width=3)
    table.add_column("Title", width=30)
    table.add_column("Artists", width=25)
    table.add_column("Album", width=25)
    table.add_column("Duration", width=8)
    table.add_column("Popularity", width=10)
    
    for i, track in enumerate(tracks, 1):
        # Format duration
        duration_ms = track.get('duration_ms', 0)
        duration_min = duration_ms // 60000
        duration_sec = (duration_ms % 60000) // 1000
        duration_str = f"{duration_min}:{duration_sec:02d}"
        
        # Format artists
        artists = ", ".join(track.get('artists', []))
        
        # Format popularity
        popularity = track.get('popularity', 0)
        popularity_bar = "█" * (popularity // 10) + "░" * (10 - popularity // 10)
        
        table.add_row(
            str(i),
            track.get('name', 'Unknown'),
            artists,
            track.get('album', 'Unknown'),
            duration_str,
            f"{popularity} {popularity_bar}"
        )
    
    console.print(table)


def display_playlists_table(playlists: List[Dict[str, Any]], title: str = "Playlists") -> None:
    """
    Display playlists in a formatted table.
    
    Args:
        playlists: List of playlist dictionaries
        title: Table title
    """
    if not playlists:
        console.print("[yellow]No playlists found[/yellow]")
        return
    
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("#", width=3)
    table.add_column("Name", width=30)
    table.add_column("Description", width=40)
    table.add_column("Tracks", width=8)
    table.add_column("Public", width=8)
    
    for i, playlist in enumerate(playlists, 1):
        table.add_row(
            str(i),
            playlist.get('name', 'Unknown'),
            playlist.get('description', '')[:37] + "..." if len(playlist.get('description', '')) > 40 else playlist.get('description', ''),
            str(playlist.get('tracks_count', 0)),
            "Yes" if playlist.get('public', False) else "No"
        )
    
    console.print(table) 