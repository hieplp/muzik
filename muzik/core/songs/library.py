"""
Personal music library management functionality.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..config import Config
from ..spotify.auth import validate_spotify_config
from ..spotify.client import SpotifyAPI
from ...utils.spotify_display import display_tracks_table

console = Console()


class PersonalLibrary:
    """Manages the user's personal music library."""
    
    def __init__(self, config: Config):
        """Initialize the personal library."""
        self.config = config
        self.library_file = Path.home() / ".muzik" / "library.json"
        self.library_file.parent.mkdir(exist_ok=True)
        
    def load_library(self) -> Dict[str, Any]:
        """Load the library from disk."""
        if not self.library_file.exists():
            return {
                "tracks": [],
                "playlists": [],
                "favorites": [],
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
        
        try:
            with open(self.library_file, 'r') as f:
                library = json.load(f)
                # Ensure all required keys exist
                library.setdefault("tracks", [])
                library.setdefault("playlists", [])
                library.setdefault("favorites", [])
                library.setdefault("metadata", {})
                return library
        except (json.JSONDecodeError, FileNotFoundError):
            console.print("[yellow]Library file corrupted, creating new one[/yellow]")
            return self.load_library()
    
    def save_library(self, library: Dict[str, Any]) -> bool:
        """Save the library to disk."""
        try:
            library["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.library_file, 'w') as f:
                json.dump(library, f, indent=2)
            return True
        except Exception as e:
            console.print(f"[red]Error saving library: {e}[/red]")
            return False
    
    def add_track(self, track: Dict[str, Any]) -> bool:
        """Add a track to the library."""
        library = self.load_library()
        
        # Check if track already exists
        for existing_track in library["tracks"]:
            if existing_track.get("id") == track.get("id"):
                console.print("[yellow]Track already in library[/yellow]")
                return False
        
        # Add metadata
        track["added_date"] = datetime.now().isoformat()
        track["source"] = "spotify" if track.get("id") else "manual"
        
        library["tracks"].append(track)
        return self.save_library(library)
    
    def remove_track(self, track_id: str) -> bool:
        """Remove a track from the library."""
        library = self.load_library()
        
        original_count = len(library["tracks"])
        library["tracks"] = [t for t in library["tracks"] if t.get("id") != track_id]
        
        if len(library["tracks"]) < original_count:
            return self.save_library(library)
        else:
            console.print("[yellow]Track not found in library[/yellow]")
            return False
    
    def search_library(self, query: str) -> List[Dict[str, Any]]:
        """Search the library for tracks."""
        library = self.load_library()
        query = query.lower()
        
        results = []
        for track in library["tracks"]:
            # Search in name, artists, album
            searchable_text = " ".join([
                track.get("name", "").lower(),
                " ".join(track.get("artists", [])).lower(),
                track.get("album", "").lower()
            ])
            
            if query in searchable_text:
                results.append(track)
        
        return results


def show_personal_library(config: Config) -> None:
    """Show the personal music library."""
    library_manager = PersonalLibrary(config)
    library = library_manager.load_library()
    
    console.print(Panel(
        f"[bold green]🎵 Personal Music Library[/bold green]\n\n"
        f"Total tracks: {len(library['tracks'])}\n"
        f"Playlists: {len(library['playlists'])}\n"
        f"Favorites: {len(library['favorites'])}\n"
        f"Last updated: {library['metadata'].get('last_updated', 'Never')[:19]}",
        title="Library Overview",
        border_style="green"
    ))
    
    if not library["tracks"]:
        console.print("[yellow]Your library is empty. Add some tracks to get started![/yellow]")
        console.print("\nYou can add tracks by:")
        console.print("• Searching Spotify and saving tracks")
        console.print("• Importing from playlists")
        console.print("• Adding tracks manually")
        input("\n[dim]Press Enter to continue...[/dim]")
        return
    
    from ..menu import Menu
    
    menu = Menu("🎵 Personal Library")
    
    menu.add_item(
        "View All Tracks",
        lambda: view_all_tracks(library_manager),
        f"Browse all {len(library['tracks'])} tracks in your library",
        "1"
    )
    
    menu.add_item(
        "Search Library",
        lambda: search_library_interactive(library_manager),
        "Search your library by title, artist, or album",
        "2"
    )
    
    menu.add_item(
        "View Favorites",
        lambda: view_favorites(library_manager),
        f"View your {len(library['favorites'])} favorite tracks",
        "3"
    )
    
    menu.add_item(
        "Manage Playlists",
        lambda: manage_library_playlists(library_manager),
        "Create and manage personal playlists",
        "4"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Add Track Manually",
        lambda: add_track_manually(library_manager),
        "Add a track by entering details manually",
        "5"
    )
    
    menu.add_item(
        "Import from Spotify",
        lambda: import_from_spotify(library_manager, config),
        "Import tracks from your Spotify library",
        "6"
    )
    
    menu.add_item(
        "Library Statistics",
        lambda: show_library_statistics(library_manager),
        "View detailed statistics about your library",
        "7"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Export Library",
        lambda: export_library_menu(library_manager),
        "Export your library to various formats",
        "8"
    )
    
    menu.add_item(
        "Clean Library",
        lambda: clean_library(library_manager),
        "Remove duplicates and fix issues",
        "9"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Back to Songs Menu",
        lambda: setattr(menu, 'running', False),
        "Return to songs menu",
        "b"
    )
    
    menu.run()


def view_all_tracks(library_manager: PersonalLibrary) -> None:
    """View all tracks in the library."""
    library = library_manager.load_library()
    tracks = library["tracks"]
    
    if not tracks:
        console.print("[yellow]No tracks in library[/yellow]")
        return
    
    # Sort tracks by date added (newest first)
    tracks_sorted = sorted(tracks, key=lambda x: x.get("added_date", ""), reverse=True)
    
    display_tracks_table(tracks_sorted, "Your Personal Library")
    
    # Interactive options
    while True:
        choice = console.input(
            "\n[dim]Enter track number for options, 's' to search, 'f' to filter, or Enter to go back: [/dim]"
        ).strip().lower()
        
        if not choice:
            break
        elif choice == 's':
            search_library_interactive(library_manager)
            break
        elif choice == 'f':
            filter_library_tracks(library_manager)
            break
        else:
            try:
                track_num = int(choice) - 1
                if 0 <= track_num < len(tracks_sorted):
                    show_track_options(tracks_sorted[track_num], library_manager)
                    # Refresh the view
                    library = library_manager.load_library()
                    tracks_sorted = sorted(library["tracks"], key=lambda x: x.get("added_date", ""), reverse=True)
                    display_tracks_table(tracks_sorted, "Your Personal Library")
                else:
                    console.print("[red]Invalid track number[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")


def search_library_interactive(library_manager: PersonalLibrary) -> None:
    """Interactive library search."""
    query = Prompt.ask("\n[bold]Enter search query[/bold]")
    if not query.strip():
        console.print("[yellow]No search query provided[/yellow]")
        return
    
    results = library_manager.search_library(query)
    
    if results:
        display_tracks_table(results, f"Search Results for '{query}'")
        
        # Allow interaction with results
        while True:
            choice = console.input(
                "\n[dim]Enter track number for options, or Enter to go back: [/dim]"
            ).strip()
            
            if not choice:
                break
            
            try:
                track_num = int(choice) - 1
                if 0 <= track_num < len(results):
                    show_track_options(results[track_num], library_manager)
                else:
                    console.print("[red]Invalid track number[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
    else:
        console.print(f"[yellow]No tracks found matching '{query}'[/yellow]")


def show_track_options(track: Dict[str, Any], library_manager: PersonalLibrary) -> None:
    """Show options for a specific track."""
    from ..menu import Menu
    
    track_name = track.get("name", "Unknown Track")
    artists = ", ".join(track.get("artists", ["Unknown Artist"]))
    
    menu = Menu(f"Options for '{track_name}' by {artists}")
    
    library = library_manager.load_library()
    is_favorite = track.get("id") in library.get("favorites", [])
    
    if is_favorite:
        menu.add_item(
            "Remove from Favorites",
            lambda: toggle_favorite(track, library_manager, False),
            "Remove this track from your favorites",
            "1"
        )
    else:
        menu.add_item(
            "Add to Favorites",
            lambda: toggle_favorite(track, library_manager, True),
            "Add this track to your favorites",
            "1"
        )
    
    menu.add_item(
        "Add to Playlist",
        lambda: add_to_playlist_interactive(track, library_manager),
        "Add this track to one of your playlists",
        "2"
    )
    
    menu.add_item(
        "View Track Details",
        lambda: show_track_details(track),
        "Show detailed information about this track",
        "3"
    )
    
    menu.add_item(
        "Edit Track Info",
        lambda: edit_track_info(track, library_manager),
        "Edit track title, artist, or other information",
        "4"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Remove from Library",
        lambda: remove_track_from_library(track, library_manager),
        "Permanently remove this track from your library",
        "r"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Back",
        lambda: setattr(menu, 'running', False),
        "Return to library view",
        "b"
    )
    
    menu.run()


def add_to_library(track: Dict[str, Any], config: Config) -> bool:
    """Add a track to the personal library."""
    library_manager = PersonalLibrary(config)
    
    if library_manager.add_track(track):
        console.print(f"[green]Added '{track.get('name')}' to your library![/green]")
        return True
    else:
        return False


def remove_from_library(track_id: str, config: Config) -> bool:
    """Remove a track from the personal library."""
    library_manager = PersonalLibrary(config)
    
    if library_manager.remove_track(track_id):
        console.print("[green]Track removed from library[/green]")
        return True
    else:
        return False


def toggle_favorite(track: Dict[str, Any], library_manager: PersonalLibrary, add: bool) -> None:
    """Toggle favorite status of a track."""
    library = library_manager.load_library()
    track_id = track.get("id")
    
    if not track_id:
        console.print("[red]Cannot favorite track without ID[/red]")
        return
    
    if add:
        if track_id not in library["favorites"]:
            library["favorites"].append(track_id)
            library_manager.save_library(library)
            console.print(f"[green]Added '{track.get('name')}' to favorites![/green]")
        else:
            console.print("[yellow]Track already in favorites[/yellow]")
    else:
        if track_id in library["favorites"]:
            library["favorites"].remove(track_id)
            library_manager.save_library(library)
            console.print(f"[green]Removed '{track.get('name')}' from favorites[/green]")
        else:
            console.print("[yellow]Track not in favorites[/yellow]")


def view_favorites(library_manager: PersonalLibrary) -> None:
    """View favorite tracks."""
    library = library_manager.load_library()
    favorite_ids = library.get("favorites", [])
    
    if not favorite_ids:
        console.print("[yellow]No favorite tracks yet[/yellow]")
        return
    
    # Get full track info for favorites
    favorite_tracks = []
    for track in library["tracks"]:
        if track.get("id") in favorite_ids:
            favorite_tracks.append(track)
    
    if favorite_tracks:
        display_tracks_table(favorite_tracks, "Your Favorite Tracks")
    else:
        console.print("[yellow]Favorite tracks not found in library[/yellow]")


def add_track_manually(library_manager: PersonalLibrary) -> None:
    """Add a track manually by entering details."""
    console.print(Panel(
        "[bold blue]🎵 Add Track Manually[/bold blue]\n\n"
        "Enter track details to add to your personal library.",
        title="Manual Entry",
        border_style="blue"
    ))
    
    name = Prompt.ask("\n[bold]Track name[/bold]")
    if not name.strip():
        console.print("[yellow]Track name is required[/yellow]")
        return
    
    artists_input = Prompt.ask("Artist(s) (separate multiple with comma)")
    artists = [a.strip() for a in artists_input.split(",") if a.strip()]
    
    album = Prompt.ask("Album name (optional)", default="")
    year = Prompt.ask("Release year (optional)", default="")
    genre = Prompt.ask("Genre (optional)", default="")
    
    # Create track object
    track = {
        "id": f"manual_{datetime.now().timestamp()}",
        "name": name,
        "artists": artists,
        "album": album,
        "year": year,
        "genre": genre,
        "duration_ms": 0,  # Unknown
        "popularity": 0,   # Unknown
        "source": "manual"
    }
    
    if library_manager.add_track(track):
        console.print(f"[green]Successfully added '{name}' to your library![/green]")
    else:
        console.print("[red]Failed to add track to library[/red]")


def import_from_spotify(library_manager: PersonalLibrary, config: Config) -> None:
    """Import tracks from Spotify."""
    if not validate_spotify_config(config):
        console.print("[red]Spotify API not configured[/red]")
        return
    
    console.print("[blue]Importing from Spotify - Feature coming soon[/blue]")
    console.print("[dim]This will allow you to import your saved tracks, recently played, etc.[/dim]")


def show_library_statistics(library_manager: PersonalLibrary) -> None:
    """Show library statistics."""
    library = library_manager.load_library()
    tracks = library["tracks"]
    
    if not tracks:
        console.print("[yellow]No tracks to analyze[/yellow]")
        return
    
    # Calculate statistics
    total_tracks = len(tracks)
    total_duration = sum(track.get("duration_ms", 0) for track in tracks)
    total_hours = total_duration / (1000 * 60 * 60)
    
    # Artist frequency
    artist_count = {}
    for track in tracks:
        for artist in track.get("artists", []):
            artist_count[artist] = artist_count.get(artist, 0) + 1
    
    top_artists = sorted(artist_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Source distribution
    source_count = {}
    for track in tracks:
        source = track.get("source", "unknown")
        source_count[source] = source_count.get(source, 0) + 1
    
    # Display statistics
    stats_table = Table(title="Personal Library Statistics", border_style="cyan")
    stats_table.add_column("Metric", style="bold")
    stats_table.add_column("Value", justify="right")
    
    stats_table.add_row("Total Tracks", str(total_tracks))
    stats_table.add_row("Favorites", str(len(library.get("favorites", []))))
    stats_table.add_row("Playlists", str(len(library.get("playlists", []))))
    
    if total_duration > 0:
        stats_table.add_row("Total Duration", f"{total_hours:.1f} hours")
        stats_table.add_row("Average Track Length", f"{total_duration / total_tracks / 1000 / 60:.1f} minutes")
    
    console.print(stats_table)
    
    # Top artists
    if top_artists:
        console.print("\n[bold]Top Artists in Library:[/bold]")
        for i, (artist, count) in enumerate(top_artists, 1):
            console.print(f"{i:2d}. {artist} ({count} tracks)")
    
    # Source distribution
    if source_count:
        console.print("\n[bold]Sources:[/bold]")
        for source, count in source_count.items():
            console.print(f"• {source.title()}: {count} tracks")


def clean_library(library_manager: PersonalLibrary) -> None:
    """Clean the library by removing duplicates and fixing issues."""
    console.print("[blue]Cleaning library - Feature coming soon[/blue]")


def export_library_menu(library_manager: PersonalLibrary) -> None:
    """Export library menu."""
    console.print("[blue]Library export - Feature coming soon[/blue]")


def show_track_details(track: Dict[str, Any]) -> None:
    """Show detailed information about a track."""
    details_table = Table(title=f"Details for '{track.get('name', 'Unknown')}'", border_style="blue")
    details_table.add_column("Property", style="bold")
    details_table.add_column("Value")
    
    details_table.add_row("Name", track.get("name", "Unknown"))
    details_table.add_row("Artists", ", ".join(track.get("artists", ["Unknown"])))
    details_table.add_row("Album", track.get("album", "Unknown"))
    details_table.add_row("Duration", f"{track.get('duration_ms', 0) / 1000 / 60:.2f} minutes")
    details_table.add_row("Popularity", f"{track.get('popularity', 'Unknown')}/100")
    details_table.add_row("Source", track.get("source", "Unknown").title())
    details_table.add_row("Added Date", track.get("added_date", "Unknown")[:19])
    
    if track.get("year"):
        details_table.add_row("Year", str(track.get("year")))
    if track.get("genre"):
        details_table.add_row("Genre", track.get("genre"))
    
    console.print(details_table)
    input("\n[dim]Press Enter to continue...[/dim]")


def edit_track_info(track: Dict[str, Any], library_manager: PersonalLibrary) -> None:
    """Edit track information."""
    console.print("[blue]Track editing - Feature coming soon[/blue]")


def remove_track_from_library(track: Dict[str, Any], library_manager: PersonalLibrary) -> None:
    """Remove a track from the library."""
    track_name = track.get("name", "Unknown")
    
    if Confirm.ask(f"Are you sure you want to remove '{track_name}' from your library?"):
        if library_manager.remove_track(track.get("id")):
            console.print(f"[green]Removed '{track_name}' from library[/green]")
        else:
            console.print("[red]Failed to remove track[/red]")


def add_to_playlist_interactive(track: Dict[str, Any], library_manager: PersonalLibrary) -> None:
    """Add track to playlist interactively."""
    console.print("[blue]Playlist management - Feature coming soon[/blue]")


def manage_library_playlists(library_manager: PersonalLibrary) -> None:
    """Manage library playlists."""
    console.print("[blue]Library playlist management - Feature coming soon[/blue]")


def filter_library_tracks(library_manager: PersonalLibrary) -> None:
    """Filter library tracks by various criteria."""
    console.print("[blue]Library filtering - Feature coming soon[/blue]") 