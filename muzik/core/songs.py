"""
Songs management functionality.
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm

from .config import Config
from .spotify.auth import validate_spotify_config
from .spotify.client import SpotifyAPI
from .spotify.display import display_tracks_table, display_playlists_table

console = Console()


def show_songs_menu() -> None:
    """Show the songs menu."""
    config = Config()
    spotify_configured = validate_spotify_config(config)
    
    from .menu import Menu
    
    menu = Menu("🎵 Songs")
    
    if spotify_configured:
        menu.add_item(
            "Search Spotify",
            lambda: search_spotify_tracks(config),
            "Search for songs using Spotify API",
            "1"
        )
        
        menu.add_item(
            "My Spotify Playlists",
            lambda: show_spotify_playlists(config),
            "View and manage your Spotify playlists",
            "2"
        )
        
        menu.add_separator()
    
    menu.add_item(
        "Find songs by title",
        lambda: console.print("[blue]Searching songs by title...[/blue]"),
        "Search for songs using title",
        "3" if spotify_configured else "1"
    )
    
    menu.add_item(
        "Find songs by authors",
        lambda: console.print("[blue]Searching songs by authors...[/blue]"),
        "Search for songs using author names",
        "4" if spotify_configured else "2"
    )
    
    menu.add_item(
        "Find songs by singers",
        lambda: console.print("[blue]Searching songs by singers...[/blue]"),
        "Search for songs using singer names",
        "5" if spotify_configured else "3"
    )
    
    if not spotify_configured:
        menu.add_separator()
        menu.add_item(
            "Configure Spotify API",
            lambda: console.print("[yellow]Go to Settings > Spotify API Settings to configure[/yellow]"),
            "Set up Spotify API access",
            "4"
        )
    
    menu.add_separator()
    
    menu.add_item(
        "Back to Main Menu",
        lambda: setattr(menu, 'running', False),
        "Return to main menu",
        "b"
    )
    
    menu.run()


def search_spotify_tracks(config: Config) -> None:
    """Search for tracks on Spotify."""
    console.print("[blue]Searching Spotify for tracks...[/blue]")
    
    query = Prompt.ask("Enter search query")
    if not query:
        console.print("[yellow]No search query provided[/yellow]")
        return
    
    limit = Prompt.ask("Number of results", default="10")
    try:
        limit = int(limit)
    except ValueError:
        limit = 10
    
    spotify = SpotifyAPI(config)
    tracks = spotify.search_tracks(query, limit)
    
    if tracks:
        display_tracks_table(tracks, f"Search Results for '{query}'")
    else:
        console.print("[yellow]No tracks found[/yellow]")


def show_spotify_playlists(config: Config) -> None:
    """Show user's Spotify playlists."""
    console.print("[blue]Loading your Spotify playlists...[/blue]")
    
    spotify = SpotifyAPI(config)
    playlists = spotify.get_user_playlists()
    
    if not playlists:
        console.print("[yellow]No playlists found[/yellow]")
        return
    
    display_playlists_table(playlists, "Your Spotify Playlists")
    
    # Ask if user wants to view tracks from a specific playlist
    if Confirm.ask("Do you want to view tracks from a specific playlist?"):
        try:
            playlist_num = int(Prompt.ask("Enter playlist number")) - 1
            if 0 <= playlist_num < len(playlists):
                playlist = playlists[playlist_num]
                console.print(f"[blue]Loading tracks from '{playlist['name']}'...[/blue]")
                
                tracks = spotify.get_playlist_tracks(playlist['id'])
                if tracks:
                    display_tracks_table(tracks, f"Tracks in '{playlist['name']}'")
                else:
                    console.print("[yellow]No tracks found in this playlist[/yellow]")
            else:
                console.print("[red]Invalid playlist number[/red]")
        except ValueError:
            console.print("[red]Invalid input[/red]") 