#!/usr/bin/env python3
"""
Main entry point for the Muzik console application.
"""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from muzik import __version__
from muzik.core.config import Config
from muzik.core.logger import setup_logger
from muzik.core.menu import show_main_menu
from muzik.utils.display import print_banner

# Create Typer app
app = typer.Typer(
    name="muzik",
    help="A modern Python console application",
    add_completion=False,
)

# Create console for rich output
console = Console()


@app.callback(invoke_without_command=True)
def main(
        version: bool = typer.Option(
            None, "--version", "-v", help="Show version and exit"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", help="Enable verbose output"
        ),
        config_file: Optional[str] = typer.Option(
            None, "--config", "-c", help="Path to configuration file"
        ),
) -> None:
    """
    Muzik - A modern Python console application.
    
    This application provides various console utilities and tools.
    """
    if version:
        console.print(f"[bold blue]Muzik[/bold blue] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()

    # Setup logging
    setup_logger(verbose=verbose)

    # Load configuration
    config = Config(config_file=config_file)

    # Display banner
    print_banner()

    # Show the menu by default
    show_main_menu()


@app.command()
def hello(
        name: str = typer.Option("World", "--name", "-n", help="Name to greet"),
        count: int = typer.Option(1, "--count", "-c", help="Number of greetings"),
) -> None:
    """
    Say hello to someone.
    """
    for i in range(count):
        console.print(f"[bold green]Hello[/bold green] [bold blue]{name}[/bold blue]! ({i + 1}/{count})")


@app.command()
def info() -> None:
    """
    Display application information.
    """
    info_text = Text()
    info_text.append("Muzik Console Application\n", style="bold blue")
    info_text.append(f"Version: {__version__}\n", style="green")
    info_text.append("A modern Python console application with rich features.", style="italic")

    panel = Panel(info_text, title="Application Info", border_style="blue")
    console.print(panel)


@app.command()
def status() -> None:
    """
    Show application status.
    """
    console.print("[bold green]✓[/bold green] Application is running")
    console.print(f"[bold blue]Version:[/bold blue] {__version__}")
    console.print("[bold blue]Status:[/bold blue] Ready")


@app.command()
def menu() -> None:
    """
    Launch interactive menu.
    """
    show_main_menu()


def main_wrapper() -> None:
    """Wrapper function to handle exceptions gracefully."""
    while True:
        try:
            app()
            break  # Normal exit
        except KeyboardInterrupt:
            from rich.prompt import Confirm
            from rich.panel import Panel

            console.print()  # Add blank line for better spacing
            console.print(Panel(
                "[yellow]⚠️  Exit Confirmation[/yellow]\n\n"
                "You pressed Ctrl+C to exit the application.\n"
                "Are you sure you want to quit?",
                title="🚪 Exit",
                border_style="yellow"
            ))

            try:
                if Confirm.ask("[bold]Do you really want to exit?[/bold]", default=False):
                    console.print()
                    console.print(Panel(
                        "[green]Thank you for using Muzik![/green] 🎵",
                        title="👋 Goodbye",
                        border_style="green"
                    ))
                    sys.exit(0)
                else:
                    console.print()
                    console.print(Panel(
                        "[blue]Welcome back![/blue] 🎵",
                        title="▶️  Continuing",
                        border_style="blue"
                    ))
                    # Continue the loop to restart the application
                    continue
            except KeyboardInterrupt:
                # If they press Ctrl+C again during confirmation, force exit
                console.print("\n[red]💥 Force exit![/red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)


if __name__ == "__main__":
    main_wrapper()
