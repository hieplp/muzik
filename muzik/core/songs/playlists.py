"""
Playlist management functionality.
"""

from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table

from ..config import Config
from ..spotify.api.auth import validate_spotify_config
from ..spotify.api.client import SpotifyAPI
from ..spotify.display import display_tracks_table, display_playlists_table

console = Console()


def show_spotify_playlists(config: Config) -> None:
    """Show user's Spotify playlists."""
    if not validate_spotify_config(config):
        console.print("[red]Spotify API not configured. Please configure in Settings.[/red]")
        return

    console.print("[blue]Loading your Spotify playlists...[/blue]")

    try:
        spotify = SpotifyAPI(config)
        playlists = spotify.get_user_playlists()

        if not playlists:
            console.print("[yellow]No playlists found in your Spotify account[/yellow]")
            return

        display_playlists_table(playlists, "Your Spotify Playlists")

        # Interactive playlist selection
        while True:
            choice = console.input(
                "\n[dim]Enter playlist number to view tracks, 'r' to refresh, or Enter to go back: [/dim]"
            ).strip().lower()

            if not choice:
                break
            elif choice == 'r':
                console.print("[blue]Refreshing playlists...[/blue]")
                playlists = spotify.get_user_playlists()
                display_playlists_table(playlists, "Your Spotify Playlists")
            else:
                try:
                    playlist_num = int(choice) - 1
                    if 0 <= playlist_num < len(playlists):
                        show_playlist_tracks(playlists[playlist_num], config)
                    else:
                        console.print("[red]Invalid playlist number[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")

    except Exception as e:
        console.print(f"[red]Error loading playlists: {e}[/red]")


def show_playlist_tracks(playlist: Dict[str, Any], config: Config) -> None:
    """Show tracks in a specific playlist."""
    console.print(f"[blue]Loading tracks from '{playlist['name']}'...[/blue]")

    try:
        spotify = SpotifyAPI(config)
        tracks = spotify.get_playlist_tracks(playlist['id'])

        if not tracks:
            console.print("[yellow]No tracks found in this playlist[/yellow]")
            return

        # Display playlist info
        console.print(Panel(
            f"[bold]{playlist['name']}[/bold]\n"
            f"Description: {playlist.get('description', 'No description')[:100]}...\n"
            f"Total tracks: {playlist.get('tracks', {}).get('total', len(tracks))}\n"
            f"Owner: {playlist.get('owner', {}).get('display_name', 'Unknown')}\n"
            f"Public: {'Yes' if playlist.get('public') else 'No'}",
            title=f"🎵 {playlist['name']}",
            border_style="green"
        ))

        display_tracks_table(tracks, f"Tracks in '{playlist['name']}'")

        # Playlist actions menu
        show_playlist_actions_menu(playlist, tracks, config)

    except Exception as e:
        console.print(f"[red]Error loading playlist tracks: {e}[/red]")


def show_playlist_actions_menu(playlist: Dict[str, Any], tracks: List[Dict[str, Any]], config: Config) -> None:
    """Show actions menu for a playlist."""
    from ..menu import Menu

    menu = Menu(f"Actions for '{playlist['name']}'")

    menu.add_item(
        "Play All",
        lambda: console.print("[blue]Playing all tracks... (Feature coming soon)[/blue]"),
        "Play all tracks in this playlist",
        "1"
    )

    menu.add_item(
        "Shuffle Play",
        lambda: console.print("[blue]Shuffling and playing... (Feature coming soon)[/blue]"),
        "Play tracks in random order",
        "2"
    )

    menu.add_item(
        "Copy to Personal Library",
        lambda: copy_playlist_to_library(playlist, tracks, config),
        "Copy all tracks to your personal library",
        "3"
    )

    menu.add_item(
        "Export Playlist",
        lambda: export_playlist_menu(playlist, tracks, config),
        "Export playlist to various formats",
        "4"
    )

    menu.add_item(
        "Playlist Statistics",
        lambda: show_playlist_statistics(playlist, tracks),
        "Show detailed playlist statistics",
        "5"
    )

    menu.add_separator()

    menu.add_item(
        "Back to Playlist",
        lambda: setattr(menu, 'running', False),
        "Return to playlist view",
        "b"
    )

    menu.run()


