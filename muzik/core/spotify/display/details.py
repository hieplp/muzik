"""
Detail view displays for Spotify data with enhanced track functionality.
"""

from typing import Any, Dict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ....utils.input_utils import get_single_char
from .streaming import SpotifyStreamer

console = Console()


def display_track_details(track: Dict[str, Any]) -> None:
    """
    Display detailed information about a track with streaming options.
    
    Args:
        track: Track dictionary
    """
    def _show_track_info():
        """Display track information."""
        table = Table(title="Track Details", show_header=False, box=None)
        table.add_column("Property", style="bold cyan")
        table.add_column("Value", style="white")
        
        # Basic info
        table.add_row("Title", track.get('name', 'Unknown'))
        table.add_row("Artists", ", ".join(track.get('artists', [])))
        table.add_row("Album", track.get('album', 'Unknown'))
        
        # Format duration
        duration_ms = track.get('duration_ms', 0)
        duration_min = duration_ms // 60000
        duration_sec = (duration_ms % 60000) // 1000
        duration_str = f"{duration_min}:{duration_sec:02d}"
        table.add_row("Duration", duration_str)
        
        # Popularity with bar
        popularity = track.get('popularity', 0)
        popularity_bar = "█" * (popularity // 10) + "░" * (10 - popularity // 10)
        table.add_row("Popularity", f"{popularity}/100 {popularity_bar}")
        
        # Additional details
        if track.get('explicit'):
            table.add_row("Explicit", "Yes")
        
        if track.get('track_number'):
            table.add_row("Track Number", str(track.get('track_number')))
        
        if track.get('disc_number') and track.get('disc_number') > 1:
            table.add_row("Disc Number", str(track.get('disc_number')))
        
        if track.get('external_url'):
            table.add_row("Spotify URL", track.get('external_url'))
        
        if track.get('preview_url'):
            table.add_row("Preview Available", "Yes")
        
        panel = Panel(
            table,
            title="[bold blue]Track Information[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        console.print(panel)
    
    def _show_options_menu(selected_index: int):
        """Display streaming options as a navigable menu."""
        options = [
            ("🎵 Play Preview (30s)", "preview"),
            ("🎧 Play Full Track (Console)", "stream"),
            ("🎤 Show Lyrics", "lyrics"),
            ("🔗 Open in Spotify App/Web", "open"),
            ("⬅️  Back to previous menu", "back")
        ]
        
        options_table = Table(show_header=False, box=None)
        options_table.add_column("Selection", width=3)
        options_table.add_column("Option", style="white")
        
        for i, (option_text, _) in enumerate(options):
            if i == selected_index:
                selection = "▶"
                style = "bold green"
            else:
                selection = " "
                style = "white"
            
            option_display = Text(option_text, style=style)
            options_table.add_row(selection, option_display)
        
        # Add instructions
        instructions = Text()
        instructions.append("↑/↓/WASD: Navigate  ", style="dim")
        instructions.append("Enter: Select  ", style="dim")
        instructions.append("Q: Back", style="dim")
        
        options_panel = Panel(
            options_table,
            title="[bold green]Options[/bold green]",
            subtitle=instructions,
            border_style="green",
            padding=(1, 2)
        )
        
        console.print("\n", options_panel)
        return options
    
    streamer = SpotifyStreamer()
    running = True
    selected_index = 0
    
    try:
        while running:
            console.clear()
            _show_track_info()
            options = _show_options_menu(selected_index)
            
            try:
                char = get_single_char().lower()
                
                if char in ['q']:
                    running = False
                elif char in ['w', 'k', 'up']:  # Up
                    selected_index = (selected_index - 1) % len(options)
                elif char in ['s', 'j', 'down']:  # Down
                    selected_index = (selected_index + 1) % len(options)
                elif char in ['\r', '\n', 'right']:  # Enter
                    option_action = options[selected_index][1]
                    
                    if option_action == "back":
                        running = False
                    elif option_action == "preview":
                        console.print("\n[yellow]Playing preview...[/yellow]")
                        streamer.play_preview(track)
                    elif option_action == "stream":
                        console.print("\n[yellow]Loading full track for console playback...[/yellow]")
                        streamer.stream_full_track(track)
                    elif option_action == "lyrics":
                        console.print("\n[yellow]Fetching lyrics...[/yellow]")
                        streamer.show_lyrics(track)
                    elif option_action == "open":
                        streamer.open_in_spotify(track)
                        console.print("\n[green]Opened in Spotify app/browser[/green]")
                        input("\nPress Enter to continue...")
                else:
                    # Direct key shortcuts (legacy support)
                    if char == 'p':
                        console.print("\n[yellow]Playing preview...[/yellow]")
                        streamer.play_preview(track)
                    elif char == 'l':
                        console.print("\n[yellow]Fetching lyrics...[/yellow]")
                        streamer.show_lyrics(track)
                    elif char == 'o':
                        streamer.open_in_spotify(track)
                        console.print("\n[green]Opened in Spotify app/browser[/green]")
                        input("\nPress Enter to continue...")
                    
            except EOFError:
                running = False
            except KeyboardInterrupt:
                running = False
                
    except KeyboardInterrupt:
        console.print("\n[dim]Returning to previous menu...[/dim]")


def display_playlist_details(playlist: Dict[str, Any]) -> None:
    """
    Display detailed information about a playlist.
    
    Args:
        playlist: Playlist dictionary
    """
    table = Table(title="Playlist Details", show_header=False, box=None)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value", style="white")
    
    # Basic info
    table.add_row("Name", playlist.get('name', 'Unknown'))
    table.add_row("Description", playlist.get('description', 'No description'))
    table.add_row("Owner", playlist.get('owner', 'Unknown'))
    table.add_row("Tracks", str(playlist.get('tracks_count', 0)))
    table.add_row("Public", "Yes" if playlist.get('public', False) else "No")
    table.add_row("Collaborative", "Yes" if playlist.get('collaborative', False) else "No")
    
    if playlist.get('followers'):
        table.add_row("Followers", str(playlist.get('followers')))
    
    if playlist.get('external_url'):
        table.add_row("Spotify URL", playlist.get('external_url'))
    
    panel = Panel(
        table,
        title="[bold blue]Playlist Information[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)


def display_album_details(album: Dict[str, Any]) -> None:
    """
    Display detailed information about an album.
    
    Args:
        album: Album dictionary
    """
    table = Table(title="Album Details", show_header=False, box=None)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value", style="white")
    
    # Basic info
    table.add_row("Name", album.get('name', 'Unknown'))
    table.add_row("Artists", ", ".join(album.get('artists', [])))
    table.add_row("Release Date", album.get('release_date', 'Unknown'))
    table.add_row("Total Tracks", str(album.get('total_tracks', 0)))
    table.add_row("Album Type", album.get('album_type', 'Unknown'))
    
    if album.get('genres'):
        table.add_row("Genres", ", ".join(album.get('genres')))
    
    if album.get('label'):
        table.add_row("Label", album.get('label'))
    
    if album.get('popularity'):
        popularity = album.get('popularity', 0)
        popularity_bar = "█" * (popularity // 10) + "░" * (10 - popularity // 10)
        table.add_row("Popularity", f"{popularity}/100 {popularity_bar}")
    
    if album.get('external_url'):
        table.add_row("Spotify URL", album.get('external_url'))
    
    panel = Panel(
        table,
        title="[bold blue]Album Information[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)


def display_artist_details(artist: Dict[str, Any]) -> None:
    """
    Display detailed information about an artist.
    
    Args:
        artist: Artist dictionary
    """
    table = Table(title="Artist Details", show_header=False, box=None)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value", style="white")
    
    # Basic info
    table.add_row("Name", artist.get('name', 'Unknown'))
    table.add_row("Followers", f"{artist.get('followers', 0):,}")
    
    if artist.get('genres'):
        table.add_row("Genres", ", ".join(artist.get('genres')))
    
    popularity = artist.get('popularity', 0)
    popularity_bar = "█" * (popularity // 10) + "░" * (10 - popularity // 10)
    table.add_row("Popularity", f"{popularity}/100 {popularity_bar}")
    
    if artist.get('external_url'):
        table.add_row("Spotify URL", artist.get('external_url'))
    
    panel = Panel(
        table,
        title="[bold blue]Artist Information[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)