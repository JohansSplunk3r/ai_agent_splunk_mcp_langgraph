"""
Factory for creating MCP tools from URL definitions.
"""
from typing import Dict, Any, Callable, Awaitable, Type, List, Optional
from pydantic import BaseModel, Field

from ..api.client import FirewallManagerApiClient
from ..core.models import (
    FilterableToolInput, 
    NonFilterableToolInput, 
    CacheClearInput, 
    CacheInfoInput,
    CacheConfigInput,
    RateLimitConfigInput,
    RateLimitInfoInput, 
    ListDevicesInput, 
    NetworkObject, 
    LogSettings, 
    DeployASADeviceChangesInput
    
)
from ..core.utils import sanitize_tool_name, generate_tool_docstring
from ..config.settings import logger, GLOBAL_RATE_LIMIT

class ToolFactory:
    """
    Factory class for creating MCP tool functions from URL definitions.
    """
    
    def __init__(self):
        """
        Initialize the ToolFactory.
        """
        self.api_client = FirewallManagerApiClient()
    
    def create_tool_function(
        self, 
        api_url_path: str, 
        input_model_type: Type[BaseModel], 
        method: str
    ) -> Callable[[BaseModel], Awaitable[Dict[str, Any]]]:
        """
        Create a tool function for the given API URL path and input model type.
        
        Args:
            api_url_path: The API endpoint path
            input_model_type: The Pydantic model class for the tool's input
            
        Returns:
            An async function that can be registered as an MCP tool
        """
        async def tool_function(
            params: input_model_type = Field(default_factory=input_model_type)  # type: ignore[valid-type]
        ) -> Dict[str, Any]:
            """
            The generated tool function that will be called when the MCP tool is invoked.
            
            Args:
                params: The parameters for the API call
                
            Returns:
                The API response as a dictionary, with all pages automatically combined if pagination is present
            """
            use_cache = None  # Use the FirewallManagerApiClient default
            request_params = {}
            
            
            # Access filter_expression if the model supports it
            if hasattr(params, 'filter_expression') and params.filter_expression is not None:  # type: ignore[attr-defined]
                request_params['filter'] = params.filter_expression  # type: ignore[attr-defined]
            
            # Access query_params
            if params and hasattr(params, 'query_params') and params.query_params is not None:  # type: ignore[attr-defined]
                # Make a copy to avoid modifying the original
                query_params = dict(params.query_params)  # type: ignore[attr-defined]
                
                # Extract special parameters                
                if 'use_cache' in query_params:
                    use_cache = query_params.pop('use_cache')
                
                # Add remaining parameters
                request_params.update(query_params)
            
            # Call the API and return the result
            
            if method == "GET":
                return await self.api_client.get(
                    api_url_path, 
                    params=request_params, 
                )
            elif method == "POST": 
                payload = params.dict(exclude={"query_params"})
                return await self.api_client.post(
                    api_url_path,
                    data=payload
                )
        
        return tool_function
    
    def create_cache_clear_function(self) -> Callable[[CacheClearInput], Awaitable[Dict[str, Any]]]:
        """
        Create a function for clearing the cache.
        
        Returns:
            An async function that can be registered as an MCP tool
        """
        async def cache_clear(
            params: CacheClearInput = Field(default_factory=CacheClearInput)
        ) -> Dict[str, Any]:
            """
            Clear the API response cache. This can be useful for ensuring that subsequent requests
            fetch fresh data from the Cisco SCC Firewall Management API.

            Args:
                params: Parameters for clearing the cache
                
            Returns:
                A dictionary with information about the operation
            """
            await self.api_client.clear_cache(namespace=params.namespace)
            return {
                "status": "success",
                "message": f"Cache{'for namespace: ' + params.namespace if params.namespace else ''} cleared successfully"
            }
        
        return cache_clear
    
    def create_cache_info_function(self) -> Callable[[CacheInfoInput], Awaitable[Dict[str, Any]]]:
        """
        Create a function for getting cache information.
        
        Returns:
            An async function that can be registered as an MCP tool
        """
        async def cache_info(
            params: CacheInfoInput = Field(default_factory=CacheInfoInput)
        ) -> Dict[str, Any]:
            """
            Get information about the current cache state.
            
            Returns:
                A dictionary with cache statistics
            """
            return await self.api_client.get_cache_info()
        
        return cache_info
    
    def create_cache_config_function(self) -> Callable[[CacheConfigInput], Awaitable[Dict[str, Any]]]:
        """
        Create a function for configuring cache settings.
        
        Returns:
            An async function that can be registered as an MCP tool
        """
        async def cache_config(
            params: CacheConfigInput = Field(default_factory=CacheConfigInput)
        ) -> Dict[str, Any]:
            """
            Configure cache settings for the Cisco Security Cloud Control API client.
            
            Args:
                params: Parameters for configuring the cache
                
            Returns:
                A dictionary with the updated cache configuration
            """
            # Update cache settings if provided
            if params.enabled is not None:
                self.api_client.cache_enabled = params.enabled
            
            if params.ttl is not None:
                self.api_client.cache_ttl = params.ttl
            
            # Return the current configuration
            return {
                "cache_enabled": self.api_client.cache_enabled,
                "cache_ttl": self.api_client.cache_ttl,
                "message": "Cache configuration updated successfully"
            }
        
        return cache_config
    
    def create_tool_from_url_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool from a URL entry in the configuration.
        
        Args:
            entry: A dictionary with URL entry data from the configuration
            
        Returns:
            A dictionary with tool information (name, function, supports_filtering)
            or None if the entry is invalid
        """
        tool_name = sanitize_tool_name(entry.get("Name", ""))
        api_url_path = entry.get("URL")
        http_request_type = entry.get("Method", "")
        filterable_fields = entry.get("FilterableFields", [])
        supports_filtering = bool(filterable_fields)
        
        if not tool_name or not api_url_path:
            logger.warning(f"⚠️ Skipping entry due to missing 'Name' or 'URL': {entry}")
            return None

        
        # Choose the appropriate input model based on filtering support
        input_model = ListDevicesInput if http_request_type=="GET" else DeployASADeviceChangesInput
        
        # Create the tool function
        tool_func = self.create_tool_function(api_url_path, input_model, http_request_type)
        
        # Set tool name and description
        tool_func.__name__ = tool_name
        tool_func.__doc__ = generate_tool_docstring(entry["Name"], api_url_path, http_request_type)
        
        return {
            "name": tool_name,
            "function": tool_func,
            "supports_filtering": supports_filtering,
            "filterable_fields": filterable_fields
        }
        
    def create_tools_from_url_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create tools from all URL entries in the configuration.
        
        Args:
            entries: A list of URL entry dictionaries from the configuration
            
        Returns:
            A list of dictionaries with tool information
        """
        tools = []
        for entry in entries:
            tool_info = self.create_tool_from_url_entry(entry)
            if tool_info:
                tools.append(tool_info)
        return tools

    def create_cache_management_tools(self) -> List[Dict[str, Any]]:
        """
        Create tools for cache management.
        
        Returns:
            A list of dictionaries with tool information
        """
        cache_tools = []
        
        # Create cache_clear tool
        cache_clear_func = self.create_cache_clear_function()
        cache_clear_func.__name__ = "cache_clear"
        cache_clear_func.__doc__ = "Clear the API response cache to ensure fresh data from Cisco SCC."
        cache_tools.append({
            "name": "cache_clear",
            "function": cache_clear_func,
            "supports_filtering": False,
            "filterable_fields": []
        })
        
        # Create cache_info tool
        cache_info_func = self.create_cache_info_function()
        cache_info_func.__name__ = "cache_info"
        cache_info_func.__doc__ = "Get information about the current cache state."
        cache_tools.append({
            "name": "cache_info",
            "function": cache_info_func,
            "supports_filtering": False,
            "filterable_fields": []
        })
        
        # Create cache_config tool
        cache_config_func = self.create_cache_config_function()
        cache_config_func.__name__ = "cache_config"
        cache_config_func.__doc__ = "Configure cache settings for the SCC API client."
        cache_tools.append({
            "name": "cache_config",
            "function": cache_config_func,
            "supports_filtering": False,
            "filterable_fields": []
        })
        
        return cache_tools