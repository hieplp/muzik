"""
Settings utility functions.
"""

import re
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def validate_email_utility() -> None:
    """Email validation utility."""
    console.print("[blue]Email Validation Utility[/blue]")
    
    email = Prompt.ask("Enter email address to validate")
    if not email:
        console.print("[yellow]No email provided[/yellow]")
        return
    
    # Simple email validation
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