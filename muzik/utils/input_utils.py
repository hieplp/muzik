"""
Enhanced input utilities using Rich for console applications.
"""

import sys
from typing import Optional, List

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table

console = Console()


def get_single_char() -> str:
    """
    Get a single character input with arrow key support.
    
    Returns:
        str: The character or arrow key direction ('up', 'down', 'left', 'right')
    
    Raises:
        KeyboardInterrupt: When Ctrl+C is pressed
    """
    try:
        if sys.platform == "win32":
            import msvcrt
            char = msvcrt.getch()
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
        console.print("\n[dim]Press Enter to exit...[/dim]")
        input()
        raise
    except Exception:
        try:
            return console.input("").strip()
        except KeyboardInterrupt:
            raise


def rich_prompt(
        message: str,
        default: Optional[str] = None,
        password: bool = False,
        choices: Optional[List[str]] = None,
        show_choices: bool = True,
        show_default: bool = True,
) -> str:
    """
    Enhanced prompt using Rich with better styling and validation.
    
    Args:
        message: Prompt message
        default: Default value
        password: Whether to hide input
        choices: List of valid choices
        show_choices: Whether to display choices
        show_default: Whether to show default value
        
    Returns:
        User input as string
    """
    try:
        return Prompt.ask(
            f"[bold cyan]{message}[/bold cyan]",
            default=default,
            password=password,
            choices=choices,
            show_choices=show_choices,
            show_default=show_default,
            console=console
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise


def rich_confirm(
        message: str,
        default: Optional[bool] = None,
        yes_text: str = "yes",
        no_text: str = "no"
) -> bool:
    """
    Enhanced confirmation dialog using Rich.
    
    Args:
        message: Confirmation message
        default: Default choice
        yes_text: Text for yes option
        no_text: Text for no option
        
    Returns:
        User confirmation as boolean
    """
    try:
        return Confirm.ask(
            f"[bold yellow]{message}[/bold yellow]",
            default=default,
            console=console
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise


def rich_int_prompt(
        message: str,
        default: Optional[int] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
) -> int:
    """
    Enhanced integer prompt using Rich with validation.
    
    Args:
        message: Prompt message
        default: Default value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        User input as integer
    """
    try:
        while True:
            try:
                value = IntPrompt.ask(
                    f"[bold cyan]{message}[/bold cyan]",
                    default=default,
                    console=console
                )

                if min_value is not None and value < min_value:
                    console.print(f"[red]Value must be at least {min_value}[/red]")
                    continue

                if max_value is not None and value > max_value:
                    console.print(f"[red]Value must be at most {max_value}[/red]")
                    continue

                return value

            except ValueError:
                console.print("[red]Please enter a valid integer[/red]")
                continue

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise


def rich_choice_menu(
        title: str,
        choices: List[str],
        descriptions: Optional[List[str]] = None,
        allow_numbers: bool = True,
        show_quit: bool = True
) -> Optional[str]:
    """
    Create a Rich-styled choice menu.
    
    Args:
        title: Menu title
        choices: List of choice options
        descriptions: Optional descriptions for each choice
        allow_numbers: Allow numeric selection
        show_quit: Show quit option
        
    Returns:
        Selected choice or None if quit
    """
    if descriptions and len(descriptions) != len(choices):
        descriptions = None

    table = Table(title=f"[bold blue]{title}[/bold blue]", show_header=False)
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Choice", style="white", width=30)
    if descriptions:
        table.add_column("Description", style="dim", width=40)

    # Add choices to table
    for i, choice in enumerate(choices, 1):
        option = f"[{i}]" if allow_numbers else ""
        desc = descriptions[i - 1] if descriptions else ""

        if descriptions:
            table.add_row(option, choice, desc)
        else:
            table.add_row(option, choice)

    if show_quit:
        table.add_row("", "─" * 30, "")
        table.add_row("[q]", "Quit", "Exit menu")

    console.print(table)

    # Build valid choices
    valid_choices = []
    if allow_numbers:
        valid_choices.extend([str(i) for i in range(1, len(choices) + 1)])
    if show_quit:
        valid_choices.append("q")

    try:
        choice = Prompt.ask(
            "[bold cyan]Select option[/bold cyan]",
            choices=valid_choices,
            show_choices=False,
            console=console
        )

        if choice == "q":
            return None

        if allow_numbers and choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(choices):
                return choices[index]

        return choice

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        return None


def display_loading_with_status(
        tasks: List[str],
        status_text: str = "Processing..."
) -> None:
    """
    Display a loading interface with multiple tasks.
    
    Args:
        tasks: List of task descriptions
        status_text: Main status text
    """
    table = Table(title=f"[bold blue]{status_text}[/bold blue]")
    table.add_column("Task", style="cyan")
    table.add_column("Status", style="green")

    for task in tasks:
        table.add_row(task, "⏳ Pending")

    console.print(table)


def pause_for_user(message: str = "Press Enter to continue...") -> None:
    """
    Pause execution with a Rich-styled message.
    
    Args:
        message: Message to display
    """
    try:
        console.print(f"\n[dim]{message}[/dim]")
        input()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise
