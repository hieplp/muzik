"""
Song search functionality.
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table

from ..config import Config
from ..spotify.auth import validate_spotify_config
from ..spotify.client import SpotifyAPI
from ...utils.spotify_display import display_tracks_table

console = Console()


def search_spotify_tracks(config: Config) -> None:
    """Search for tracks on Spotify."""
    if not validate_spotify_config(config):
        console.print("[red]Spotify API not configured. Please configure in Settings.[/red]")
        return
    
    console.print(Panel(
        "[bold blue]🎵 Spotify Track Search[/bold blue]\n\n"
        "Search for songs, artists, albums, or any combination.\n"
        "Examples:\n"
        "• 'Bohemian Rhapsody Queen'\n"
        "• 'artist:Taylor Swift love'\n"
        "• 'album:Abbey Road'\n"
        "• 'year:2023 pop'",
        title="Search Tips",
        border_style="blue"
    ))
    
    query = Prompt.ask("\n[bold]Enter search query[/bold]")
    if not query.strip():
        console.print("[yellow]No search query provided[/yellow]")
        return
    
    try:
        limit = IntPrompt.ask("Number of results", default=10, show_default=True)
        limit = max(1, min(50, limit))  # Limit between 1-50
    except (ValueError, KeyboardInterrupt):
        limit = 10
    
    console.print(f"\n[blue]Searching Spotify for: '{query}'...[/blue]")
    
    try:
        spotify = SpotifyAPI(config)
        tracks = spotify.search_tracks(query, limit)
        
        if tracks:
            display_tracks_table(tracks, f"Search Results for '{query}'")
            
            # Ask if user wants to save any tracks
            if console.input("\n[dim]Press 's' to save a track to library, or Enter to continue: [/dim]").lower() == 's':
                save_track_to_library(tracks, config)
        else:
            console.print("[yellow]No tracks found for your search.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error searching Spotify: {e}[/red]")


def search_by_title(config: Config) -> None:
    """Search for songs by title."""
    console.print(Panel(
        "[bold green]🎵 Search by Title[/bold green]\n\n"
        "Search for songs by their title or partial title match.",
        title="Title Search",
        border_style="green"
    ))
    
    title = Prompt.ask("\n[bold]Enter song title[/bold]")
    if not title.strip():
        console.print("[yellow]No title provided[/yellow]")
        return
    
    # If Spotify is configured, search there first
    if validate_spotify_config(config):
        console.print(f"[blue]Searching Spotify for title: '{title}'...[/blue]")
        try:
            spotify = SpotifyAPI(config)
            # Use track: prefix for more accurate title searches
            tracks = spotify.search_tracks(f'track:"{title}"', limit=20)
            
            if tracks:
                display_tracks_table(tracks, f"Title Search Results for '{title}'")
                return
        except Exception as e:
            console.print(f"[yellow]Spotify search failed: {e}[/yellow]")
    
    # Fallback to local search or other sources
    console.print("[blue]Searching local sources...[/blue]")
    search_local_by_title(title, config)


def search_by_author(config: Config) -> None:
    """Search for songs by author/composer."""
    console.print(Panel(
        "[bold magenta]🎵 Search by Author/Composer[/bold magenta]\n\n"
        "Search for songs by their composer, songwriter, or author.",
        title="Author Search",
        border_style="magenta"
    ))
    
    author = Prompt.ask("\n[bold]Enter author/composer name[/bold]")
    if not author.strip():
        console.print("[yellow]No author name provided[/yellow]")
        return
    
    if validate_spotify_config(config):
        console.print(f"[blue]Searching for songs by author: '{author}'...[/blue]")
        try:
            spotify = SpotifyAPI(config)
            # Search with various strategies for composer/author
            queries = [
                f'"{author}" songwriter',
                f'"{author}" composer', 
                f'"{author}"'
            ]
            
            all_tracks = []
            for query in queries:
                tracks = spotify.search_tracks(query, limit=15)
                all_tracks.extend(tracks)
            
            # Remove duplicates based on track ID
            unique_tracks = {}
            for track in all_tracks:
                unique_tracks[track.get('id')] = track
            
            if unique_tracks:
                display_tracks_table(list(unique_tracks.values())[:20], f"Author Search Results for '{author}'")
                return
        except Exception as e:
            console.print(f"[yellow]Spotify search failed: {e}[/yellow]")
    
    console.print("[blue]Searching local sources...[/blue]")
    search_local_by_author(author, config)


def search_by_singer(config: Config) -> None:
    """Search for songs by singer/artist."""
    console.print(Panel(
        "[bold cyan]🎵 Search by Singer/Artist[/bold cyan]\n\n"
        "Search for songs performed by a specific artist or singer.",
        title="Artist Search", 
        border_style="cyan"
    ))
    
    artist = Prompt.ask("\n[bold]Enter artist/singer name[/bold]")
    if not artist.strip():
        console.print("[yellow]No artist name provided[/yellow]")
        return
    
    if validate_spotify_config(config):
        console.print(f"[blue]Searching for songs by artist: '{artist}'...[/blue]")
        try:
            spotify = SpotifyAPI(config)
            tracks = spotify.search_tracks(f'artist:"{artist}"', limit=25)
            
            if tracks:
                display_tracks_table(tracks, f"Artist Search Results for '{artist}'")
                
                # Offer to show artist's popular tracks
                if console.input("\n[dim]Press 'a' to see more from this artist, or Enter to continue: [/dim]").lower() == 'a':
                    show_artist_details(artist, config)
                return
        except Exception as e:
            console.print(f"[yellow]Spotify search failed: {e}[/yellow]")
    
    console.print("[blue]Searching local sources...[/blue]")
    search_local_by_artist(artist, config)


def show_artist_details(artist_name: str, config: Config) -> None:
    """Show detailed information about an artist."""
    try:
        spotify = SpotifyAPI(config)
        
        console.print(f"[blue]Getting detailed information for '{artist_name}'...[/blue]")
        
        # Search for the artist
        artists = spotify.search_artists(artist_name, limit=1)
        if not artists:
            console.print("[yellow]Artist not found[/yellow]")
            return
        
        artist = artists[0]
        
        # Display artist info
        console.print(Panel(
            f"[bold]{artist['name']}[/bold]\n"
            f"Followers: {artist.get('followers', {}).get('total', 'N/A'):,}\n"
            f"Popularity: {artist.get('popularity', 'N/A')}/100\n"
            f"Genres: {', '.join(artist.get('genres', []))[:50]}",
            title=f"🎤 {artist['name']}",
            border_style="cyan"
        ))
        
        # Get top tracks
        top_tracks = spotify.get_artist_top_tracks(artist['id'])
        if top_tracks:
            display_tracks_table(top_tracks, f"Top Tracks by {artist['name']}")
            
    except Exception as e:
        console.print(f"[red]Error getting artist details: {e}[/red]")


def search_local_by_title(title: str, config: Config) -> None:
    """Search local sources by title (placeholder)."""
    console.print(f"[dim]Local title search for '{title}' - Feature coming soon[/dim]")


def search_local_by_author(author: str, config: Config) -> None:
    """Search local sources by author (placeholder)."""
    console.print(f"[dim]Local author search for '{author}' - Feature coming soon[/dim]")


def search_local_by_artist(artist: str, config: Config) -> None:
    """Search local sources by artist (placeholder)."""
    console.print(f"[dim]Local artist search for '{artist}' - Feature coming soon[/dim]")


def save_track_to_library(tracks: List[Dict[str, Any]], config: Config) -> None:
    """Save a selected track to personal library."""
    try:
        track_num = IntPrompt.ask("Enter track number to save", show_default=False)
        if 1 <= track_num <= len(tracks):
            track = tracks[track_num - 1]
            # This would integrate with the library module
            console.print(f"[green]Saved '{track['name']}' by {', '.join(track['artists'])} to library[/green]")
        else:
            console.print("[red]Invalid track number[/red]")
    except (ValueError, KeyboardInterrupt):
        console.print("[yellow]Save cancelled[/yellow]")


def advanced_search(config: Config) -> None:
    """Advanced search with multiple filters."""
    console.print(Panel(
        "[bold yellow]🔍 Advanced Search[/bold yellow]\n\n"
        "Use advanced filters to find exactly what you're looking for.\n"
        "You can combine multiple criteria for precise results.",
        title="Advanced Search",
        border_style="yellow"
    ))
    
    filters = {}
    
    # Collect search criteria
    if title := Prompt.ask("Song title (optional)", default=""):
        filters['title'] = title
    
    if artist := Prompt.ask("Artist name (optional)", default=""):
        filters['artist'] = artist
        
    if album := Prompt.ask("Album name (optional)", default=""):
        filters['album'] = album
        
    if year := Prompt.ask("Release year (optional)", default=""):
        filters['year'] = year
        
    if genre := Prompt.ask("Genre (optional)", default=""):
        filters['genre'] = genre
    
    # Build search query
    query_parts = []
    for key, value in filters.items():
        if value:
            if key == 'title':
                query_parts.append(f'track:"{value}"')
            elif key == 'artist':
                query_parts.append(f'artist:"{value}"')
            elif key == 'album':
                query_parts.append(f'album:"{value}"')
            elif key == 'year':
                query_parts.append(f'year:{value}')
            elif key == 'genre':
                query_parts.append(f'genre:"{value}"')
    
    if not query_parts:
        console.print("[yellow]No search criteria provided[/yellow]")
        return
    
    query = ' '.join(query_parts)
    console.print(f"[blue]Searching with query: {query}[/blue]")
    
    if validate_spotify_config(config):
        try:
            spotify = SpotifyAPI(config)
            tracks = spotify.search_tracks(query, limit=30)
            
            if tracks:
                display_tracks_table(tracks, "Advanced Search Results")
            else:
                console.print("[yellow]No tracks found matching your criteria[/yellow]")
        except Exception as e:
            console.print(f"[red]Error in advanced search: {e}[/red]")
    else:
        console.print("[red]Spotify API required for advanced search[/red]") 