"""
Settings menu functionality.
"""

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table

from ..config import Config
from ..spotify.api.auth import SpotifyAuth, validate_spotify_config
from .config_display import show_config_with_clear
from .config_editor import edit_config_file, reset_to_defaults
from .utilities import validate_email_utility, validate_url_utility, display_table_utility

console = Console()


def configure_spotify_tokens(config: Config) -> None:
    """Configure Spotify tokens interactively."""
    auth = SpotifyAuth(config)
    
    console.print(Panel(
        "[bold blue]Spotify API Configuration[/bold blue]\n\n"
        "To use Spotify API features, you need to configure your access tokens.\n"
        "You can get these from the Spotify Developer Dashboard:\n"
        "https://developer.spotify.com/dashboard\n\n"
        "1. Create a new app in the Spotify Developer Dashboard\n"
        "2. Get your Client ID and Client Secret\n"
        "3. Set up OAuth redirect URI (default: http://localhost:8888/callback)\n"
        "4. Generate access tokens using the OAuth flow",
        title="🎵 Spotify Setup",
        border_style="blue"
    ))
    
    # Show current configuration
    status = auth.get_status()
    console.print("\n[bold]Current Configuration:[/bold]")
    console.print(f"Client ID: {'[green]Set[/green]' if status['client_id_set'] else '[red]Not set[/red]'}")
    console.print(f"Client Secret: {'[green]Set[/green]' if status['client_secret_set'] else '[red]Not set[/red]'}")
    console.print(f"Access Token: {'[green]Set[/green]' if status['access_token_set'] else '[red]Not set[/red]'}")
    console.print(f"Refresh Token: {'[green]Set[/green]' if status['refresh_token_set'] else '[red]Not set[/red]'}")
    
    # Create rich choice menu
    from muzik.utils.input_utils import rich_choice_menu
    
    choices = [
        "Client ID and Client Secret",
        "Access Token and Refresh Token", 
        "All settings",
        "Clear all Spotify settings",
        "Back to menu"
    ]
    
    descriptions = [
        "Configure app credentials from Spotify Developer Dashboard",
        "Configure OAuth tokens for API access",
        "Configure all Spotify settings at once",
        "Remove all stored Spotify configuration",
        "Return to previous menu"
    ]
    
    console.print("\n[bold]Spotify Configuration Options[/bold]")
    choice_text = rich_choice_menu(
        "What would you like to configure?",
        choices,
        descriptions,
        show_quit=False
    )
    
    if not choice_text:
        return
        
    choice = str(choices.index(choice_text) + 1)
    
    if choice == "1":
        _configure_client_credentials(auth)
    elif choice == "2":
        _configure_access_tokens(auth)
    elif choice == "3":
        _configure_client_credentials(auth)
        _configure_access_tokens(auth)
    elif choice == "4":
        _clear_spotify_settings(auth)
    elif choice == "5":
        return


def show_spotify_status(config: Config) -> None:
    """Show Spotify API status with enhanced Rich display."""
    from muzik.utils.display import display_key_value_table, create_info_panel
    from muzik.utils.input_utils import pause_for_user
    
    auth = SpotifyAuth(config)
    status = auth.get_status()
    
    # Create status data for table
    status_data = {
        "Configuration Status": "✓ Configured" if status['configured'] else "✗ Not Configured",
        "Client ID": status['client_id'] if status['client_id'] else "Not set",
        "Client Secret": "Set" if status['client_secret_set'] else "Not set", 
        "Access Token": "Set" if status['access_token_set'] else "Not set",
        "Refresh Token": "Set" if status['refresh_token_set'] else "Not set"
    }
    
    # Display status table
    display_key_value_table(status_data, "Spotify API Configuration Status")
    
    # Test API connection if possible
    if status['configured']:
        console.print("\n[bold]Testing API Connection...[/bold]")
        success, error = auth.test_connection()
        if success:
            console.print("[green]✓ API connection test successful![/green]")
        else:
            console.print(f"[red]✗ API connection test failed: {error}[/red]")
    else:
        console.print("\n[yellow]⚠️  Configure Client ID and Client Secret to enable API features[/yellow]")
    
    pause_for_user()


