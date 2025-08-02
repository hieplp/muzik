"""
Application information and status functionality.
"""

from rich.console import Console

console = Console()


def show_application_menu() -> None:
    """Show the application menu."""
    from .menu import Menu

    menu = Menu("📱 Application")

    menu.add_item(
        "Application info",
        lambda: console.print("[blue]Muzik v0.1.0 - A modern Python console application[/blue]"),
        "Show application information",
        "1"
    )

    menu.add_item(
        "Application status",
        lambda: console.print("[green]✓ Application is running and ready[/green]"),
        "Check application status",
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
