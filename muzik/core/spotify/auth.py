"""
Spotify authentication and token management.
"""

from typing import Optional

from ..config import Config


class SpotifyAuth:
    """Handles Spotify authentication and token management."""
    
    def __init__(self, config: Config):
        """
        Initialize Spotify authentication.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client_id = config.get("spotify.client_id", "")
        self.client_secret = config.get("spotify.client_secret", "")
        self.access_token = config.get("spotify.access_token", "")
        self.refresh_token = config.get("spotify.refresh_token", "")
        self.redirect_uri = config.get("spotify.redirect_uri", "http://localhost:8888/callback")
    
    def is_configured(self) -> bool:
        """
        Check if Spotify API is properly configured.
        
        Returns:
            True if configured, False otherwise
        """
        return bool(self.client_id and self.client_secret)
    
    def set_credentials(self, client_id: str, client_secret: str) -> None:
        """
        Set Spotify client credentials.
        
        Args:
            client_id: Spotify client ID
            client_secret: Spotify client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.config.set("spotify.client_id", client_id)
        self.config.set("spotify.client_secret", client_secret)
    
    def set_tokens(self, access_token: str, refresh_token: Optional[str] = None) -> None:
        """
        Set Spotify access tokens.
        
        Args:
            access_token: Spotify access token
            refresh_token: Optional refresh token
        """
        self.access_token = access_token
        self.config.set("spotify.access_token", access_token)
        
        if refresh_token:
            self.refresh_token = refresh_token
            self.config.set("spotify.refresh_token", refresh_token)
    
    def clear_settings(self) -> None:
        """Clear all Spotify settings."""
        self.config.set("spotify.client_id", "")
        self.config.set("spotify.client_secret", "")
        self.config.set("spotify.access_token", "")
        self.config.set("spotify.refresh_token", "")
        
        self.client_id = ""
        self.client_secret = ""
        self.access_token = ""
        self.refresh_token = ""
    
    def get_status(self) -> dict:
        """
        Get Spotify API configuration status.
        
        Returns:
            Dictionary with configuration status
        """
        return {
            "configured": self.is_configured(),
            "client_id_set": bool(self.client_id),
            "client_secret_set": bool(self.client_secret),
            "access_token_set": bool(self.access_token),
            "refresh_token_set": bool(self.refresh_token),
            "client_id": self.client_id[:10] + "..." if self.client_id else "",
        }
    
    def test_connection(self) -> tuple[bool, Optional[str]]:
        """
        Test API connection.
        
        Returns:
            Tuple of (success, error_message)
        """
        if not self.is_configured():
            return False, "Spotify API is not configured"
        
        try:
            from muzik.utils.api_client import SpotifyAPIClient
            api_client = SpotifyAPIClient(self.client_id, self.client_secret)
            api_client.get_client_credentials_token()
            api_client.close()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_api_client(self):
        """
        Get configured Spotify API client.
        
        Returns:
            SpotifyAPIClient instance or None if not configured
        """
        if not self.is_configured():
            return None
        
        try:
            from muzik.utils.api_client import SpotifyAPIClient
            client = SpotifyAPIClient(self.client_id, self.client_secret)
            client.get_client_credentials_token()
            return client
        except Exception:
            return None


def validate_spotify_config(config: Config) -> bool:
    """
    Validate Spotify configuration.
    
    Args:
        config: Application configuration
        
    Returns:
        True if valid, False otherwise
    """
    auth = SpotifyAuth(config)
    return auth.is_configured() 