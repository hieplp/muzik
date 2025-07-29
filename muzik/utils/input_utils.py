"""
Input utilities for console applications.
"""

import sys
from typing import Optional

from rich.console import Console

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