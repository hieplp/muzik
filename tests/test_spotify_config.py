"""
Tests for Spotify configuration utilities.
"""

from unittest.mock import patch

from muzik.core.spotify_config import (
    validate_spotify_config,
    show_spotify_status,
    clear_spotify_settings,
)

from muzik.core.config import Config


class TestSpotifyConfig:
    """Test Spotify configuration utilities."""

    def test_validate_spotify_config_empty(self):
        """Test validation with empty config."""
        config = Config()
        assert not validate_spotify_config(config)

    def test_validate_spotify_config_partial(self):
        """Test validation with partial config."""
        config = Config()
        config.set("spotify.client_id", "test_client_id")
        config.set("spotify.client_secret", "test_client_secret")
        # Missing access_token and refresh_token
        assert not validate_spotify_config(config)

    def test_validate_spotify_config_complete(self):
        """Test validation with complete config."""
        config = Config()
        config.set("spotify.client_id", "test_client_id")
        config.set("spotify.client_secret", "test_client_secret")
        config.set("spotify.access_token", "test_access_token")
        config.set("spotify.refresh_token", "test_refresh_token")
        assert validate_spotify_config(config)

    @patch('muzik.core.spotify_config.Confirm.ask', return_value=True)
    def test_clear_spotify_settings(self, mock_confirm):
        """Test clearing Spotify settings."""
        config = Config()
        config.set("spotify.client_id", "test_client_id")
        config.set("spotify.client_secret", "test_client_secret")
        config.set("spotify.access_token", "test_access_token")
        config.set("spotify.refresh_token", "test_refresh_token")

        # Verify settings are set
        assert config.get("spotify.client_id") == "test_client_id"
        assert config.get("spotify.access_token") == "test_access_token"

        # Clear settings
        clear_spotify_settings(config)

        # Verify settings are cleared
        assert config.get("spotify.client_id") == ""
        assert config.get("spotify.client_secret") == ""
        assert config.get("spotify.access_token") == ""
        assert config.get("spotify.refresh_token") == ""

        # Verify Confirm.ask was called
        mock_confirm.assert_called_once()

    @patch('muzik.core.spotify_config.console.print')
    def test_show_spotify_status(self, mock_print):
        """Test showing Spotify status."""
        config = Config()
        config.set("spotify.client_id", "test_client_id")
        config.set("spotify.client_secret", "test_client_secret")
        config.set("spotify.access_token", "test_access_token")
        config.set("spotify.refresh_token", "test_refresh_token")

        show_spotify_status(config)

        # Verify that console.print was called
        assert mock_print.called
