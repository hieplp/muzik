"""
Configuration editing functionality.
"""

import os
import subprocess
import sys

from rich.console import Console
from rich.prompt import Confirm

from ..config import Config

console = Console()


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
