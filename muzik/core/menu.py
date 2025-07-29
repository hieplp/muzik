"""
Simple interactive menu system that works reliably.
"""

import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()


class MenuItem:
    """Represents a menu item."""
    
    def __init__(
        self,
        title: str,
        action: Optional[Callable] = None,
        description: Optional[str] = None,
        shortcut: Optional[str] = None,
        enabled: bool = True,
    ) -> None:
        """
        Initialize a menu item.
        
        Args:
            title: Display title
            action: Function to call when selected
            description: Optional description
            shortcut: Keyboard shortcut
            enabled: Whether item is enabled
        """
        self.title = title
        self.action = action
        self.description = description
        self.shortcut = shortcut
        self.enabled = enabled


class Menu:
    """Simple interactive menu with reliable navigation."""
    
    def __init__(self, title: str = "Menu") -> None:
        """
        Initialize the menu.
        
        Args:
            title: Menu title
        """
        self.title = title
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.running = True
    
    def add_item(
        self,
        title: str,
        action: Optional[Callable] = None,
        description: Optional[str] = None,
        shortcut: Optional[str] = None,
        enabled: bool = True,
    ) -> None:
        """
        Add an item to the menu.
        
        Args:
            title: Display title
            action: Function to call when selected
            description: Optional description
            shortcut: Keyboard shortcut
            enabled: Whether item is enabled
        """
        item = MenuItem(title, action, description, shortcut, enabled)
        self.items.append(item)
    
    def add_separator(self) -> None:
        """Add a separator line to the menu."""
        self.items.append(MenuItem("─" * 40, enabled=False))
    
    def _render_menu(self) -> Panel:
        """Render the menu as a rich panel."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Selection", width=3)
        table.add_column("Title", width=30)
        table.add_column("Description", width=40)
        table.add_column("Shortcut", width=10)
        
        for i, item in enumerate(self.items):
            if not item.enabled:
                # Separator line
                table.add_row("", item.title, "", "")
                continue
            
            # Selection indicator
            if i == self.selected_index:
                selection = "▶"
                style = "bold blue"
            else:
                selection = " "
                style = "white"
            
            # Title with style
            title_text = Text(item.title, style=style)
            
            # Description
            description = item.description or ""
            
            # Shortcut
            shortcut = f"[{item.shortcut}]" if item.shortcut else ""
            
            table.add_row(selection, title_text, description, shortcut)
        
        # Add instructions
        instructions = Text()
        instructions.append("↑/↓/WASD: Navigate  ", style="dim")
        instructions.append("Enter: Select  ", style="dim")
        instructions.append("Numbers: Direct select  ", style="dim")
        instructions.append("q: Quit", style="dim")
        
        panel = Panel(
            table,
            title=f"[bold blue]{self.title}[/bold blue]",
            subtitle=instructions,
            border_style="blue",
        )
        
        return panel
    
    def _get_single_char(self) -> str:
        """Get a single character input."""
        try:
            if sys.platform == "win32":
                import msvcrt
                char = msvcrt.getch()
                # Check for Ctrl+C on Windows
                if char == b'\x03':
                    raise KeyboardInterrupt
                if char == b'\xe0':  # Extended key prefix
                    char = msvcrt.getch()
                    if char == b'H':  # Up arrow
                        return 'up'
                    elif char == b'P':  # Down arrow
                        return 'down'
                    elif char == b'M':  # Right arrow
                        return 'right'
                    elif char == b'K':  # Left arrow
                        return 'left'
                return char.decode('utf-8', errors='ignore')
            else:
                import tty
                import termios
                
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    char = sys.stdin.read(1)
                    
                    # Check for Ctrl+C (ASCII 3)
                    if char == '\x03':
                        raise KeyboardInterrupt                    
                    # Handle arrow key escape sequences
                    if char == '\x1b':  # Escape sequence
                        next_char = sys.stdin.read(1)
                        if next_char == '[':
                            third_char = sys.stdin.read(1)
                            if third_char == 'A':  # Up arrow
                                return 'up'
                            elif third_char == 'B':  # Down arrow
                                return 'down'
                            elif third_char == 'C':  # Right arrow
                                return 'right'
                            elif third_char == 'D':  # Left arrow
                                return 'left'
                    return char
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt 
            console.print("\n[dim]Press Enter to exit...[/dim]")
            input()
            raise
        except Exception:
            # Fallback to simple input
            try:
                return console.input("").strip()
            except KeyboardInterrupt:
                raise
    
    def _handle_input(self) -> None:
        """Handle keyboard input."""
        try:
            char = self._get_single_char()
            
            if char == 'q':
                self.running = False
            elif char in ['w', 'k', 'a', 'up']:  # Up
                self._move_selection(-1)
            elif char in ['s', 'j', 'd', 'down']:  # Down
                self._move_selection(1)
            elif char in ['\r', '\n', 'right']:  # Enter
                self._execute_selection()
            elif char == ' ':  # Space
                self._execute_selection()
            else:
                # Check for numeric shortcuts
                try:
                    index = int(char) - 1
                    if 0 <= index < len(self.items):
                        self.selected_index = index
                        self._execute_selection()
                except ValueError:
                    pass
                    
        except EOFError:
            self.running = False
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt to allow proper handling at higher levels
            raise
    
    def _move_selection(self, direction: int) -> None:
        """Move the selection up or down."""
        if not self.items:
            return
        
        # Find enabled items
        enabled_indices = [i for i, item in enumerate(self.items) if item.enabled]
        if not enabled_indices:
            return
        
        # Find current position in enabled items
        try:
            current_pos = enabled_indices.index(self.selected_index)
        except ValueError:
            current_pos = 0
        
        # Move selection
        new_pos = (current_pos + direction) % len(enabled_indices)
        self.selected_index = enabled_indices[new_pos]
    
    def _execute_selection(self) -> None:
        """Execute the currently selected item."""
        if not self.items or self.selected_index >= len(self.items):
            return
        
        item = self.items[self.selected_index]
        if not item.enabled or not item.action:
            return
        
        try:
            item.action()
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt to allow global exit
            raise
        except Exception as e:
            console.print(f"[bold red]Error executing {item.title}: {e}[/bold red]")
    
    def run(self) -> None:
        """Run the interactive menu."""
        if not self.items:
            console.print("[yellow]No menu items to display[/yellow]")
            return
        
        # Ensure we have a valid selection
        enabled_indices = [i for i, item in enumerate(self.items) if item.enabled]
        if enabled_indices:
            self.selected_index = enabled_indices[0]
        
        try:
            while self.running:
                console.clear()
                console.print(self._render_menu())
                self._handle_input()
        except KeyboardInterrupt:
            # Re-raise to allow proper handling at higher levels
            raise


def show_main_menu() -> None:
    """Show the main application menu."""
    from .songs import show_songs_menu
    from .settings import show_settings_menu
    from .application import show_application_menu
    from .about import show_about_menu
    
    menu = Menu("🎵 Muzik Console Application")
    
    # Songs section
    menu.add_item(
        "Songs",
        show_songs_menu,
        "Find and manage songs",
        "1"
    )
    
    menu.add_separator()
    
    # Settings section
    menu.add_item(
        "Settings",
        show_settings_menu,
        "Configure application settings",
        "2"
    )
    
    # Application section
    menu.add_item(
        "Application",
        show_application_menu,
        "Application information and status",
        "3"
    )
    
    # About section
    menu.add_item(
        "About",
        show_about_menu,
        "Information about the application",
        "4"
    )
    
    menu.add_separator()
    
    # Exit
    menu.add_item(
        "Exit",
        lambda: setattr(menu, 'running', False),
        "Exit the application",
        "q"
    )
    
    menu.run()


def create_simple_menu(
    title: str,
    options: List[Tuple[str, Callable, Optional[str]]],
    show_back: bool = True,
) -> None:
    """
    Create and show a simple menu.
    
    Args:
        title: Menu title
        options: List of (title, action, description) tuples
        show_back: Whether to show a back option
    """
    menu = Menu(title)
    
    for title, action, description in options:
        menu.add_item(title, action, description)
    
    if show_back:
        menu.add_separator()
        menu.add_item(
            "Back",
            lambda: setattr(menu, 'running', False),
            "Go back to previous menu",
            "b"
        )
    
    menu.run()