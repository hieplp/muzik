"""
Settings menu functionality.
"""

from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..config import Config
from ..spotify_config import configure_spotify_tokens, show_spotify_status
from .config_display import show_config_with_clear
from .config_editor import edit_config_file, reset_to_defaults
from .utilities import validate_email_utility, validate_url_utility, display_table_utility

console = Console()


def show_settings_menu() -> None:
    """Show the settings menu."""
    from ..menu import Menu
    
    menu = Menu("⚙️ Settings")
    
    menu.add_item(
        "Config",
        show_config_menu,
        "Manage application configuration",
        "1"
    )
    
    menu.add_item(
        "Utilities",
        show_utils_menu,
        "Access utility functions",
        "2"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Back to Main Menu",
        lambda: setattr(menu, 'running', False),
        "Return to main menu",
        "b"
    )
    
    menu.run()


def show_config_menu() -> None:
    """Show the configuration menu."""
    config = Config()
    
    from ..menu import Menu
    
    menu = Menu("⚙️ Configuration")
    
    menu.add_item(
        "Show Current Config",
        lambda: show_config_with_clear(config),
        "Display current configuration",
        "1"
    )
    
    menu.add_item(
        "Spotify API Settings",
        lambda: configure_spotify_tokens(config),
        "Configure Spotify API access tokens",
        "2"
    )
    
    menu.add_item(
        "Spotify Status",
        lambda: show_spotify_status(config),
        "Show Spotify API configuration status",
        "3"
    )
    
    menu.add_item(
        "Edit Config File",
        lambda: edit_config_file(config),
        "Edit configuration file",
        "4"
    )
    
    menu.add_item(
        "Reset to Defaults",
        lambda: reset_to_defaults(config),
        "Reset configuration to default values",
        "5"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Back to Main Menu",
        lambda: setattr(menu, 'running', False),
        "Return to main menu",
        "b"
    )
    
    menu.run()


def show_utils_menu() -> None:
    """Show the utilities menu."""
    from ..menu import Menu
    
    menu = Menu("🔧 Utilities")
    
    menu.add_item(
        "Validate Email",
        lambda: validate_email_utility(),
        "Validate email addresses",
        "1"
    )
    
    menu.add_item(
        "Validate URL",
        lambda: validate_url_utility(),
        "Validate URLs",
        "2"
    )
    
    menu.add_item(
        "Display Table",
        lambda: display_table_utility(),
        "Display data in tables",
        "3"
    )
    
    menu.add_separator()
    
    menu.add_item(
        "Back to Main Menu",
        lambda: setattr(menu, 'running', False),
        "Return to main menu",
        "b"
    )
    
    menu.run() 