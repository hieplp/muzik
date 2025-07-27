"""
Display utilities for rich console output.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()


def print_banner() -> None:
    """Print application banner."""
    banner_text = Text()
    banner_text.append("🎵 ", style="bold blue")
    banner_text.append("MUZIK", style="bold white on blue")
    banner_text.append(" 🎵", style="bold blue")
    banner_text.append("\nA Modern Python Console Application", style="italic cyan")

    panel = Panel(
        banner_text,
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


def print_table(
        data: List[Dict[str, Any]],
        title: Optional[str] = None,
        show_header: bool = True,
) -> None:
    """
    Print data as a formatted table.
    
    Args:
        data: List of dictionaries to display
        title: Optional table title
        show_header: Whether to show column headers
    """
    if not data:
        console.print("[yellow]No data to display[/yellow]")
        return

    table = Table(title=title, show_header=show_header)

    # Add columns
    for key in data[0].keys():
        table.add_column(key, style="cyan", no_wrap=True)

    # Add rows
    for row in data:
        table.add_row(*[str(value) for value in row.values()])

    console.print(table)


def print_progress(
        total: int,
        description: str = "Processing...",
        transient: bool = False,
) -> Progress:
    """
    Create and return a progress bar.
    
    Args:
        total: Total number of items
        description: Progress description
        transient: Whether to make progress bar transient
        
    Returns:
        Progress instance
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=transient,
    )

    progress.add_task(description, total=total)
    return progress


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_separator(char: str = "─", length: int = 50) -> None:
    """Print a separator line."""
    console.print(char * length, style="dim")


def print_header(text: str, level: int = 1) -> None:
    """
    Print a formatted header.
    
    Args:
        text: Header text
        level: Header level (1-3)
    """
    styles = {
        1: "bold white on blue",
        2: "bold blue",
        3: "bold cyan",
    }

    style = styles.get(level, "bold")
    console.print(f"\n[bold]{text}[/bold]", style=style)
    if level == 1:
        console.print("─" * len(text), style="blue")
