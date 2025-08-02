# Muzik - A Modern Python Console Application

A feature-rich Python console application built with modern tools and best practices.

## Features

- 🎵 **Modern CLI Interface** - Built with Typer for beautiful command-line interfaces
- 🎨 **Rich Output** - Beautiful console output with colors and formatting using Rich
- ⚙️ **Configuration Management** - Flexible configuration with YAML files and environment variables
- 🎵 **Spotify Integration** - Search tracks, view playlists, and manage your Spotify library
- 📝 **Comprehensive Logging** - Rich logging with multiple levels and output formats
- 🧪 **Testing Suite** - Full test coverage with pytest
- 🔧 **Development Tools** - Code formatting, linting, and type checking
- 📦 **Modern Packaging** - Standard Python packaging with pyproject.toml

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Development Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd muzik
```

2. Install in development mode:

```bash
make install-dev
```

Or manually:

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Commands

```bash
# Show help
muzik --help

# Show version
muzik --version

# Run hello command
muzik hello --name "Your Name" --count 3

# Show application info
muzik info

# Show application status
muzik status
```

### Configuration

The application supports configuration through:

1. **Environment Variables**:
   ```bash
   export MUZIK_DEBUG=true
   export MUZIK_LOG_LEVEL=DEBUG
   export MUZIK_COLORS=false
   export SPOTIFY_ACCESS_TOKEN=your_access_token
   export SPOTIFY_CLIENT_ID=your_client_id
   export SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

2. **Configuration File** (YAML):
   ```yaml
   app:
     name: "My Custom App"
     debug: true
   logging:
     level: "DEBUG"
   display:
     colors: true
   spotify:
     access_token: "your_access_token"
     refresh_token: "your_refresh_token"
     client_id: "your_client_id"
     client_secret: "your_client_secret"
     redirect_uri: "http://localhost:8888/callback"
   ```

3. **Command Line Options**:
   ```bash
   muzik --verbose --config my-config.yaml
   ```

### Spotify Integration

To use Spotify features, you need to configure your Spotify API credentials:

1. **Get Spotify API Credentials**:
    - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
    - Create a new application
    - Get your Client ID and Client Secret
    - Set up OAuth redirect URI (default: `http://localhost:8888/callback`)

2. **Configure in the Application**:
    - Run the application and go to Settings > Spotify API Settings
    - Enter your Client ID and Client Secret
    - Generate and enter your Access Token and Refresh Token

3. **Available Spotify Features**:
    - Search for tracks by title, artist, or album
    - View your personal playlists
    - Browse playlist contents
    - Get track details and metadata

## Development

### Project Structure

```
muzik/
├── muzik/                 # Main package
│   ├── __init__.py       # Package initialization
│   ├── main.py           # CLI entry point
│   ├── core/             # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py     # Configuration management
│   │   └── logger.py     # Logging setup
│   └── utils/            # Utility functions
│       ├── __init__.py
│       ├── display.py    # Display utilities
│       └── validators.py # Validation functions
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_config.py
│   └── test_validators.py
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
├── Makefile             # Development tasks
└── README.md            # This file
```

### Development Commands

```bash
# Install dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-coverage

# Format code
make format

# Check code formatting
make format-check

# Run linting
make lint

# Run all checks
make check

# Clean build artifacts
make clean

# Run the application
make run
```

### Adding New Commands

To add a new command to the CLI:

1. Add the command function to `muzik/main.py`:

```python
@app.command()
def my_command(
    param: str = typer.Option("default", "--param", "-p", help="Parameter description"),
) -> None:
    """Command description."""
    console.print(f"Executing command with param: {param}")
```

2. The command will be automatically available:

```bash
muzik my-command --param value
```

### Adding New Utilities

1. Create new modules in `muzik/utils/`
2. Add imports to `muzik/utils/__init__.py`
3. Write tests in `tests/`

## Testing

The project uses pytest for testing. Run tests with:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=muzik --cov-report=html

# Run specific test file
pytest tests/test_config.py
```

## Code Quality

The project enforces code quality through:

- **Black** - Code formatting
- **Flake8** - Linting
- **MyPy** - Type checking
- **Pytest** - Testing

Run all quality checks:

```bash
make check
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Dependencies

### Core Dependencies

- **typer** - Modern CLI framework
- **rich** - Rich text and beautiful formatting
- **click** - CLI toolkit
- **colorama** - Cross-platform colored terminal text
- **python-dotenv** - Environment variable management
- **requests** - HTTP library
- **tabulate** - Pretty-print tabular data
- **spotipy** - Spotify Web API wrapper

### Development Dependencies

- **pytest** - Testing framework
- **black** - Code formatter
- **flake8** - Linter
- **mypy** - Type checker

## Version History

- **0.1.0** - Initial release with basic CLI functionality