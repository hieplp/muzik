"""
Generic API client for making HTTP requests.
"""

import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, Timeout
from rich.console import Console
from urllib3.util.retry import Retry

console = Console()


class APIClient:
    """Generic HTTP API client with retry logic and error handling."""

    def __init__(
            self,
            base_url: str = "",
            timeout: int = 30,
            max_retries: int = 3,
            backoff_factor: float = 0.3,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
            headers: Default headers for requests
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

        # Set up retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=backoff_factor,
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        if headers:
            self.session.headers.update(headers)

    def _make_request(
            self,
            method: str,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            auth: Optional[tuple] = None,
            **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with error handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: URL parameters
            data: Form data or raw data
            json_data: JSON data
            headers: Additional headers
            auth: Authentication tuple (username, password)
            **kwargs: Additional request arguments
            
        Returns:
            Response object
            
        Raises:
            RequestException: On request failure
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint

        request_kwargs = {
            'timeout': self.timeout,
            'params': params,
            'headers': headers,
            'auth': auth,
            **kwargs
        }

        if json_data is not None:
            request_kwargs['json'] = json_data
        elif data is not None:
            request_kwargs['data'] = data

        try:
            response = self.session.request(method, url, **request_kwargs)
            response.raise_for_status()
            return response

        except Timeout:
            console.print(f"[red]Request timeout for {method} {url}[/red]")
            raise
        except RequestException as e:
            console.print(f"[red]Request failed for {method} {url}: {e}[/red]")
            raise

    def get(
            self,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> requests.Response:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params, headers=headers, **kwargs)

    def post(
            self,
            endpoint: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> requests.Response:
        """Make POST request."""
        return self._make_request("POST", endpoint, data=data, json_data=json_data, headers=headers, **kwargs)

    def put(
            self,
            endpoint: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> requests.Response:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, data=data, json_data=json_data, headers=headers, **kwargs)

    def delete(
            self,
            endpoint: str,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> requests.Response:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint, headers=headers, **kwargs)

    def get_json(
            self,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Make GET request and return JSON response.
        
        Returns:
            JSON response as dictionary
        """
        response = self.get(endpoint, params=params, headers=headers, **kwargs)
        return response.json()

    def post_json(
            self,
            endpoint: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Make POST request and return JSON response.
        
        Returns:
            JSON response as dictionary
        """
        response = self.post(endpoint, data=data, json_data=json_data, headers=headers, **kwargs)
        return response.json()

    def set_auth_header(self, token: str, token_type: str = "Bearer") -> None:
        """
        Set authorization header.
        
        Args:
            token: Access token
            token_type: Token type (Bearer, Basic, etc.)
        """
        self.session.headers["Authorization"] = f"{token_type} {token}"

    def remove_auth_header(self) -> None:
        """Remove authorization header."""
        self.session.headers.pop("Authorization", None)

    def close(self) -> None:
        """Close the session."""
        self.session.close()


class SpotifyAPIClient(APIClient):
    """Specialized API client for Spotify Web API."""

    ACCOUNTS_BASE_URL = "https://accounts.spotify.com"
    API_BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Spotify API client.
        
        Args:
            client_id: Spotify client ID
            client_secret: Spotify client secret
        """
        super().__init__(base_url=self.API_BASE_URL)
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None

    def get_client_credentials_token(self) -> Dict[str, Any]:
        """
        Get access token using client credentials flow.
        
        Example curl equivalent:
        curl -X POST "https://accounts.spotify.com/api/token" \
             -H "Content-Type: application/x-www-form-urlencoded" \
             -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"
        
        Returns:
            Token response dictionary
        """
        auth_client = APIClient(base_url=self.ACCOUNTS_BASE_URL)

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = auth_client.post("/api/token", data=urlencode(data), headers=headers)
        token_data = response.json()

        # Store token and expiration
        self.access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self.token_expires_at = time.time() + expires_in

        # Set authorization header
        self.set_auth_header(self.access_token)

        auth_client.close()
        return token_data

    def refresh_token_if_needed(self) -> None:
        """Refresh token if it's expired or about to expire."""
        if (not self.access_token or
                not self.token_expires_at or
                time.time() >= (self.token_expires_at - 300)):  # Refresh 5 minutes before expiry

            console.print("[blue]Refreshing Spotify access token...[/blue]")
            self.get_client_credentials_token()

    def make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make authenticated request to Spotify API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            Response object
        """
        self.refresh_token_if_needed()
        return self._make_request(method, endpoint, **kwargs)

    def search(
            self,
            query: str,
            search_type: str = "track",
            limit: int = 20,
            offset: int = 0,
            market: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for items on Spotify.
        
        Args:
            query: Search query
            search_type: Type of search (track, artist, album, playlist)
            limit: Number of results to return
            offset: Offset for pagination
            market: Market (country code)
            
        Returns:
            Search results
        """
        params = {
            "q": query,
            "type": search_type,
            "limit": limit,
            "offset": offset
        }

        if market:
            params["market"] = market

        response = self.make_authenticated_request("GET", "/search", params=params)
        return response.json()
