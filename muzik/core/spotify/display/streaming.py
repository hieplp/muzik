"""
Spotify streaming functionality with audio playback and lyrics display.
"""

import webbrowser
import threading
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

console = Console()


class SpotifyStreamer:
    """Handles Spotify streaming, preview playback, and lyrics display."""
    
    def __init__(self):
        """Initialize the Spotify streamer."""
        self.is_playing = False
        self.current_thread = None
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except pygame.error:
                console.print("[red]Warning: Audio system not available[/red]")
    
    def play_preview(self, track: Dict[str, Any]) -> None:
        """
        Play a 30-second preview of the track.
        
        Args:
            track: Track dictionary with preview_url
        """
        preview_url = track.get('preview_url')
        
        if not preview_url:
            console.print("[red]❌ No preview available for this track[/red]")
            input("\nPress Enter to continue...")
            return
        
        if not PYGAME_AVAILABLE:
            console.print("[red]❌ Audio playback not available. Install pygame: pip install pygame[/red]")
            console.print(f"[blue]Preview URL: {preview_url}[/blue]")
            input("\nPress Enter to continue...")
            return
        
        try:
            console.print(f"[green]🎵 Playing preview: {track.get('name', 'Unknown')}[/green]")
            console.print("[dim]Press 's' to stop, any other key to pause/resume[/dim]")
            
            # Download and play preview
            response = requests.get(preview_url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Save preview to temporary file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            try:
                pygame.mixer.music.load(tmp_file_path)
                pygame.mixer.music.play()
                
                self.is_playing = True
                paused = False
                
                # Interactive playback control
                with Progress(
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=console,
                    transient=True
                ) as progress:
                    
                    task = progress.add_task("Playing preview...", total=30)
                    
                    start_time = time.time()
                    while self.is_playing and pygame.mixer.music.get_busy():
                        elapsed = time.time() - start_time
                        if elapsed >= 30:  # 30-second preview
                            break
                        
                        progress.update(task, completed=elapsed)
                        
                        # Check for user input (non-blocking)
                        try:
                            import select
                            import sys
                            
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                char = sys.stdin.read(1).lower()
                                if char == 's':
                                    self.is_playing = False
                                    break
                                else:
                                    if paused:
                                        pygame.mixer.music.unpause()
                                        console.print("[green]▶️ Resumed[/green]")
                                        paused = False
                                    else:
                                        pygame.mixer.music.pause()
                                        console.print("[yellow]⏸️ Paused[/yellow]")
                                        paused = True
                        except (ImportError, OSError):
                            # Fallback for systems without select
                            time.sleep(0.1)
                
                pygame.mixer.music.stop()
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except OSError:
                    pass
            
            console.print("[green]✅ Preview finished[/green]")
            
        except requests.RequestException as e:
            console.print(f"[red]❌ Failed to download preview: {e}[/red]")
        except pygame.error as e:
            console.print(f"[red]❌ Audio playback error: {e}[/red]")
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {e}[/red]")
        
        input("\nPress Enter to continue...")
    
    def stream_full_track(self, track: Dict[str, Any]) -> None:
        """
        Stream the full track by opening Spotify.
        
        Args:
            track: Track dictionary
        """
        spotify_url = track.get('external_url')
        track_name = track.get('name', 'Unknown')
        artists = ", ".join(track.get('artists', []))
        
        if not spotify_url:
            console.print("[red]❌ No Spotify URL available[/red]")
            input("\nPress Enter to continue...")
            return
        
        console.print(f"[green]🎵 Opening '{track_name}' by {artists} in Spotify...[/green]")
        console.print("[dim]This will open the track in your Spotify app or web browser[/dim]")
        
        # Extract track ID from URL
        track_id = spotify_url.split('/')[-1].split('?')[0]  # Remove query params if any
        
        success = False
        
        try:
            # Method 1: Try opening web URL directly (most reliable)
            webbrowser.open(spotify_url)
            console.print("[green]✅ Opened in web browser[/green]")
            success = True
        except Exception as web_error:
            console.print(f"[yellow]⚠️ Web browser failed: {web_error}[/yellow]")
        
        # Method 2: Try Spotify URI if web failed
        if not success:
            try:
                import subprocess
                import platform
                
                spotify_uri = f"spotify:track:{track_id}"
                
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", spotify_uri], check=True, capture_output=True)
                    console.print("[green]✅ Opened in Spotify app (macOS)[/green]")
                    success = True
                elif platform.system() == "Windows":  # Windows
                    subprocess.run(["start", spotify_uri], shell=True, check=True, capture_output=True)
                    console.print("[green]✅ Opened in Spotify app (Windows)[/green]")
                    success = True
                elif platform.system() == "Linux":  # Linux
                    subprocess.run(["xdg-open", spotify_uri], check=True, capture_output=True)
                    console.print("[green]✅ Opened in Spotify app (Linux)[/green]")
                    success = True
                    
            except (subprocess.CalledProcessError, FileNotFoundError) as app_error:
                console.print(f"[yellow]⚠️ Spotify app open failed: {app_error}[/yellow]")
        
        # Method 3: Final fallback - try webbrowser with URI
        if not success:
            try:
                webbrowser.open(f"spotify:track:{track_id}")
                console.print("[green]✅ Opened with system handler[/green]")
                success = True
            except Exception as uri_error:
                console.print(f"[yellow]⚠️ URI handler failed: {uri_error}[/yellow]")
        
        # If all methods failed, provide manual options
        if not success:
            console.print("[red]❌ Could not automatically open Spotify[/red]")
            console.print(f"[blue]🔗 Manual URL: {spotify_url}[/blue]")
            console.print(f"[blue]🎵 Spotify URI: spotify:track:{track_id}[/blue]")
            console.print("[dim]Copy and paste either URL into Spotify or your browser[/dim]")
        
        input("\nPress Enter to continue...")
    
    def show_lyrics(self, track: Dict[str, Any]) -> None:
        """
        Display lyrics for the track (using a simple lyrics API or placeholder).
        
        Args:
            track: Track dictionary
        """
        track_name = track.get('name', 'Unknown')
        artists = track.get('artists', [])
        artist_name = artists[0] if artists else 'Unknown'
        
        console.print(f"[green]🎤 Fetching lyrics for '{track_name}' by {artist_name}...[/green]")
        
        try:
            # Try to fetch lyrics from a free lyrics API
            lyrics = self._fetch_lyrics(track_name, artist_name)
            
            if lyrics:
                self._display_lyrics(track_name, artist_name, lyrics)
            else:
                self._show_lyrics_placeholder(track_name, artist_name)
                
        except Exception as e:
            console.print(f"[red]❌ Error fetching lyrics: {e}[/red]")
            self._show_lyrics_placeholder(track_name, artist_name)
        
        input("\nPress Enter to continue...")
    
    def _fetch_lyrics(self, track_name: str, artist_name: str) -> Optional[str]:
        """
        Fetch lyrics from a free API.
        
        Args:
            track_name: Name of the track
            artist_name: Name of the artist
            
        Returns:
            Lyrics text or None if not found
        """
        try:
            # Using lyrics.ovh API (free, no API key required)
            url = f"https://api.lyrics.ovh/v1/{artist_name}/{track_name}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('lyrics')
            
        except Exception:
            pass
        
        return None
    
    def _display_lyrics(self, track_name: str, artist_name: str, lyrics: str) -> None:
        """
        Display lyrics in a formatted panel.
        
        Args:
            track_name: Name of the track
            artist_name: Name of the artist
            lyrics: Lyrics text
        """
        console.clear()
        
        # Clean up lyrics text
        lyrics = lyrics.strip()
        if len(lyrics) > 2000:  # Truncate very long lyrics
            lyrics = lyrics[:2000] + "\n\n[... lyrics truncated ...]"
        
        lyrics_text = Text(lyrics, style="white")
        
        panel = Panel(
            lyrics_text,
            title=f"[bold green]🎤 Lyrics: {track_name} - {artist_name}[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        console.print(panel)
    
    def _show_lyrics_placeholder(self, track_name: str, artist_name: str) -> None:
        """
        Show a placeholder when lyrics are not available.
        
        Args:
            track_name: Name of the track
            artist_name: Name of the artist
        """
        placeholder_text = Text()
        placeholder_text.append("🎵 ", style="bold blue")
        placeholder_text.append(f"Lyrics for '{track_name}' by {artist_name}\n\n", style="bold white")
        placeholder_text.append("❌ Lyrics not available\n\n", style="red")
        placeholder_text.append("You can search for lyrics manually at:\n", style="dim")
        placeholder_text.append("• genius.com\n", style="blue")
        placeholder_text.append("• azlyrics.com\n", style="blue")
        placeholder_text.append("• musixmatch.com", style="blue")
        
        panel = Panel(
            placeholder_text,
            title="[bold yellow]🎤 Lyrics[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        console.print(panel)
    
    def open_in_spotify(self, track: Dict[str, Any]) -> None:
        """
        Open the track in Spotify app or web browser.
        
        Args:
            track: Track dictionary
        """
        spotify_url = track.get('external_url')
        
        if not spotify_url:
            console.print("[red]❌ No Spotify URL available[/red]")
            return
        
        # Use the same improved opening logic as stream_full_track
        track_id = spotify_url.split('/')[-1].split('?')[0]
        
        success = False
        
        try:
            webbrowser.open(spotify_url)
            success = True
        except Exception:
            try:
                import subprocess
                import platform
                
                spotify_uri = f"spotify:track:{track_id}"
                
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", spotify_uri], check=True, capture_output=True)
                    success = True
                elif platform.system() == "Windows":  # Windows
                    subprocess.run(["start", spotify_uri], shell=True, check=True, capture_output=True)
                    success = True
                elif platform.system() == "Linux":  # Linux
                    subprocess.run(["xdg-open", spotify_uri], check=True, capture_output=True)
                    success = True
                    
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    webbrowser.open(f"spotify:track:{track_id}")
                    success = True
                except Exception:
                    pass
        
        if not success:
            console.print(f"[red]❌ Could not open Spotify automatically[/red]")
            console.print(f"[blue]Manual URL: {spotify_url}[/blue]")
    
    def stop_playback(self) -> None:
        """Stop any current playback."""
        self.is_playing = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass