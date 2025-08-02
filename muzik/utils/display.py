"""
Enhanced display utilities for rich console output with advanced Rich features.
"""

from typing import Any, Dict, List, Optional, Union
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.status import Status
from rich.tree import Tree
from rich.columns import Columns
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.align import Align
from rich.box import ROUNDED

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


def display_tree(
    root_name: str,
    data: Dict[str, Any],
    expanded: bool = True
) -> None:
    """
    Display hierarchical data as a tree structure.
    
    Args:
        root_name: Name of the root node
        data: Hierarchical data dictionary
        expanded: Whether to show tree expanded
    """
    tree = Tree(f"[bold blue]{root_name}[/bold blue]", expanded=expanded)
    
    def add_node(parent_tree: Tree, node_data: Any, name: str = "") -> None:
        if isinstance(node_data, dict):
            for key, value in node_data.items():
                if isinstance(value, (dict, list)):
                    branch = parent_tree.add(f"[cyan]{key}[/cyan]")
                    add_node(branch, value)
                else:
                    parent_tree.add(f"[cyan]{key}[/cyan]: [white]{value}[/white]")
        elif isinstance(node_data, list):
            for i, item in enumerate(node_data):
                if isinstance(item, (dict, list)):
                    branch = parent_tree.add(f"[yellow][{i}][/yellow]")
                    add_node(branch, item)
                else:
                    parent_tree.add(f"[yellow][{i}][/yellow] [white]{item}[/white]")
        else:
            parent_tree.add(f"[white]{node_data}[/white]")
    
    add_node(tree, data)
    console.print(tree)


def display_columns(
    items: List[str],
    title: Optional[str] = None,
    equal_width: bool = False,
    min_width: int = 12
) -> None:
    """
    Display items in columns.
    
    Args:
        items: List of items to display
        title: Optional title
        equal_width: Whether to use equal column widths
        min_width: Minimum column width
    """
    if title:
        console.print(f"[bold blue]{title}[/bold blue]\n")
    
    # Create styled items
    styled_items = [Text(str(item), style="cyan") for item in items]
    
    columns = Columns(
        styled_items,
        equal=equal_width,
        width=min_width if equal_width else None
    )
    
    console.print(columns)


def display_markdown(content: str, title: Optional[str] = None) -> None:
    """
    Display markdown content with Rich formatting.
    
    Args:
        content: Markdown content
        title: Optional title
    """
    if title:
        console.print(f"[bold blue]{title}[/bold blue]\n")
    
    markdown = Markdown(content)
    console.print(markdown)


def display_syntax(
    code: str,
    language: str = "python",
    theme: str = "monokai",
    line_numbers: bool = True,
    title: Optional[str] = None
) -> None:
    """
    Display code with syntax highlighting.
    
    Args:
        code: Code content
        language: Programming language
        theme: Syntax highlighting theme
        line_numbers: Whether to show line numbers
        title: Optional title
    """
    syntax = Syntax(
        code,
        language,
        theme=theme,
        line_numbers=line_numbers
    )
    
    if title:
        panel = Panel(
            syntax,
            title=f"[bold blue]{title}[/bold blue]",
            border_style="blue",
            box=ROUNDED
        )
        console.print(panel)
    else:
        console.print(syntax)


def create_layout(sections: Dict[str, Any]) -> Layout:
    """
    Create a Rich layout with multiple sections.
    
    Args:
        sections: Dictionary of section_name -> content
        
    Returns:
        Rich Layout object
    """
    layout = Layout()
    
    if len(sections) == 1:
        name, content = next(iter(sections.items()))
        layout.update(content)
    elif len(sections) == 2:
        layout.split_column(
            Layout(name="top"),
            Layout(name="bottom")
        )
        names = list(sections.keys())
        layout["top"].update(sections[names[0]])
        layout["bottom"].update(sections[names[1]])
    elif len(sections) == 3:
        layout.split_column(
            Layout(name="header"),
            Layout(name="main"),
            Layout(name="footer")
        )
        names = list(sections.keys())
        layout["header"].update(sections[names[0]])
        layout["main"].update(sections[names[1]])
        layout["footer"].update(sections[names[2]])
    elif len(sections) == 4:
        layout.split_column(
            Layout(name="header"),
            Layout(name="body"),
            Layout(name="footer")
        )
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        names = list(sections.keys())
        layout["header"].update(sections[names[0]])
        layout["left"].update(sections[names[1]])
        layout["right"].update(sections[names[2]])
        layout["footer"].update(sections[names[3]])
    
    return layout


def live_progress_demo(duration: int = 10) -> None:
    """
    Demonstrate live progress updates.
    
    Args:
        duration: Duration in seconds
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        
        task1 = progress.add_task("[red]Downloading...", total=100)
        task2 = progress.add_task("[green]Processing...", total=100)
        task3 = progress.add_task("[cyan]Uploading...", total=100)
        
        for i in range(duration * 10):
            time.sleep(0.1)
            progress.update(task1, advance=1.0)
            progress.update(task2, advance=0.5)
            progress.update(task3, advance=0.3)


def status_spinner(message: str, duration: int = 3) -> None:
    """
    Show a status spinner for a given duration.
    
    Args:
        message: Status message
        duration: Duration in seconds
    """
    with Status(message, console=console) as status:
        time.sleep(duration)


def create_info_panel(
    title: str,
    content: Union[str, Text, Table],
    style: str = "blue",
    padding: tuple = (1, 2)
) -> Panel:
    """
    Create a styled information panel.
    
    Args:
        title: Panel title
        content: Panel content
        style: Border style
        padding: Panel padding
        
    Returns:
        Rich Panel object
    """
    return Panel(
        content,
        title=f"[bold {style}]{title}[/bold {style}]",
        border_style=style,
        padding=padding,
        box=ROUNDED
    )


def display_key_value_table(
    data: Dict[str, Any],
    title: str = "Information",
    key_style: str = "cyan",
    value_style: str = "white"
) -> None:
    """
    Display key-value pairs in a formatted table.
    
    Args:
        data: Key-value data
        title: Table title
        key_style: Style for keys
        value_style: Style for values
    """
    table = Table(title=f"[bold blue]{title}[/bold blue]", box=ROUNDED)
    table.add_column("Property", style=key_style, width=20)
    table.add_column("Value", style=value_style, width=40)
    
    for key, value in data.items():
        # Handle different value types
        if isinstance(value, bool):
            display_value = "✓ Yes" if value else "✗ No"
            style = "green" if value else "red"
            table.add_row(key, f"[{style}]{display_value}[/{style}]")
        elif isinstance(value, (list, tuple)):
            display_value = ", ".join(str(v) for v in value)
            table.add_row(key, display_value)
        elif value is None:
            table.add_row(key, "[dim]Not set[/dim]")
        else:
            table.add_row(key, str(value))
    
    console.print(table)


def center_text(text: str, style: str = "bold") -> Align:
    """
    Center text with Rich alignment.
    
    Args:
        text: Text to center
        style: Text style
        
    Returns:
        Rich Align object
    """
    return Align.center(Text(text, style=style))
