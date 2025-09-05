# FW SCC MCP Server - Modular Structure

This is a restructured version of the SCC FW MCP Server with a more modular design. The key improvements in this version include:

## Directory Structure

```
ise_mcp_server/
├── __init__.py
├── __main__.py          # Command-line entry point
├── server.py            # Main server class
├── config/              # Configuration-related modules
│   ├── __init__.py
│   ├── settings.py      # Environment variables and settings
│   ├── urls.json        # URL definitions for the API endpoints
│   └── urls_config.py   # Functions to load URLs configuration
├── core/                # Core functionality
│   ├── __init__.py
│   ├── models.py        # Pydantic models for tool inputs
│   └── utils.py         # Utility functions
├── api/                 # API client
│   ├── __init__.py
│   └── client.py        # ISE API client
└── tools/               # Tool-related modules
    ├── __init__.py
    └── factory.py       # Tool factory
```

## Key Components

- **FWMCPServer**: Main server class in `server.py` that initializes the FastMCP instance, registers tools, and starts the server.
- **ToolFactory**: Factory class in `tools/factory.py` that creates tool functions from URL definitions.
- **FirewallManagerApiClient**: Client class in `api/client.py` for making API requests to Cisco SCC FW.
- **Settings**: Configuration module in `config/settings.py` that loads and validates environment variables.
- **URLs Configuration**: Functions in `config/urls_config.py` for loading the URL definitions from a JSON file.
- **Models**: Pydantic models in `core/models.py` for tool inputs.
- **Utilities**: Utility functions in `core/utils.py` for common tasks.

