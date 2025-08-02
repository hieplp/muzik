"""
Configuration display functionality.
"""

from rich.console import Console
from rich.table import Table

from ..config import Config

console = Console()


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
        try:
            input()
        except KeyboardInterrupt:
            # Re-raise to allow proper handling at higher levels
            raise

    except Exception as e:
        console.print(f"[red]Error displaying configuration: {e}[/red]")
        console.print("[dim]Press Enter to continue...[/dim]")
        try:
            input()
        except KeyboardInterrupt:
            # Re-raise to allow proper handling at higher levels
            raise


def show_config_with_clear(config: Config) -> None:
    """Display the current configuration with screen clear."""
    # Clear the screen first
    console.clear()

    # Show the configuration
    show_current_config(config)
