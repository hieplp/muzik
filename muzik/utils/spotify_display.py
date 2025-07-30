"""
Spotify-specific display utilities for interactive tables and data presentation.
"""

from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .input_utils import get_single_char

console = Console()


def display_tracks_table(tracks: List[Dict[str, Any]], title: str = "Tracks") -> None:
    """
    Display tracks in an interactive table with selection capabilities.
    
    Args:
        tracks: List of track dictionaries
        title: Table title
    """
    if not tracks:
        console.print("[yellow]No tracks found[/yellow]")
        return
    
    selected_index = 0
    running = True
    
    def _render_tracks_table() -> Panel:
        """Render the tracks table with selection."""
        table = Table(title=title, show_header=True, header_style="bold blue")
        table.add_column("Selection", width=3)
        table.add_column("#", width=3)
        table.add_column("Title", width=30)
        table.add_column("Artists", width=25)
        table.add_column("Album", width=25)
        table.add_column("Duration", width=8)
        table.add_column("Popularity", width=10)
        
        for i, track in enumerate(tracks):
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
            
            # Selection indicator
            if i == selected_index:
                selection = "▶"
                style = "bold blue"
            else:
                selection = " "
                style = "white"
            
            # Title with style
            title_text = Text(track.get('name', 'Unknown'), style=style)
            artists_text = Text(artists, style=style)
            album_text = Text(track.get('album', 'Unknown'), style=style)
            duration_text = Text(duration_str, style=style)
            popularity_text = Text(f"{popularity} {popularity_bar}", style=style)
            
            table.add_row(
                selection,
                Text(str(i + 1), style=style),
                title_text,
                artists_text,
                album_text,
                duration_text,
                popularity_text
            )
        
        # Add instructions
        instructions = Text()
        instructions.append("↑/↓/WASD: Navigate  ", style="dim")
        instructions.append("Enter: View Details  ", style="dim")
        instructions.append("Numbers: Direct select  ", style="dim")
        instructions.append("b/q: Back", style="dim")
        
        panel = Panel(
            table,
            title=f"[bold blue]{title}[/bold blue]",
            subtitle=instructions,
            border_style="blue",
        )
        
        return panel
    
    def _move_selection(direction: int) -> None:
        """Move the selection up or down."""
        nonlocal selected_index
        if not tracks:
            return
        selected_index = (selected_index + direction) % len(tracks)
    
    def _show_track_details() -> None:
        """Show details for the selected track."""
        if 0 <= selected_index < len(tracks):
            console.clear()
            display_track_details(tracks[selected_index])
            console.print("\n[dim]Press Enter to return to track list...[/dim]")
            input()
    
    def _handle_input() -> None:
        """Handle keyboard input."""
        nonlocal running
        try:
            char = get_single_char()
            
            if char in ['q', 'b']:
                running = False
            elif char in ['w', 'k', 'a', 'up']:  # Up
                _move_selection(-1)
            elif char in ['s', 'j', 'd', 'down']:  # Down
                _move_selection(1)
            elif char in ['\r', '\n', 'right']:  # Enter
                _show_track_details()
            elif char == ' ':  # Space
                _show_track_details()
            else:
                # Check for numeric shortcuts
                try:
                    index = int(char) - 1
                    if 0 <= index < len(tracks):
                        selected_index = index
                        _show_track_details()
                except ValueError:
                    pass
                    
        except EOFError:
            running = False
        except KeyboardInterrupt:
            raise
    
    # Interactive loop
    try:
        while running:
            console.clear()
            console.print(_render_tracks_table())
            _handle_input()
    except KeyboardInterrupt:
        console.print("\n[dim]Returning to previous menu...[/dim]")
        pass


def display_playlists_table(playlists: List[Dict[str, Any]], title: str = "Playlists") -> None:
    """
    Display playlists in an interactive table with selection capabilities.
    
    Args:
        playlists: List of playlist dictionaries
        title: Table title
    """
    if not playlists:
        console.print("[yellow]No playlists found[/yellow]")
        return
    
    selected_index = 0
    running = True
    
    def _render_playlists_table() -> Panel:
        """Render the playlists table with selection."""
        table = Table(title=title, show_header=True, header_style="bold blue")
        table.add_column("Selection", width=3)
        table.add_column("#", width=3)
        table.add_column("Name", width=30)
        table.add_column("Description", width=40)
        table.add_column("Tracks", width=8)
        table.add_column("Public", width=8)
        
        for i, playlist in enumerate(playlists):
            description = playlist.get('description', '')
            if len(description) > 37:
                description = description[:37] + "..."
            
            # Selection indicator
            if i == selected_index:
                selection = "▶"
                style = "bold blue"
            else:
                selection = " "
                style = "white"
            
            # Content with style
            name_text = Text(playlist.get('name', 'Unknown'), style=style)
            description_text = Text(description, style=style)
            tracks_text = Text(str(playlist.get('tracks_count', 0)), style=style)
            public_text = Text("Yes" if playlist.get('public', False) else "No", style=style)
            
            table.add_row(
                selection,
                Text(str(i + 1), style=style),
                name_text,
                description_text,
                tracks_text,
                public_text
            )
        
        # Add instructions
        instructions = Text()
        instructions.append("↑/↓/WASD: Navigate  ", style="dim")
        instructions.append("Enter: View Details  ", style="dim")
        instructions.append("Numbers: Direct select  ", style="dim")
        instructions.append("b/q: Back", style="dim")
        
        panel = Panel(
            table,
            title=f"[bold blue]{title}[/bold blue]",
            subtitle=instructions,
            border_style="blue",
        )
        
        return panel
    
    def _move_selection(direction: int) -> None:
        """Move the selection up or down."""
        nonlocal selected_index
        if not playlists:
            return
        selected_index = (selected_index + direction) % len(playlists)
    
    def _show_playlist_details() -> None:
        """Show details for the selected playlist."""
        if 0 <= selected_index < len(playlists):
            console.clear()
            display_playlist_details(playlists[selected_index])
            console.print("\n[dim]Press Enter to return to playlist list...[/dim]")
            input()
    
    def _handle_input() -> None:
        """Handle keyboard input."""
        nonlocal running
        try:
            char = get_single_char()
            
            if char in ['q', 'b']:
                running = False
            elif char in ['w', 'k', 'a', 'up']:  # Up
                _move_selection(-1)
            elif char in ['s', 'j', 'd', 'down']:  # Down
                _move_selection(1)
            elif char in ['\r', '\n', 'right']:  # Enter
                _show_playlist_details()
            elif char == ' ':  # Space
                _show_playlist_details()
            else:
                # Check for numeric shortcuts
                try:
                    index = int(char) - 1
                    if 0 <= index < len(playlists):
                        selected_index = index
                        _show_playlist_details()
                except ValueError:
                    pass
                    
        except EOFError:
            running = False
        except KeyboardInterrupt:
            raise
    
    # Interactive loop
    try:
        while running:
            console.clear()
            console.print(_render_playlists_table())
            _handle_input()
    except KeyboardInterrupt:
        console.print("\n[dim]Returning to previous menu...[/dim]")
        pass


def display_track_details(track: Dict[str, Any]) -> None:
    """
    Display detailed information about a track.
    
    Args:
        track: Track dictionary
    """
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