import os
import asyncio
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

class SplunkMCPClient:
    """Simple Splunk MCP Client"""
    
    def __init__(self):
        self.mcp_server_url = os.getenv("SPLUNK_MCP_BASE_URL", "https://secstrat-siem.api.scs.splunk.com/secstrat-siem/mcp/v1/")
        self.api_key = os.getenv("SPLUNK_MCP_BEARER_TOKEN", "eyJraWQiOiJzcGx1bmsuc2VjcmV0IiwiYWxnIjoiSFM1MTIiLCJ2ZXIiOiJ2MiIsInR0eXAiOiJzdGF0aWMifQ.eyJpc3MiOiJqYWNvc3RhQHNwbHVuay5jb20gZnJvbSBzaC1pLTA5NmE2NjE0ZGY4ZDJjYzk0Iiwic3ViIjoiamFjb3N0YUBzcGx1bmsuY29tIiwiYXVkIjoibWNwIiwiaWRwIjoiU3BsdW5rIiwianRpIjoiN2JkZWViYjQ1NjM4MTNhZWQ2ZjM2MDM2YzUxMWMzOTY5YWQ4ZTdjMWNmNTA4ZjI2ZjQ5ZTJkM2Y1YjBlMjk3ZCIsImlhdCI6MTc1Njk0MzYxMywiZXhwIjoxNzg4NDc5NjEzLCJuYnIiOjE3NTY5NDM2MTN9.BrwWDioRswQV3wnVSUX0rJNKjQ9y7d2QI4Czvy5eFcEAvxh-TLvosVYfxy3UR6vhazdQhhU4EHB4ONCdPMHKCQ")
    
    async def _call_tool(self, tool_name: str, arguments: dict = None):
        """Generic method to call any MCP tool"""
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.mcp_server_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                return response.status_code, response.text
                
        except Exception as e:
            return None, str(e)
    
    async def get_indexes(self, row_limit: int = 100):
        """Get a list of indexes from Splunk"""
        print(f"Getting Splunk indexes (limit: {row_limit})...")
        
        status_code, response_text = await self._call_tool("get_indexes", {"row_limit": row_limit})
        
        if status_code == 200:
            print("✓ Successfully retrieved indexes")
            return response_text
        else:
            print(f"✗ Failed to get indexes: {status_code}")
            return response_text
    
    async def get_splunk_info(self):
        """Get comprehensive information about the Splunk instance"""
        print("Getting Splunk instance information...")
        
        status_code, response_text = await self._call_tool("get_splunk_info", {})
        
        if status_code == 200:
            print("✓ Successfully retrieved Splunk info")
            return response_text
        else:
            print(f"✗ Failed to get Splunk info: {status_code}")
            return response_text
    
    async def run_splunk_query(self, query: str, earliest_time: str = "-24h", latest_time: str = "now", row_limit: int = 100):
        """Execute a Splunk search query and return the results"""
        print(f"Running Splunk query: {query[:100]}...")
        
        arguments = {
            "query": query,
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "row_limit": row_limit
        }
        
        status_code, response_text = await self._call_tool("run_splunk_query", arguments)
        
        if status_code == 200:
            print("✓ Successfully executed Splunk query")
            return response_text
        else:
            print(f"✗ Failed to execute query: {status_code}")
            return response_text
    
    async def get_knowledge_objects(self, obj_type: str, row_limit: int = 100):
        """Get knowledge objects from Splunk (saved_searches, lookups, data_models, etc.)"""
        valid_types = ["saved_searches", "lookups", "automatic_lookups", "data_models", "mltk_models", "ml_algorithms"]
        
        if obj_type not in valid_types:
            print(f"✗ Invalid type. Must be one of: {valid_types}")
            return f"Error: Invalid type. Must be one of: {valid_types}"
        
        print(f"Getting knowledge objects: {obj_type} (limit: {row_limit})...")
        
        arguments = {
            "type": obj_type,
            "row_limit": row_limit
        }
        
        status_code, response_text = await self._call_tool("get_knowledge_objects", arguments)
        
        if status_code == 200:
            print("✓ Successfully retrieved knowledge objects")
            return response_text
        else:
            print(f"✗ Failed to get knowledge objects: {status_code}")
            return response_text
    
    async def get_metadata(self, metadata_type: str, index: str = "*", earliest_time: str = "-24h", latest_time: str = "now", row_limit: int = 100):
        """Get metadata information from Splunk (hosts, sources, sourcetypes)"""
        print(f"Getting metadata: {metadata_type} from index {index}...")
        
        arguments = {
            "type": metadata_type,
            "index": index,
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "row_limit": row_limit
        }
        
        status_code, response_text = await self._call_tool("get_metadata", arguments)
        
        if status_code == 200:
            print("✓ Successfully retrieved metadata")
            return response_text
        else:
            print(f"✗ Failed to get metadata: {status_code}")
            return response_text
    
    async def test_tools_list(self):
        """Test connection with tools/list JSON-RPC request"""
        print(f"Testing Splunk MCP Server: {self.mcp_server_url}")
        
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.mcp_server_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                return response.status_code, response.text
                
        except Exception as e:
            return None, str(e)

async def main():
    """Test the MCP connection and tools"""
    client = SplunkMCPClient()
    
    # Test basic connection
    print("=== Testing Connection ===")
    status_code, response_text = await client.test_tools_list()
    
    if status_code == 200:
        print("✓ Connection successful!")
        
        # Test get_indexes function
        print("\n=== Testing get_indexes Tool ===")
        indexes_result = await client.get_indexes(row_limit=5)
        print(f"Indexes result: {indexes_result[:200]}...")
        
        # Test get_splunk_info function
        print("\n=== Testing get_splunk_info Tool ===")
        info_result = await client.get_splunk_info()
        print(f"Splunk info result: {info_result[:300]}...")
        
        # Test run_splunk_query function
        print("\n=== Testing run_splunk_query Tool ===")
        query_result = await client.run_splunk_query("| stats count", row_limit=5)
        print(f"Query result: {query_result[:400]}...")
        
        # Test get_knowledge_objects function with different types
        print("\n=== Testing get_knowledge_objects Tool ===")
        
        # Test saved_searches
        print("\n--- Testing saved_searches ---")
        saved_searches_result = await client.get_knowledge_objects("saved_searches", row_limit=3)
        print(f"Saved searches: {saved_searches_result[:250]}...")
        
        # Test lookups
        print("\n--- Testing lookups ---")
        lookups_result = await client.get_knowledge_objects("lookups", row_limit=3)
        print(f"Lookups: {lookups_result[:250]}...")
        
        # Test data_models
        print("\n--- Testing data_models ---")
        data_models_result = await client.get_knowledge_objects("data_models", row_limit=3)
        print(f"Data models: {data_models_result[:250]}...")
        
        # Test mltk_models
        print("\n--- Testing mltk_models ---")
        mltk_result = await client.get_knowledge_objects("mltk_models", row_limit=3)
        print(f"MLTK models: {mltk_result[:250]}...")
        
    else:
        print(f"✗ Connection failed: HTTP {status_code}")

if __name__ == "__main__":
    asyncio.run(main())