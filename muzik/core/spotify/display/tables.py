"""
Interactive table displays for Spotify data.
"""

from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .details import display_track_details, display_playlist_details
from ....utils.input_utils import get_single_char

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
