"""
Display utilities for Spotify data.
"""

from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

console = Console()


def display_tracks_table(tracks: List[Dict[str, Any]], title: str = "Tracks") -> None:
    """
    Display tracks in a formatted table.
    
    Args:
        tracks: List of track dictionaries
        title: Table title
    """
    if not tracks:
        console.print("[yellow]No tracks found[/yellow]")
        return
    
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("#", width=3)
    table.add_column("Title", width=30)
    table.add_column("Artists", width=25)
    table.add_column("Album", width=25)
    table.add_column("Duration", width=8)
    table.add_column("Popularity", width=10)
    
    for i, track in enumerate(tracks, 1):
        # Format duration
        duration_ms = track.get('duration_ms', 0)
        duration_min = duration_ms // 60000
        duration_sec = (duration_ms % 60000) // 1000
        duration_str = f"{duration_min}:{duration_sec:02d}"
        
        # Format artists
        artists = ", ".join(track.get('artists', []))
        
        # Format popularity
        popularity = track.get('popularity', 0)
        popularity_bar = "█" * (popularity // 10) + "░" * (10 - popularity // 10)
        
        table.add_row(
            str(i),
            track.get('name', 'Unknown'),
            artists,
            track.get('album', 'Unknown'),
            duration_str,
            f"{popularity} {popularity_bar}"
        )
    
    console.print(table)


def display_playlists_table(playlists: List[Dict[str, Any]], title: str = "Playlists") -> None:
    """
    Display playlists in a formatted table.
    
    Args:
        playlists: List of playlist dictionaries
        title: Table title
    """
    if not playlists:
        console.print("[yellow]No playlists found[/yellow]")
        return
    
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("#", width=3)
    table.add_column("Name", width=30)
    table.add_column("Description", width=40)
    table.add_column("Tracks", width=8)
    table.add_column("Public", width=8)
    
    for i, playlist in enumerate(playlists, 1):
        description = playlist.get('description', '')
        if len(description) > 37:
            description = description[:37] + "..."
        
        table.add_row(
            str(i),
            playlist.get('name', 'Unknown'),
            description,
            str(playlist.get('tracks_count', 0)),
            "Yes" if playlist.get('public', False) else "No"
        )
    
    console.print(table)


def display_albums_table(albums: List[Dict[str, Any]], title: str = "Albums") -> None:
    """
    Display albums in a formatted table.
    
    Args:
        albums: List of album dictionaries
        title: Table title
    """
    if not albums:
        console.print("[yellow]No albums found[/yellow]")
        return
    
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("#", width=3)
    table.add_column("Album", width=30)
    table.add_column("Artists", width=25)
    table.add_column("Release Date", width=12)
    table.add_column("Tracks", width=8)
    table.add_column("Type", width=10)
    
    for i, album in enumerate(albums, 1):
        # Format artists
        artists = ", ".join(album.get('artists', []))
        
        # Format release date
        release_date = album.get('release_date', '')
        if len(release_date) > 10:
            release_date = release_date[:10]  # Keep only YYYY-MM-DD part
        
        table.add_row(
            str(i),
            album.get('name', 'Unknown'),
            artists,
            release_date,
            str(album.get('total_tracks', 0)),
            album.get('album_type', 'album').title()
        )
    
    console.print(table)


def display_artists_table(artists: List[Dict[str, Any]], title: str = "Artists") -> None:
    """
    Display artists in a formatted table.
    
    Args:
        artists: List of artist dictionaries
        title: Table title
    """
    if not artists:
        console.print("[yellow]No artists found[/yellow]")
        return
    
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("#", width=3)
    table.add_column("Artist", width=30)
    table.add_column("Genres", width=30)
    table.add_column("Followers", width=12)
    table.add_column("Popularity", width=10)
    
    for i, artist in enumerate(artists, 1):
        # Format genres
        genres = ", ".join(artist.get('genres', []))
        if len(genres) > 27:
            genres = genres[:27] + "..."
        
        # Format followers
        followers = artist.get('followers', 0)
        if followers >= 1000000:
            followers_str = f"{followers / 1000000:.1f}M"
        elif followers >= 1000:
            followers_str = f"{followers / 1000:.1f}K"
        else:
            followers_str = str(followers)
        
        # Format popularity
        popularity = artist.get('popularity', 0)
        popularity_bar = "█" * (popularity // 10) + "░" * (10 - popularity // 10)
        
        table.add_row(
            str(i),
            artist.get('name', 'Unknown'),
            genres or "N/A",
            followers_str,
            f"{popularity} {popularity_bar}"
        )
    
    console.print(table)


def display_track_details(track: Dict[str, Any]) -> None:
    """
    Display detailed information about a single track.
    
    Args:
        track: Track dictionary
    """
    table = Table(title=f"Track Details: {track.get('name', 'Unknown')}", show_header=False)
    table.add_column("Property", style="bold", width=15)
    table.add_column("Value", width=50)
    
    # Basic info
    table.add_row("Title", track.get('name', 'Unknown'))
    table.add_row("Artists", ", ".join(track.get('artists', [])))
    table.add_row("Album", track.get('album', 'Unknown'))
    
    # Duration
    duration_ms = track.get('duration_ms', 0)
    duration_min = duration_ms // 60000
    duration_sec = (duration_ms % 60000) // 1000
    table.add_row("Duration", f"{duration_min}:{duration_sec:02d}")
    
    # Additional info
    if 'popularity' in track:
        table.add_row("Popularity", str(track['popularity']))
    if 'explicit' in track:
        table.add_row("Explicit", "Yes" if track['explicit'] else "No")
    if 'track_number' in track:
        table.add_row("Track Number", str(track['track_number']))
    if 'disc_number' in track:
        table.add_row("Disc Number", str(track['disc_number']))
    if 'preview_url' in track and track['preview_url']:
        table.add_row("Preview", "Available")
    if 'external_url' in track:
        table.add_row("Spotify URL", track['external_url'])
    
    console.print(table)


def display_album_details(album: Dict[str, Any]) -> None:
    """
    Display detailed information about a single album.
    
    Args:
        album: Album dictionary
    """
    table = Table(title=f"Album Details: {album.get('name', 'Unknown')}", show_header=False)
    table.add_column("Property", style="bold", width=15)
    table.add_column("Value", width=50)
    
    # Basic info
    table.add_row("Album", album.get('name', 'Unknown'))
    table.add_row("Artists", ", ".join(album.get('artists', [])))
    table.add_row("Release Date", album.get('release_date', 'Unknown'))
    table.add_row("Total Tracks", str(album.get('total_tracks', 0)))
    table.add_row("Album Type", album.get('album_type', 'album').title())
    
    # Additional info
    if 'genres' in album and album['genres']:
        table.add_row("Genres", ", ".join(album['genres']))
    if 'label' in album:
        table.add_row("Label", album['label'])
    if 'popularity' in album:
        table.add_row("Popularity", str(album['popularity']))
    if 'external_url' in album:
        table.add_row("Spotify URL", album['external_url'])
    
    console.print(table)
    
    # Display tracks if available
    if 'tracks' in album and album['tracks']:
        console.print("\n[bold]Album Tracks:[/bold]")
        display_tracks_table(album['tracks'], f"Tracks from {album.get('name', 'Album')}")


def display_artist_details(artist: Dict[str, Any]) -> None:
    """
    Display detailed information about a single artist.
    
    Args:
        artist: Artist dictionary
    """
    table = Table(title=f"Artist Details: {artist.get('name', 'Unknown')}", show_header=False)
    table.add_column("Property", style="bold", width=15)
    table.add_column("Value", width=50)
    
    # Basic info
    table.add_row("Artist", artist.get('name', 'Unknown'))
    table.add_row("Popularity", str(artist.get('popularity', 0)))
    
    # Followers
    followers = artist.get('followers', 0)
    if followers >= 1000000:
        followers_str = f"{followers:,} ({followers / 1000000:.1f}M)"
    elif followers >= 1000:
        followers_str = f"{followers:,} ({followers / 1000:.1f}K)"
    else:
        followers_str = f"{followers:,}"
    table.add_row("Followers", followers_str)
    
    # Genres
    if 'genres' in artist and artist['genres']:
        table.add_row("Genres", ", ".join(artist['genres']))
    else:
        table.add_row("Genres", "N/A")
    
    if 'external_url' in artist:
        table.add_row("Spotify URL", artist['external_url'])
    
    console.print(table) 