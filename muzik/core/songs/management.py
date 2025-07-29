"""
Song management and utility functions.
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, TaskID

from ..config import Config
from ..spotify.auth import validate_spotify_config
from ..spotify.client import SpotifyAPI
from .library import PersonalLibrary

console = Console()


def show_management_menu(config: Config) -> None:
    """Show the song management menu."""
    from ..menu import Menu
    
    menu = Menu("🎵 Song Management")
    
    # Playlist management
    menu.add_item(
        "Create Playlist",
        lambda: create_playlist_menu(config),
        "Create a new playlist (Spotify or local)",
        "1"
    )
    
    menu.add_item(
        "Delete Playlist",
        lambda: delete_playlist_menu(config),
        "Delete an existing playlist",
        "2"
    )
    
    menu.add_item(
        "Merge Playlists",
        lambda: merge_playlists_menu(config),
        "Combine multiple playlists into one",
        "3"
    )
    
    menu.add_separator()
    
    # Data management
    menu.add_item(
        "Export Data",
        lambda: export_data_menu(config),
        "Export your music data to various formats",
        "4"
    )
    
    menu.add_item(
        "Import Data",
        lambda: import_data_menu(config),
        "Import music data from external sources",
        "5"
    )
    
    menu.add_item(
        "Backup Library",
        lambda: backup_library(config),
        "Create a backup of your personal library",
        "6"
    )
    
    menu.add_item(
        "Restore Library",
        lambda: restore_library_menu(config),
        "Restore your library from a backup",
        "7"
    )
    
    menu.add_separator()
    
    # Utilities
    menu.add_item(
        "Library Statistics",
        lambda: show_advanced_statistics(config),
        "View detailed statistics and analytics",
        "8"
    )
    
    menu.add_item(
        "Duplicate Finder",
        lambda: find_duplicates_menu(config),
        "Find and manage duplicate tracks",
        "9"
    )
    
    menu.add_item(
        "Data Cleanup",
        lambda: cleanup_data_menu(config),
        "Clean up and optimize your music data",
        "10"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Back to Songs Menu",
        lambda: setattr(menu, 'running', False),
        "Return to songs menu",
        "b"
    )
    
    menu.run()


def create_playlist_menu(config: Config) -> None:
    """Menu for creating playlists."""
    from ..menu import Menu
    
    menu = Menu("🎵 Create Playlist")
    
    if validate_spotify_config(config):
        menu.add_item(
            "Create Spotify Playlist",
            lambda: create_spotify_playlist(config),
            "Create a new playlist on Spotify",
            "1"
        )
        
        menu.add_item(
            "Create from Library",
            lambda: create_playlist_from_library(config),
            "Create a Spotify playlist from your personal library",
            "2"
        )
        
        menu.add_separator()
    
    menu.add_item(
        "Create Local Playlist",
        lambda: create_local_playlist(config),
        "Create a local playlist file",
        "3" if validate_spotify_config(config) else "1"
    )
    
    menu.add_item(
        "Smart Playlist",
        lambda: create_smart_playlist(config),
        "Create a playlist based on criteria",
        "4" if validate_spotify_config(config) else "2"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Back",
        lambda: setattr(menu, 'running', False),
        "Return to management menu",
        "b"
    )
    
    menu.run()


def create_playlist(name: str, tracks: List[Dict[str, Any]], config: Config) -> bool:
    """Create a new playlist."""
    if validate_spotify_config(config):
        try:
            spotify = SpotifyAPI(config)
            
            # Create the playlist
            playlist = spotify.create_playlist(name, f"Created by Muzik on {datetime.now().strftime('%Y-%m-%d')}")
            
            if playlist and tracks:
                # Add tracks to the playlist
                track_ids = [track.get('id') for track in tracks if track.get('id')]
                if track_ids:
                    spotify.add_tracks_to_playlist(playlist['id'], track_ids)
            
            console.print(f"[green]Successfully created playlist '{name}' with {len(tracks)} tracks![/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error creating playlist: {e}[/red]")
            return False
    else:
        # Create local playlist
        return create_local_playlist_file(name, tracks, config)


def delete_playlist(playlist_id: str, config: Config) -> bool:
    """Delete a playlist."""
    if validate_spotify_config(config):
        try:
            spotify = SpotifyAPI(config)
            
            # First get playlist info
            playlist = spotify.get_playlist(playlist_id)
            if not playlist:
                console.print("[red]Playlist not found[/red]")
                return False
            
            # Confirm deletion
            if not Confirm.ask(f"Are you sure you want to delete playlist '{playlist['name']}'?"):
                return False
            
            # Note: Spotify API doesn't allow deleting playlists, only unfollowing
            if spotify.unfollow_playlist(playlist_id):
                console.print(f"[green]Unfollowed playlist '{playlist['name']}'[/green]")
                return True
            else:
                console.print("[red]Failed to unfollow playlist[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error deleting playlist: {e}[/red]")
            return False
    else:
        console.print("[yellow]Local playlist deletion not implemented yet[/yellow]")
        return False


def export_playlist(playlist: Dict[str, Any], format: str, config: Config) -> bool:
    """Export a playlist to various formats."""
    try:
        playlist_name = playlist.get('name', 'Unknown Playlist')
        export_dir = Path.home() / "Music" / "Muzik Exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'json':
            filename = export_dir / f"{playlist_name}.json"
            with open(filename, 'w') as f:
                json.dump(playlist, f, indent=2)
                
        elif format.lower() == 'csv':
            filename = export_dir / f"{playlist_name}.csv"
            
            # Get tracks if not included
            tracks = playlist.get('tracks', [])
            if not tracks and validate_spotify_config(config):
                spotify = SpotifyAPI(config)
                tracks = spotify.get_playlist_tracks(playlist.get('id'))
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Artists', 'Album', 'Duration (ms)', 'Popularity'])
                
                for track in tracks:
                    writer.writerow([
                        track.get('name', ''),
                        ', '.join(track.get('artists', [])),
                        track.get('album', ''),
                        track.get('duration_ms', ''),
                        track.get('popularity', '')
                    ])
        
        elif format.lower() == 'm3u':
            filename = export_dir / f"{playlist_name}.m3u"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                tracks = playlist.get('tracks', [])
                for track in tracks:
                    duration = track.get('duration_ms', 0) // 1000
                    artists = ', '.join(track.get('artists', []))
                    name = track.get('name', '')
                    f.write(f"#EXTINF:{duration},{artists} - {name}\n")
                    # Note: We don't have actual file paths, so this is mainly for metadata
                    f.write(f"# Spotify ID: {track.get('id', 'unknown')}\n")
        
        console.print(f"[green]Exported '{playlist_name}' to {filename}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error exporting playlist: {e}[/red]")
        return False


def create_spotify_playlist(config: Config) -> None:
    """Create a new Spotify playlist."""
    console.print(Panel(
        "[bold green]🎵 Create Spotify Playlist[/bold green]\n\n"
        "Create a new playlist in your Spotify account.",
        title="Spotify Playlist",
        border_style="green"
    ))
    
    name = Prompt.ask("\n[bold]Playlist name[/bold]")
    if not name.strip():
        console.print("[yellow]Playlist name is required[/yellow]")
        return
    
    description = Prompt.ask("Description (optional)", default=f"Created by Muzik on {datetime.now().strftime('%Y-%m-%d')}")
    public = Confirm.ask("Make playlist public?", default=False)
    
    try:
        spotify = SpotifyAPI(config)
        playlist = spotify.create_playlist(name, description, public)
        
        if playlist:
            console.print(f"[green]Successfully created playlist '{name}'![/green]")
            console.print(f"Playlist URL: https://open.spotify.com/playlist/{playlist['id']}")
            
            # Ask if user wants to add tracks
            if Confirm.ask("Do you want to add tracks now?"):
                add_tracks_to_spotify_playlist(playlist, config)
        else:
            console.print("[red]Failed to create playlist[/red]")
            
    except Exception as e:
        console.print(f"[red]Error creating playlist: {e}[/red]")


def add_tracks_to_spotify_playlist(playlist: Dict[str, Any], config: Config) -> None:
    """Add tracks to a Spotify playlist interactively."""
    console.print(f"[blue]Adding tracks to '{playlist['name']}'...[/blue]")
    
    try:
        spotify = SpotifyAPI(config)
        track_uris = []
        
        while True:
            search_type = Prompt.ask(
                "\nHow do you want to add tracks?",
                choices=["search", "library", "done"],
                default="search"
            )
            
            if search_type == "done":
                break
            elif search_type == "search":
                query = Prompt.ask("Search for tracks")
                if query:
                    tracks = spotify.search_tracks(query, limit=10)
                    if tracks:
                        from ..spotify.display import display_tracks_table
                        display_tracks_table(tracks, f"Search results for '{query}'")
                        
                        try:
                            choice = IntPrompt.ask("Select track number (0 to skip)")
                            if 1 <= choice <= len(tracks):
                                track = tracks[choice - 1]
                                track_uris.append(track['uri'])
                                console.print(f"[green]Added '{track['name']}'[/green]")
                        except (ValueError, KeyboardInterrupt):
                            continue
                    else:
                        console.print("[yellow]No tracks found[/yellow]")
                        
            elif search_type == "library":
                library_manager = PersonalLibrary(config)
                library = library_manager.load_library()
                
                if library["tracks"]:
                    from ..spotify.display import display_tracks_table
                    display_tracks_table(library["tracks"][:20], "Your Library (first 20)")
                    
                    try:
                        choice = IntPrompt.ask("Select track number (0 to skip)")
                        if 1 <= choice <= len(library["tracks"][:20]):
                            track = library["tracks"][choice - 1]
                            if track.get('uri'):
                                track_uris.append(track['uri'])
                                console.print(f"[green]Added '{track['name']}'[/green]")
                            else:
                                console.print("[yellow]Track doesn't have Spotify URI[/yellow]")
                    except (ValueError, KeyboardInterrupt):
                        continue
                else:
                    console.print("[yellow]Your library is empty[/yellow]")
        
        # Add all selected tracks
        if track_uris:
            spotify.add_tracks_to_playlist(playlist['id'], track_uris)
            console.print(f"[green]Successfully added {len(track_uris)} tracks to '{playlist['name']}'![/green]")
        else:
            console.print("[yellow]No tracks were added[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error adding tracks: {e}[/red]")


def create_playlist_from_library(config: Config) -> None:
    """Create a Spotify playlist from personal library."""
    library_manager = PersonalLibrary(config)
    library = library_manager.load_library()
    
    if not library["tracks"]:
        console.print("[yellow]Your personal library is empty[/yellow]")
        return
    
    console.print(Panel(
        f"[bold blue]🎵 Create Playlist from Library[/bold blue]\n\n"
        f"You have {len(library['tracks'])} tracks in your library.\n"
        "You can create a playlist with all tracks or filter by criteria.",
        title="Library to Playlist",
        border_style="blue"
    ))
    
    name = Prompt.ask("\n[bold]Playlist name[/bold]")
    if not name.strip():
        console.print("[yellow]Playlist name is required[/yellow]")
        return
    
    # Filter options
    filter_type = Prompt.ask(
        "Filter tracks?",
        choices=["all", "favorites", "artist", "recent"],
        default="all"
    )
    
    tracks = library["tracks"]
    
    if filter_type == "favorites":
        favorite_ids = library.get("favorites", [])
        tracks = [t for t in tracks if t.get("id") in favorite_ids]
    elif filter_type == "artist":
        artist = Prompt.ask("Artist name to filter by")
        tracks = [t for t in tracks if any(artist.lower() in a.lower() for a in t.get("artists", []))]
    elif filter_type == "recent":
        # Get tracks added in last 30 days
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        tracks = [t for t in tracks if t.get("added_date", "") > cutoff]
    
    if not tracks:
        console.print("[yellow]No tracks match your filter criteria[/yellow]")
        return
    
    console.print(f"[blue]Creating playlist with {len(tracks)} tracks...[/blue]")
    
    # Filter out tracks without Spotify IDs
    spotify_tracks = [t for t in tracks if t.get("id") and not t.get("id", "").startswith("manual_")]
    
    if create_playlist(name, spotify_tracks, config):
        console.print(f"[green]Successfully created playlist '{name}' with {len(spotify_tracks)} tracks![/green]")
        if len(spotify_tracks) < len(tracks):
            console.print(f"[yellow]Note: {len(tracks) - len(spotify_tracks)} tracks were skipped (no Spotify ID)[/yellow]")


def create_local_playlist(config: Config) -> None:
    """Create a local playlist file."""
    console.print("[blue]Local playlist creation - Feature coming soon[/blue]")


def create_local_playlist_file(name: str, tracks: List[Dict[str, Any]], config: Config) -> bool:
    """Create a local playlist file."""
    try:
        playlist_dir = Path.home() / "Music" / "Muzik Playlists"
        playlist_dir.mkdir(parents=True, exist_ok=True)
        
        filename = playlist_dir / f"{name}.json"
        
        playlist_data = {
            "name": name,
            "created": datetime.now().isoformat(),
            "tracks": tracks,
            "type": "local"
        }
        
        with open(filename, 'w') as f:
            json.dump(playlist_data, f, indent=2)
        
        console.print(f"[green]Created local playlist '{name}' at {filename}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error creating local playlist: {e}[/red]")
        return False


def create_smart_playlist(config: Config) -> None:
    """Create a smart playlist based on criteria."""
    console.print("[blue]Smart playlist creation - Feature coming soon[/blue]")


def delete_playlist_menu(config: Config) -> None:
    """Menu for deleting playlists."""
    console.print("[blue]Playlist deletion - Feature coming soon[/blue]")


def merge_playlists_menu(config: Config) -> None:
    """Menu for merging playlists."""
    console.print("[blue]Playlist merging - Feature coming soon[/blue]")


def export_data_menu(config: Config) -> None:
    """Menu for exporting data."""
    from ..menu import Menu
    
    menu = Menu("📤 Export Data")
    
    menu.add_item(
        "Export Personal Library",
        lambda: export_personal_library(config),
        "Export your personal library to JSON/CSV",
        "1"
    )
    
    if validate_spotify_config(config):
        menu.add_item(
            "Export Spotify Playlists",
            lambda: export_spotify_playlists(config),
            "Export all your Spotify playlists",
            "2"
        )
        
        menu.add_item(
            "Export Spotify Data",
            lambda: export_all_spotify_data(config),
            "Export all your Spotify data (playlists, saved tracks, etc.)",
            "3"
        )
    
    menu.add_separator()
    
    menu.add_item(
        "Back",
        lambda: setattr(menu, 'running', False),
        "Return to management menu",
        "b"
    )
    
    menu.run()


def import_data_menu(config: Config) -> None:
    """Menu for importing data."""
    console.print("[blue]Data import - Feature coming soon[/blue]")


def backup_library(config: Config) -> None:
    """Create a backup of the personal library."""
    library_manager = PersonalLibrary(config)
    library = library_manager.load_library()
    
    backup_dir = Path.home() / ".muzik" / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"library_backup_{timestamp}.json"
    
    try:
        with open(backup_file, 'w') as f:
            json.dump(library, f, indent=2)
        
        console.print(f"[green]Library backed up to {backup_file}[/green]")
        console.print(f"Backup contains {len(library['tracks'])} tracks")
        
    except Exception as e:
        console.print(f"[red]Error creating backup: {e}[/red]")


def restore_library_menu(config: Config) -> None:
    """Menu for restoring library from backup."""
    console.print("[blue]Library restore - Feature coming soon[/blue]")


def show_advanced_statistics(config: Config) -> None:
    """Show advanced statistics and analytics."""
    console.print("[blue]Advanced statistics - Feature coming soon[/blue]")


def find_duplicates_menu(config: Config) -> None:
    """Menu for finding duplicate tracks."""
    console.print("[blue]Duplicate finder - Feature coming soon[/blue]")


def cleanup_data_menu(config: Config) -> None:
    """Menu for data cleanup utilities."""
    console.print("[blue]Data cleanup - Feature coming soon[/blue]")


def export_personal_library(config: Config) -> None:
    """Export personal library to file."""
    library_manager = PersonalLibrary(config)
    library = library_manager.load_library()
    
    if not library["tracks"]:
        console.print("[yellow]Your library is empty, nothing to export[/yellow]")
        return
    
    format_choice = Prompt.ask(
        "Export format",
        choices=["json", "csv"],
        default="json"
    )
    
    export_dir = Path.home() / "Music" / "Muzik Exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        if format_choice == "json":
            filename = export_dir / f"muzik_library_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(library, f, indent=2)
                
        elif format_choice == "csv":
            filename = export_dir / f"muzik_library_{timestamp}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Artists', 'Album', 'Duration (ms)', 'Added Date', 'Source', 'Favorite'])
                
                favorites = library.get("favorites", [])
                for track in library["tracks"]:
                    writer.writerow([
                        track.get('name', ''),
                        ', '.join(track.get('artists', [])),
                        track.get('album', ''),
                        track.get('duration_ms', ''),
                        track.get('added_date', ''),
                        track.get('source', ''),
                        'Yes' if track.get('id') in favorites else 'No'
                    ])
        
        console.print(f"[green]Exported {len(library['tracks'])} tracks to {filename}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error exporting library: {e}[/red]")


def export_spotify_playlists(config: Config) -> None:
    """Export all Spotify playlists."""
    if not validate_spotify_config(config):
        console.print("[red]Spotify API not configured[/red]")
        return
    
    console.print("[blue]Exporting Spotify playlists...[/blue]")
    
    try:
        spotify = SpotifyAPI(config)
        playlists = spotify.get_user_playlists()
        
        if not playlists:
            console.print("[yellow]No playlists found[/yellow]")
            return
        
        export_dir = Path.home() / "Music" / "Muzik Exports" / "Spotify Playlists"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        with Progress() as progress:
            task = progress.add_task("Exporting playlists...", total=len(playlists))
            
            for playlist in playlists:
                # Get full playlist data including tracks
                full_playlist = spotify.get_playlist(playlist['id'])
                tracks = spotify.get_playlist_tracks(playlist['id'])
                full_playlist['tracks'] = tracks
                
                # Export to JSON
                filename = export_dir / f"{playlist['name']}.json"
                with open(filename, 'w') as f:
                    json.dump(full_playlist, f, indent=2)
                
                progress.advance(task)
        
        console.print(f"[green]Exported {len(playlists)} playlists to {export_dir}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error exporting playlists: {e}[/red]")


def export_all_spotify_data(config: Config) -> None:
    """Export all Spotify data."""
    console.print("[blue]Complete Spotify data export - Feature coming soon[/blue]") 