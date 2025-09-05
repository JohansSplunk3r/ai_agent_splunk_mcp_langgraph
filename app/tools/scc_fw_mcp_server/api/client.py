"""
API client for communicating with Cisco Security Cloud Control Firewall Manager API.
Supports API key authentication and GET, PUT, POST, DELETE methods.
"""
import httpx
import json
from typing import Dict, Any, Optional
from fastmcp.exceptions import ToolError
from ..config.settings import FIREWALL_BASE_URL, API_KEY, HEADERS, logger, GLOBAL_RATE_LIMIT, RATE_LIMIT_ENABLED, CATEGORY_RATE_LIMITS, get_endpoint_category
from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer
from aiolimiter import AsyncLimiter

class FirewallManagerApiClient:
    """
    Client for making requests to the Cisco Security Cloud Control Firewall Manager API.
    """
    DEFAULT_TIMEOUT = 15
    DEFAULT_CACHE_TTL = 300

    def __init__(self):
        assert API_KEY is not None, "API_KEY environment variable is not set."
        assert FIREWALL_BASE_URL is not None, "FIREWALL_BASE_URL environment variable is not set."
        self.base_url = FIREWALL_BASE_URL
        self.api_key = API_KEY
        self.cache_enabled = False

        logger.info(f"📦 Cisco SCC Firewall API client initialized")


    def _get_headers(self) -> Dict[str, str]:
        headers = HEADERS.copy() if HEADERS else {}
        headers["Authorization"] = f"Bearer {self.api_key}"
        headers["Content-Type"] = "application/json"
        return headers

    async def get(self, api_path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        
        url = f"{self.base_url}{api_path}"
        
        request_params = params or {}
        
        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.get(url, headers=self._get_headers(), params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GET {url} failed: {e.response.status_code} - {e.response.text}")
            raise ToolError(f"GET request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"GET {url} failed: {e}")
            raise ToolError(f"GET request failed: {e}")

    async def put(self, api_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{api_path}"
        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.put(url, headers=self._get_headers(), json=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"PUT {url} failed: {e.response.status_code} - {e.response.text}")
            raise ToolError(f"PUT request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"PUT {url} failed: {e}")
            raise ToolError(f"PUT request failed: {e}")

    async def post(self, api_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{api_path}"
        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(url, headers=self._get_headers(), json=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"POST {url} failed: {e.response.status_code} - {e.response.text}")
            raise ToolError(f"POST request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"POST {url} failed: {e}")
            raise ToolError(f"POST request failed: {e}")

    async def delete(self, api_path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{api_path}"
        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.delete(url, headers=self._get_headers(), params=params)
                response.raise_for_status()
                if response.text:
                    return response.json()
                return {"status": "deleted"}
        except httpx.HTTPStatusError as e:
            logger.error(f"DELETE {url} failed: {e.response.status_code} - {e.response.text}")
            raise ToolError(f"DELETE request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"DELETE {url} failed: {e}")
            raise ToolError(f"DELETE request failed: {e}")