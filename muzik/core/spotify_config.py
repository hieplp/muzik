"""
Spotify API configuration utilities.
"""

import os
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

from .config import Config

console = Console()


def configure_spotify_tokens(config: Config) -> None:
    """Configure Spotify access tokens interactively."""
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
    
    # Get current values
    current_client_id = config.get("spotify.client_id", "")
    current_client_secret = config.get("spotify.client_secret", "")
    current_access_token = config.get("spotify.access_token", "")
    current_refresh_token = config.get("spotify.refresh_token", "")
    
    console.print("\n[bold]Current Configuration:[/bold]")
    console.print(f"Client ID: {'[green]Set[/green]' if current_client_id else '[red]Not set[/red]'}")
    console.print(f"Client Secret: {'[green]Set[/green]' if current_client_secret else '[red]Not set[/red]'}")
    console.print(f"Access Token: {'[green]Set[/green]' if current_access_token else '[red]Not set[/red]'}")
    console.print(f"Refresh Token: {'[green]Set[/green]' if current_refresh_token else '[red]Not set[/red]'}")
    
    # Ask what to configure
    console.print("\n[bold]What would you like to configure?[/bold]")
    console.print("1. Client ID and Client Secret")
    console.print("2. Access Token and Refresh Token")
    console.print("3. All settings")
    console.print("4. Clear all Spotify settings")
    console.print("5. Back to menu")
    
    choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])
    
    if choice == "1":
        configure_client_credentials(config)
    elif choice == "2":
        configure_access_tokens(config)
    elif choice == "3":
        configure_client_credentials(config)
        configure_access_tokens(config)
    elif choice == "4":
        clear_spotify_settings(config)
    elif choice == "5":
        return


def configure_client_credentials(config: Config) -> None:
    """Configure Spotify client ID and secret."""
    console.print(Panel(
        "[bold blue]Spotify Client Credentials[/bold blue]\n\n"
        "Enter your Spotify app credentials from the Developer Dashboard.",
        title="🔑 Client Setup",
        border_style="blue"
    ))
    
    current_client_id = config.get("spotify.client_id", "")
    current_client_secret = config.get("spotify.client_secret", "")
    
    if current_client_id:
        console.print(f"Current Client ID: {current_client_id[:10]}...")
        if not Confirm.ask("Do you want to update the Client ID?"):
            client_id = current_client_id
        else:
            client_id = Prompt.ask("Enter your Spotify Client ID")
    else:
        client_id = Prompt.ask("Enter your Spotify Client ID")
    
    if current_client_secret:
        console.print(f"Current Client Secret: {current_client_secret[:10]}...")
        if not Confirm.ask("Do you want to update the Client Secret?"):
            client_secret = current_client_secret
        else:
            client_secret = Prompt.ask("Enter your Spotify Client Secret", password=True)
    else:
        client_secret = Prompt.ask("Enter your Spotify Client Secret", password=True)
    
    # Save to config
    config.set("spotify.client_id", client_id)
    config.set("spotify.client_secret", client_secret)
    
    try:
        config.save()
        console.print("[green]✓ Client credentials saved successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Error saving configuration: {e}[/red]")


def configure_access_tokens(config: Config) -> None:
    """Configure Spotify access tokens."""
    console.print(Panel(
        "[bold blue]Spotify Access Tokens[/bold blue]\n\n"
        "Enter your Spotify access tokens. You can get these by:\n"
        "1. Using the Spotify OAuth flow\n"
        "2. Generating tokens manually from the Developer Dashboard\n"
        "3. Using a tool like spotipy to generate tokens",
        title="🎫 Token Setup",
        border_style="blue"
    ))
    
    current_access_token = config.get("spotify.access_token", "")
    current_refresh_token = config.get("spotify.refresh_token", "")
    
    if current_access_token:
        console.print(f"Current Access Token: {current_access_token[:20]}...")
        if not Confirm.ask("Do you want to update the Access Token?"):
            access_token = current_access_token
        else:
            access_token = Prompt.ask("Enter your Spotify Access Token", password=True)
    else:
        access_token = Prompt.ask("Enter your Spotify Access Token", password=True)
    
    if current_refresh_token:
        console.print(f"Current Refresh Token: {current_refresh_token[:20]}...")
        if not Confirm.ask("Do you want to update the Refresh Token?"):
            refresh_token = current_refresh_token
        else:
            refresh_token = Prompt.ask("Enter your Spotify Refresh Token", password=True)
    else:
        refresh_token = Prompt.ask("Enter your Spotify Refresh Token", password=True)
    
    # Save to config
    config.set("spotify.access_token", access_token)
    config.set("spotify.refresh_token", refresh_token)
    
    try:
        config.save()
        console.print("[green]✓ Access tokens saved successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Error saving configuration: {e}[/red]")


def clear_spotify_settings(config: Config) -> None:
    """Clear all Spotify settings."""
    if Confirm.ask("Are you sure you want to clear all Spotify settings?"):
        config.set("spotify.access_token", "")
        config.set("spotify.refresh_token", "")
        config.set("spotify.client_id", "")
        config.set("spotify.client_secret", "")
        
        try:
            config.save()
            console.print("[green]✓ Spotify settings cleared successfully![/green]")
        except Exception as e:
            console.print(f"[red]✗ Error saving configuration: {e}[/red]")


def show_spotify_status(config: Config) -> None:
    """Show current Spotify configuration status."""
    client_id = config.get("spotify.client_id", "")
    client_secret = config.get("spotify.client_secret", "")
    access_token = config.get("spotify.access_token", "")
    refresh_token = config.get("spotify.refresh_token", "")
    
    status_text = Text()
    status_text.append("Spotify API Configuration Status\n\n", style="bold blue")
    
    # Client credentials
    status_text.append("Client Credentials:\n", style="bold")
    status_text.append(f"  Client ID: {'[green]✓ Set[/green]' if client_id else '[red]✗ Not set[/red]'}\n")
    status_text.append(f"  Client Secret: {'[green]✓ Set[/green]' if client_secret else '[red]✗ Not set[/red]'}\n\n")
    
    # Access tokens
    status_text.append("Access Tokens:\n", style="bold")
    status_text.append(f"  Access Token: {'[green]✓ Set[/green]' if access_token else '[red]✗ Not set[/red]'}\n")
    status_text.append(f"  Refresh Token: {'[green]✓ Set[/green]' if refresh_token else '[red]✗ Not set[/red]'}\n\n")
    
    # Overall status
    if client_id and client_secret and access_token and refresh_token:
        status_text.append("[green]✓ Spotify API is fully configured and ready to use![/green]\n")
    elif client_id and client_secret:
        status_text.append("[yellow]⚠ Client credentials are set, but access tokens are missing[/yellow]\n")
    else:
        status_text.append("[red]✗ Spotify API is not configured[/red]\n")
    
    console.print(Panel(status_text, title="🎵 Spotify Status", border_style="blue"))


def validate_spotify_config(config: Config) -> bool:
    """Validate that Spotify configuration is complete."""
    client_id = config.get("spotify.client_id", "")
    client_secret = config.get("spotify.client_secret", "")
    access_token = config.get("spotify.access_token", "")
    refresh_token = config.get("spotify.refresh_token", "")
    
    return bool(client_id and client_secret and access_token and refresh_token) 