def manage_playlists(config: Config) -> None:
    """Playlist management menu."""
    from ..menu import Menu

    menu = Menu("🎵 Playlist Management")

    if validate_spotify_config(config):
        menu.add_item(
            "View My Playlists",
            lambda: show_spotify_playlists(config),
            "View and interact with your Spotify playlists",
            "1"
        )

        menu.add_item(
            "Create New Playlist",
            lambda: create_spotify_playlist(config),
            "Create a new playlist on Spotify",
            "2"
        )

        menu.add_item(
            "Follow Playlist",
            lambda: follow_playlist(config),
            "Follow a public playlist by URL or ID",
            "3"
        )

        menu.add_separator()

    menu.add_item(
        "Local Playlists",
        lambda: manage_local_playlists(config),
        "Manage local playlist files",
        "4" if validate_spotify_config(config) else "1"
    )

    menu.add_item(
        "Import Playlist",
        lambda: import_playlist_menu(config),
        "Import playlists from various sources",
        "5" if validate_spotify_config(config) else "2"
    )

    menu.add_item(
        "Export Playlists",
        lambda: export_all_playlists_menu(config),
        "Export all playlists to various formats",
        "6" if validate_spotify_config(config) else "3"
    )

    menu.add_separator()

    menu.add_item(
        "Back to Songs Menu",
        lambda: setattr(menu, 'running', False),
        "Return to songs menu",
        "b"
    )

    menu.run()


def create_spotify_playlist(config: Config) -> None:
    """Create a new Spotify playlist."""
    console.print(Panel(
        "[bold green]🎵 Create New Spotify Playlist[/bold green]\n\n"
        "Create a new playlist in your Spotify account.",
        title="Create Playlist",
        border_style="green"
    ))

    name = Prompt.ask("\n[bold]Playlist name[/bold]")
    if not name.strip():
        console.print("[yellow]Playlist name is required[/yellow]")
        return

    description = Prompt.ask("Playlist description (optional)", default="")
    public = Confirm.ask("Make playlist public?", default=False)

    try:
        spotify = SpotifyAPI(config)
        playlist = spotify.create_playlist(name, description, public)

        if playlist:
            console.print(f"[green]Successfully created playlist '{name}'![/green]")
            console.print(f"Playlist ID: {playlist.get('id')}")

            # Ask if user wants to add tracks
            if Confirm.ask("Do you want to add tracks to this playlist now?"):
                add_tracks_to_playlist(playlist, config)
        else:
            console.print("[red]Failed to create playlist[/red]")

    except Exception as e:
        console.print(f"[red]Error creating playlist: {e}[/red]")


def add_tracks_to_playlist(playlist: Dict[str, Any], config: Config) -> None:
    """Add tracks to a playlist interactively."""
    console.print(f"[blue]Adding tracks to '{playlist['name']}'...[/blue]")

    try:
        spotify = SpotifyAPI(config)
        track_ids = []

        while True:
            query = Prompt.ask("\nSearch for a track to add (or Enter to finish)")
            if not query.strip():
                break

            tracks = spotify.search_tracks(query, limit=10)
            if not tracks:
                console.print("[yellow]No tracks found[/yellow]")
                continue

            display_tracks_table(tracks, f"Search results for '{query}'")

            try:
                choice = IntPrompt.ask("Select track number to add (0 to skip)")
                if 1 <= choice <= len(tracks):
                    track = tracks[choice - 1]
                    track_ids.append(track['id'])
                    console.print(f"[green]Added '{track['name']}' by {', '.join(track['artists'])}[/green]")
            except (ValueError, KeyboardInterrupt):
                continue

        if track_ids:
            spotify.add_tracks_to_playlist(playlist['id'], track_ids)
            console.print(f"[green]Successfully added {len(track_ids)} tracks to '{playlist['name']}'![/green]")
        else:
            console.print("[yellow]No tracks were added[/yellow]")

    except Exception as e:
        console.print(f"[red]Error adding tracks: {e}[/red]")


