import os
import logging
from typing import Union, Dict

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FWMCPServer")

# ISE Connection Settings
FIREWALL_BASE_URL = os.getenv("FIREWALL_BASE_URL")
API_KEY = os.getenv("API_KEY")

# Rate Limiting Settings
# Get rate limit values from environment variables with defaults
GLOBAL_RATE_LIMIT = int(os.getenv("FW_GLOBAL_RATE_LIMIT", "30"))  # 30 requests/sec overall

# Validate critical settings
def validate_settings():
    """Validate that all required settings are present."""
    if not FIREWALL_BASE_URL or not API_KEY:
        logger.error("❌ Missing one or more required environment variables: FIREWALL_BASE_URL, API_KEY. Exiting.")
        return False
    return True

# Common HTTP Headers
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# Server Settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_TRANSPORT = "streamable-http"
