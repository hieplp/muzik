"""
Settings management functionality.
"""

import os
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm, Prompt

from .config import Config
from .spotify_config import configure_spotify_tokens, show_spotify_status

console = Console()


def show_settings_menu() -> None:
    """Show the settings menu."""
    from .menu import Menu
    
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
    
    from .menu import Menu
    
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
    from .menu import Menu
    
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


def show_current_config(config: Config) -> None:
    """Display the current configuration in separate formatted tables."""
    console.print("[blue]Loading current configuration...[/blue]")
    
    try:
        # Get all configuration data
        config_data = config.to_dict()
        
        # Display app configuration
        app_config = config_data.get("app", {})
        if app_config:
            app_table = Table(title="📱 App Configuration", show_header=True, header_style="bold blue")
            app_table.add_column("Key", width=20, style="bold")
            app_table.add_column("Value", width=40)
            
            for key, value in app_config.items():
                app_table.add_row(key, str(value))
            
            console.print(app_table)
            console.print()  # Empty line for spacing
        
        # Display logging configuration
        logging_config = config_data.get("logging", {})
        if logging_config:
            logging_table = Table(title="📝 Logging Configuration", show_header=True, header_style="bold blue")
            logging_table.add_column("Key", width=20, style="bold")
            logging_table.add_column("Value", width=40)
            
            for key, value in logging_config.items():
                logging_table.add_row(key, str(value))
            
            console.print(logging_table)
            console.print()  # Empty line for spacing
        
        # Display display configuration
        display_config = config_data.get("display", {})
        if display_config:
            display_table = Table(title="🎨 Display Configuration", show_header=True, header_style="bold blue")
            display_table.add_column("Key", width=20, style="bold")
            display_table.add_column("Value", width=40)
            
            for key, value in display_config.items():
                display_table.add_row(key, str(value))
            
            console.print(display_table)
            console.print()  # Empty line for spacing
        
        # Display Spotify configuration (mask sensitive data)
        spotify_config = config_data.get("spotify", {})
        if spotify_config:
            spotify_table = Table(title="🎵 Spotify Configuration", show_header=True, header_style="bold blue")
            spotify_table.add_column("Key", width=20, style="bold")
            spotify_table.add_column("Value", width=40)
            
            for key, value in spotify_config.items():
                if key in ["access_token", "refresh_token", "client_secret"]:
                    # Mask sensitive data
                    if value:
                        masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                    else:
                        masked_value = "Not set"
                else:
                    masked_value = str(value) if value else "Not set"
                spotify_table.add_row(key, masked_value)
            
            console.print(spotify_table)
            console.print()  # Empty line for spacing
        
        # Show configuration file location
        config_file = getattr(config, 'config_file', None)
        if config_file:
            console.print(f"[dim]Configuration file: {config_file}[/dim]")
        else:
            console.print("[dim]Using default configuration[/dim]")
        
        # Show environment variables info
        console.print("[dim]Note: Values may be overridden by environment variables[/dim]")
        
        # Add a pause so user can see the output
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()
        
    except Exception as e:
        console.print(f"[red]Error displaying configuration: {e}[/red]")
        console.print("[dim]Press Enter to continue...[/dim]")
        input()


def show_config_with_clear(config: Config) -> None:
    """Display the current configuration with screen clear."""
    # Clear the screen first
    console.clear()
    
    # Show the configuration
    show_current_config(config)


def edit_config_file(config: Config) -> None:
    """Open the configuration file in the default editor."""
    config_file = getattr(config, 'config_file', None)
    
    if not config_file:
        # Create default config file if it doesn't exist
        config_file = "config.yaml"
        try:
            config.save(config_file)
            console.print(f"[green]✓ Created default configuration file: {config_file}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error creating config file: {e}[/red]")
            return
    
    # Try to open the file in the default editor
    try:
        if sys.platform == "win32":
            os.startfile(config_file)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", config_file], check=True)
        else:  # Linux
            subprocess.run(["xdg-open", config_file], check=True)
        
        console.print(f"[green]✓ Opened configuration file: {config_file}[/green]")
        console.print("[yellow]Note: Save the file and restart the application to apply changes[/yellow]")
        
    except Exception as e:
        console.print(f"[red]✗ Error opening config file: {e}[/red]")
        console.print(f"[yellow]Please manually edit: {config_file}[/yellow]")


def reset_to_defaults(config: Config) -> None:
    """Reset configuration to default values."""
    if not Confirm.ask("Are you sure you want to reset all configuration to defaults?"):
        console.print("[yellow]Reset cancelled[/yellow]")
        return
    
    try:
        # Create a new config with defaults
        default_config = Config()
        
        # Save the default config
        config_file = getattr(config, 'config_file', None) or "config.yaml"
        default_config.save(config_file)
        
        console.print("[green]✓ Configuration reset to defaults successfully![/green]")
        console.print(f"[dim]Default configuration saved to: {config_file}[/dim]")
        console.print("[yellow]Note: Restart the application to apply the new configuration[/yellow]")
        
    except Exception as e:
        console.print(f"[red]✗ Error resetting configuration: {e}[/red]")


def validate_email_utility() -> None:
    """Email validation utility."""
    console.print("[blue]Email Validation Utility[/blue]")
    
    email = Prompt.ask("Enter email address to validate")
    if not email:
        console.print("[yellow]No email provided[/yellow]")
        return
    
    # Simple email validation
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        console.print(f"[green]✓ Valid email: {email}[/green]")
    else:
        console.print(f"[red]✗ Invalid email: {email}[/red]")
        console.print("[dim]Email should be in format: user@domain.com[/dim]")


def validate_url_utility() -> None:
    """URL validation utility."""
    console.print("[blue]URL Validation Utility[/blue]")
    
    url = Prompt.ask("Enter URL to validate")
    if not url:
        console.print("[yellow]No URL provided[/yellow]")
        return
    
    # Simple URL validation
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    
    if re.match(pattern, url):
        console.print(f"[green]✓ Valid URL: {url}[/green]")
    else:
        console.print(f"[red]✗ Invalid URL: {url}[/red]")
        console.print("[dim]URL should start with http:// or https://[/dim]")


def display_table_utility() -> None:
    """Display table utility."""
    console.print("[blue]Table Display Utility[/blue]")
    
    # Sample data for demonstration
    sample_data = [
        {"Name": "John Doe", "Age": 30, "City": "New York"},
        {"Name": "Jane Smith", "Age": 25, "City": "Los Angeles"},
        {"Name": "Bob Johnson", "Age": 35, "City": "Chicago"},
    ]
    
    table = Table(title="Sample Data Table", show_header=True, header_style="bold blue")
    table.add_column("Name", width=15)
    table.add_column("Age", width=8)
    table.add_column("City", width=15)
    
    for row in sample_data:
        table.add_row(row["Name"], str(row["Age"]), row["City"])
    
    console.print(table)
    console.print("[dim]This is a sample table. You can modify this function to display your own data.[/dim]")