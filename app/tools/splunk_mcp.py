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
    
    async def test_tools_list(self):
        """Test connection with tools/list JSON-RPC request"""
        print(f"Testing Splunk MCP Server: {self.mcp_server_url}")
        print(f"Using API key: {'Yes' if self.api_key else 'No'}")
        
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
        
        print(f"Payload: {json.dumps(payload)}")
        print(f"Headers: {headers}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.mcp_server_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Response body: {response.text}")
                
                return response.status_code, response.text
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return None, str(e)

async def main():
    """Test the MCP connection"""
    client = SplunkMCPClient()
    status_code, response_text = await client.test_tools_list()
    
    if status_code:
        print(f"\nResult: HTTP {status_code}")
        if status_code == 200:
            print("✓ Connection successful!")
        else:
            print("✗ Connection failed")
    else:
        print("✗ Request failed")

if __name__ == "__main__":
    asyncio.run(main())