def _configure_client_credentials(auth: SpotifyAuth) -> None:
    """Configure Spotify client ID and secret with enhanced prompts."""
    from muzik.utils.input_utils import rich_prompt, rich_confirm
    
    console.print(Panel(
        "[bold blue]Spotify Client Credentials[/bold blue]\n\n"
        "Enter your Spotify app credentials from the Developer Dashboard.\n"
        "Get these from: https://developer.spotify.com/dashboard",
        title="🔑 Client Setup",
        border_style="blue"
    ))
    
    status = auth.get_status()
    
    if status['client_id_set']:
        console.print(f"Current Client ID: [dim]{status['client_id']}[/dim]")
        if not rich_confirm("Do you want to update the Client ID?"):
            client_id = auth.client_id
        else:
            client_id = rich_prompt("Enter your Spotify Client ID")
    else:
        client_id = rich_prompt("Enter your Spotify Client ID")
    
    if status['client_secret_set']:
        console.print("Current Client Secret: [dim][hidden][/dim]")
        if not rich_confirm("Do you want to update the Client Secret?"):
            client_secret = auth.client_secret
        else:
            client_secret = rich_prompt("Enter your Spotify Client Secret", password=True)
    else:
        client_secret = rich_prompt("Enter your Spotify Client Secret", password=True)
    
    # Save credentials
    auth.set_credentials(client_id, client_secret)
    console.print("[green]✓ Client credentials saved successfully![/green]")


def _configure_access_tokens(auth: SpotifyAuth) -> None:
    """Configure access and refresh tokens with enhanced prompts."""
    from muzik.utils.input_utils import rich_prompt, rich_confirm
    
    console.print(Panel(
        "[bold blue]Spotify Access Tokens[/bold blue]\n\n"
        "Enter your Spotify access tokens. You can generate these using OAuth flow.\n"
        "These tokens provide access to your Spotify account data.",
        title="🎫 Token Setup", 
        border_style="blue"
    ))
    
    status = auth.get_status()
    
    if status['access_token_set']:
        console.print("Current Access Token: [dim][hidden][/dim]")
        if not rich_confirm("Do you want to update the Access Token?"):
            access_token = auth.access_token
        else:
            access_token = rich_prompt("Enter your Spotify Access Token", password=True)
    else:
        access_token = rich_prompt("Enter your Spotify Access Token", password=True)
    
    if status['refresh_token_set']:
        console.print("Current Refresh Token: [dim][hidden][/dim]")
        if not rich_confirm("Do you want to update the Refresh Token?"):
            refresh_token = auth.refresh_token
        else:
            refresh_token = rich_prompt("Enter your Spotify Refresh Token (optional)", default="", password=True)
    else:
        refresh_token = rich_prompt("Enter your Spotify Refresh Token (optional)", default="", password=True)
    
    # Save tokens
    auth.set_tokens(access_token, refresh_token if refresh_token else None)
    console.print("[green]✓ Access tokens saved successfully![/green]")


def _clear_spotify_settings(auth: SpotifyAuth) -> None:
    """Clear all Spotify settings with enhanced confirmation."""
    from muzik.utils.input_utils import rich_confirm
    
    console.print(Panel(
        "[bold red]⚠️  Clear All Spotify Settings[/bold red]\n\n"
        "This will remove all stored Spotify configuration:\n"
        "• Client ID and Client Secret\n"
        "• Access Token and Refresh Token\n"
        "• All API access will be disabled\n\n"
        "[bold]This action cannot be undone![/bold]",
        title="🗑️  Confirm Deletion",
        border_style="red"
    ))
    
    if not rich_confirm("Are you sure you want to clear all Spotify settings?", default=False):
        console.print("[yellow]Clear operation cancelled[/yellow]")
        return
    
    # Double confirmation for destructive action
    if not rich_confirm("This will permanently delete your settings. Continue?", default=False):
        console.print("[yellow]Clear operation cancelled[/yellow]")
        return
    
    auth.clear_settings()
    console.print("[green]✓ All Spotify settings cleared successfully![/green]")


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