"""
YouTube audio player with pygame integration.
"""

import time
import threading
from typing import Dict, Any, Optional

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from .downloader import YoutubeDownloader

console = Console()


class YoutubePlayer:
    """Handles YouTube audio playback with interactive controls."""
    
    def __init__(self):
        """Initialize the YouTube player."""
        self.downloader = YoutubeDownloader()
        self.is_playing = False
        self.current_file = None
        self._user_input = ""
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
            except pygame.error:
                console.print("[red]Warning: Audio system not available[/red]")
    
    def play_track(self, track_name: str, artists: str, lyrics: Optional[str] = None) -> bool:
        """
        Play a track from YouTube with interactive controls.
        
        Args:
            track_name: Name of the track
            artists: Artist names
            lyrics: Optional lyrics for display
            
        Returns:
            True if playback was successful, False otherwise
        """
        if not PYGAME_AVAILABLE:
            console.print("[red]❌ Audio playback not available. Install pygame: pip install pygame[/red]")
            return False
        
        # Get video info first for user feedback
        console.print(f"[green]🔍 Searching for '{track_name}' by {artists} on YouTube...[/green]")
        video_info = self.downloader.get_video_info(track_name, artists)
        
        if video_info:
            console.print(f"[green]✅ Found: {video_info.get('title', 'Unknown')}[/green]")
            # Get duration from video info
            duration = video_info.get('duration', 0)
            if duration:
                minutes, seconds = divmod(int(duration), 60)
                console.print(f"[dim]Duration: {minutes}:{seconds:02d}[/dim]")
        else:
            console.print("[red]❌ Could not find track on YouTube[/red]")
            return False
        
        # Download audio file
        console.print("[yellow]📥 Downloading audio for playback...[/yellow]")
        audio_file = self.downloader.search_and_download(track_name, artists)
        
        if not audio_file:
            console.print("[red]❌ Failed to download audio[/red]")
            return False
        
        self.current_file = audio_file
        duration = video_info.get('duration', 0) or 300  # Fallback to 5 minutes if no duration
        
        try:
            console.print(f"[green]🎧 Loading: {track_name} by {artists}[/green]")
            
            # Load and play the downloaded file
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            self.is_playing = True
            paused = False
            show_lyrics = False
            
            # Start the playback with progress tracking
            return self._run_playback_loop(track_name, artists, lyrics, duration)
            
        except pygame.error as e:
            console.print(f"[red]❌ Audio playback error: {e}[/red]")
            self._cleanup_current_file()
            return False
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {e}[/red]")
            self._cleanup_current_file()
            return False
    
    def _run_playback_loop(self, track_name: str, artists: str, lyrics: Optional[str], duration: int) -> bool:
        """
        Run the main playback loop with progress tracking and controls.
        
        Args:
            track_name: Track name
            artists: Artists
            lyrics: Optional lyrics
            duration: Track duration in seconds
            
        Returns:
            True if playback completed successfully
        """
        paused = False
        show_lyrics = False
        start_time = time.time()
        user_input = ""
        
        # Start input monitoring in separate thread
        input_thread = threading.Thread(target=self._monitor_input, daemon=True)
        input_thread.start()
        
        try:
            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=40),
                "[progress.percentage]{task.percentage:>3.0f}%",
                "•",
                TextColumn("[blue]{task.completed:.0f}s"),
                "/",
                TextColumn("[blue]{task.total:.0f}s"),
                TimeRemainingColumn(),
                console=console,
                transient=False
            ) as progress:
                
                task = progress.add_task("🎵 Playing", total=duration, completed=0)
                
                console.print(f"[bold green]🎧 Now Playing: {track_name} by {artists}[/bold green]")
                console.print("[dim]Controls: [SPACE]=Pause/Resume, [L]=Lyrics, [S]=Stop, [Q]=Quit[/dim]")
                
                if show_lyrics and lyrics:
                    console.print("\n")
                    self._display_lyrics_panel(track_name, artists, lyrics)
                
                while self.is_playing and pygame.mixer.music.get_busy():
                    # Calculate elapsed time (accounting for pauses)
                    if not paused:
                        elapsed = time.time() - start_time
                    else:
                        # Don't update time when paused
                        elapsed = progress.tasks[0].completed
                    
                    # Update progress
                    progress.update(task, completed=min(elapsed, duration))
                    
                    # Handle user input
                    if hasattr(self, '_user_input') and self._user_input:
                        char = self._user_input.lower()
                        self._user_input = ""  # Clear input
                        
                        if char in ['q', 's']:
                            self.is_playing = False
                            break
                        elif char in [' ', 'p']:  # Space or 'p' for pause/resume
                            if paused:
                                pygame.mixer.music.unpause()
                                paused = False
                                start_time = time.time() - elapsed  # Adjust start time
                                progress.update(task, description="🎵 Playing")
                                console.print("\n[green]▶️  Resumed[/green]")
                            else:
                                pygame.mixer.music.pause()
                                paused = True
                                progress.update(task, description="⏸️  Paused")
                                console.print("\n[yellow]⏸️  Paused[/yellow]")
                        elif char == 'l' and lyrics:  # Toggle lyrics
                            show_lyrics = not show_lyrics
                            if show_lyrics:
                                console.print("\n")
                                self._display_lyrics_panel(track_name, artists, lyrics)
                            else:
                                console.clear()
                                console.print(f"[bold green]🎧 Now Playing: {track_name} by {artists}[/bold green]")
                                console.print("[dim]Controls: [SPACE]=Pause/Resume, [L]=Lyrics, [S]=Stop, [Q]=Quit[/dim]")
                    
                    # Check if track finished
                    if elapsed >= duration:
                        break
                        
                    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
                pygame.mixer.music.stop()
                progress.update(task, completed=duration, description="✅ Completed")
                
        except KeyboardInterrupt:
            self.is_playing = False
            console.print("\n[yellow]⏹️  Playback interrupted[/yellow]")
        
        # Cleanup
        self._cleanup_current_file()
        console.print("\n[green]✅ Playback finished[/green]")
        input("\nPress Enter to continue...")
        return True
    
    def _monitor_input(self):
        """Monitor keyboard input in a separate thread."""
        import sys
        
        try:
            # Try termios first (Unix/Linux/macOS)
            import termios
            import tty
            
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            
            while self.is_playing:
                try:
                    char = sys.stdin.read(1)
                    if char:
                        self._user_input = char
                except:
                    break
                    
        except ImportError:
            # Fallback for Windows
            try:
                import msvcrt
                while self.is_playing:
                    if msvcrt.kbhit():
                        char = msvcrt.getch().decode('utf-8')
                        self._user_input = char
                    time.sleep(0.1)
            except ImportError:
                # Final fallback - simple input prompting
                self._simple_input_fallback()
        except Exception:
            # If termios fails, try simple fallback
            self._simple_input_fallback()
        finally:
            try:
                # Restore terminal settings
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass
    
    def _simple_input_fallback(self):
        """Simple input fallback that works on all systems."""
        console.print("\n[yellow]⚠️  Advanced controls not available on this system[/yellow]")
        console.print("[dim]Available commands:[/dim]")
        console.print("[dim]• Type 'p' + Enter to pause/resume[/dim]")
        console.print("[dim]• Type 'l' + Enter to toggle lyrics[/dim]")
        console.print("[dim]• Type 'q' + Enter to quit[/dim]")
        
        import threading
        def simple_input():
            while self.is_playing:
                try:
                    command = input().strip().lower()
                    if command:
                        self._user_input = command[0]  # Use first character
                except (EOFError, KeyboardInterrupt):
                    self._user_input = 'q'
                    break
                except:
                    pass
        
        input_thread = threading.Thread(target=simple_input, daemon=True)
        input_thread.start()
    

    
    def _display_lyrics_panel(self, track_name: str, artists: str, lyrics: str) -> None:
        """
        Display lyrics in a formatted panel.
        
        Args:
            track_name: Track name
            artists: Artists
            lyrics: Lyrics text
        """
        # Clean and format lyrics
        lines = lyrics.strip().split('\n')
        display_lines = lines[:12] if len(lines) > 12 else lines
        
        lyrics_text = Text()
        for line in display_lines:
            if line.strip():
                lyrics_text.append(line.strip() + "\n", style="white")
        
        if len(lines) > 12:
            lyrics_text.append("...\n[More lyrics available]", style="dim")
        
        panel = Panel(
            lyrics_text,
            title=f"[bold green]🎤 {track_name} - {artists}[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        console.print(panel)
    
    def _cleanup_current_file(self):
        """Clean up the current temporary file."""
        if self.current_file:
            try:
                import os
                os.unlink(self.current_file)
            except Exception:
                pass
            self.current_file = None
    
    def stop_playback(self):
        """Stop current playback and cleanup."""
        self.is_playing = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass
        self._cleanup_current_file()
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.stop_playback()
        if hasattr(self, 'downloader'):
            self.downloader.cleanup_temp_files()