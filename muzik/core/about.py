"""
About information functionality.
"""

from rich.console import Console

console = Console()


def show_about_menu() -> None:
    """Show the about menu."""
    from .menu import Menu

    menu = Menu("ℹ️ About")

    menu.add_item(
        "Author",
        lambda: console.print("[blue]Created by: Your Name[/blue]\n[blue]Email: your.email@example.com[/blue]"),
        "Information about the author",
        "1"
    )

    menu.add_separator()

    menu.add_item(
        "Back to Main Menu",
        lambda: setattr(menu, 'running', False),
        "Return to main menu",
        "b"
    )

    menu.run()