def follow_playlist(config: Config) -> None:
    """Follow a public playlist."""
    console.print(Panel(
        "[bold blue]🎵 Follow Playlist[/bold blue]\n\n"
        "Follow a public playlist by entering its Spotify URL or ID.",
        title="Follow Playlist",
        border_style="blue"
    ))

    playlist_input = Prompt.ask("\n[bold]Enter playlist URL or ID[/bold]")
    if not playlist_input.strip():
        console.print("[yellow]Playlist URL or ID is required[/yellow]")
        return

    # Extract playlist ID from URL if needed
    playlist_id = extract_playlist_id(playlist_input)
    if not playlist_id:
        console.print("[red]Invalid playlist URL or ID[/red]")
        return

    try:
        spotify = SpotifyAPI(config)

        # Get playlist info first
        playlist = spotify.get_playlist(playlist_id)
        if not playlist:
            console.print("[red]Playlist not found or is private[/red]")
            return

        console.print(Panel(
            f"[bold]{playlist['name']}[/bold]\n"
            f"Owner: {playlist.get('owner', {}).get('display_name', 'Unknown')}\n"
            f"Tracks: {playlist.get('tracks', {}).get('total', 0)}\n"
            f"Description: {playlist.get('description', 'No description')[:100]}...",
            title="Playlist to Follow",
            border_style="blue"
        ))

        if Confirm.ask("Do you want to follow this playlist?"):
            if spotify.follow_playlist(playlist_id):
                console.print(f"[green]Successfully followed '{playlist['name']}'![/green]")
            else:
                console.print("[red]Failed to follow playlist[/red]")

    except Exception as e:
        console.print(f"[red]Error following playlist: {e}[/red]")


def extract_playlist_id(input_str: str) -> Optional[str]:
    """Extract playlist ID from URL or return ID if already an ID."""
    input_str = input_str.strip()

    # If it's a Spotify URL
    if 'spotify.com/playlist/' in input_str:
        try:
            return input_str.split('playlist/')[1].split('?')[0]
        except IndexError:
            return None

    # If it's already an ID (22 characters, alphanumeric)
    if len(input_str) == 22 and input_str.isalnum():
        return input_str

    return None


def copy_playlist_to_library(playlist: Dict[str, Any], tracks: List[Dict[str, Any]], config: Config) -> None:
    """Copy playlist tracks to personal library."""
    console.print(f"[blue]Copying {len(tracks)} tracks from '{playlist['name']}' to library...[/blue]")

    # This would integrate with the library module
    # For now, just show what would be copied
    console.print(f"[green]Would copy {len(tracks)} tracks to personal library[/green]")
    console.print("[dim]Personal library feature coming soon[/dim]")


def show_playlist_statistics(playlist: Dict[str, Any], tracks: List[Dict[str, Any]]) -> None:
    """Show detailed statistics for a playlist."""
    if not tracks:
        console.print("[yellow]No tracks to analyze[/yellow]")
        return

    # Calculate statistics
    total_duration = sum(track.get('duration_ms', 0) for track in tracks)
    total_hours = total_duration / (1000 * 60 * 60)

    # Artist frequency
    artist_count = {}
    for track in tracks:
        for artist in track.get('artists', []):
            artist_count[artist] = artist_count.get(artist, 0) + 1

    top_artists = sorted(artist_count.items(), key=lambda x: x[1], reverse=True)[:5]

    # Display statistics
    stats_table = Table(title=f"Statistics for '{playlist['name']}'", border_style="cyan")
    stats_table.add_column("Metric", style="bold")
    stats_table.add_column("Value", justify="right")

    stats_table.add_row("Total Tracks", str(len(tracks)))
    stats_table.add_row("Total Duration", f"{total_hours:.1f} hours")
    stats_table.add_row("Average Track Length", f"{total_duration / len(tracks) / 1000 / 60:.1f} minutes")

    console.print(stats_table)

    if top_artists:
        console.print("\n[bold]Top Artists:[/bold]")
        for i, (artist, count) in enumerate(top_artists, 1):
            console.print(f"{i}. {artist} ({count} tracks)")


def manage_local_playlists(config: Config) -> None:
    """Manage local playlist files."""
    console.print("[blue]Local playlist management - Feature coming soon[/blue]")


def import_playlist_menu(config: Config) -> None:
    """Import playlists from various sources."""
    console.print("[blue]Playlist import - Feature coming soon[/blue]")


def export_playlist_menu(playlist: Dict[str, Any], tracks: List[Dict[str, Any]], config: Config) -> None:
    """Export a single playlist."""
    console.print(f"[blue]Exporting '{playlist['name']}' - Feature coming soon[/blue]")


def export_all_playlists_menu(config: Config) -> None:
    """Export all playlists."""
    console.print("[blue]Export all playlists - Feature coming soon[/blue]")
