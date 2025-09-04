import os
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
from sse_starlette.sse import EventSourceResponse

load_dotenv()

app = FastAPI(title="Splunk MCP Server", version="1.0.0")

class BaselineResult(BaseModel):
    success: bool
    data: dict
    timestamp: str

class MCPConnection:
    """SSE connection to Splunk MCP Server"""
    
    def __init__(self):
        self.mcp_server_url = os.getenv("SPLUNK_MCP_BASE_URL", "http://localhost:8080")
        self.api_key = os.getenv("SPLUNK_MCP_BEARER_TOKEN")
    
    async def sse_stream(self, query: str):
        """Create SSE stream to MCP server"""
        headers = {"Accept": "text/event-stream"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.mcp_server_url}/mcp/stream",
                json={"query": query},
                headers=headers,
                timeout=30.0
            ) as response:
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': f'MCP server error: {response.status_code}'})}\n\n"
                    return
                
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        yield chunk

class DFBaselineTraffic:
    """df_baseline_traffic model with SSE streaming"""
    
    def __init__(self):
        self.model_name = "df_baseline_traffic"
        self.index = "test_summary_firewall" 
        self.mcp_conn = MCPConnection()
    
    def get_query(self) -> str:
        """Get hardcoded SPL query"""
        return f"""
        search index={self.index} earliest=-24h@h latest=now 
        | apply {self.model_name} 
        | head 20
        | table _time, *
        """.strip()
    
    async def run_stream(self):
        """Stream results via SSE"""
        query = self.get_query()
        async for chunk in self.mcp_conn.sse_stream(query):
            yield chunk
    
    async def run(self):
        """Run model and return raw query results"""
        query = self.get_query()
        results = []
        async for chunk in self.mcp_conn.sse_stream(query):
            if chunk.startswith("data:"):
                data_part = chunk[5:].strip()
                if data_part:
                    try:
                        results.append(json.loads(data_part))
                    except json.JSONDecodeError:
                        continue
        return results

class SSBaselineTraffic:
    """ss_baseline_traffic model with SSE streaming"""
    
    def __init__(self):
        self.model_name = "ss_baseline_traffic"
        self.index = "test_summary_firewall"
        self.mcp_conn = MCPConnection()
    
    def get_query(self) -> str:
        """Get hardcoded SPL query"""
        return f"""
        search index={self.index} earliest=-24h@h latest=now 
        | apply {self.model_name} 
        | head 20
        | table _time, *
        """.strip()
    
    async def run_stream(self):
        """Stream results via SSE"""
        query = self.get_query()
        async for chunk in self.mcp_conn.sse_stream(query):
            yield chunk
    
    async def run(self):
        """Run model and return raw query results"""
        query = self.get_query()
        results = []
        async for chunk in self.mcp_conn.sse_stream(query):
            if chunk.startswith("data:"):
                data_part = chunk[5:].strip()
                if data_part:
                    try:
                        results.append(json.loads(data_part))
                    except json.JSONDecodeError:
                        continue
        return results

# FastAPI endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/df-baseline-traffic")
async def get_df_baseline():
    """Get df_baseline_traffic results"""
    model = DFBaselineTraffic()
    result = await model.run()
    return result

@app.get("/df-baseline-traffic/stream")
async def stream_df_baseline():
    """Stream df_baseline_traffic results via SSE"""
    model = DFBaselineTraffic()
    return EventSourceResponse(model.run_stream())

@app.get("/ss-baseline-traffic")
async def get_ss_baseline():
    """Get ss_baseline_traffic results"""
    model = SSBaselineTraffic()
    result = await model.run()
    return result

@app.get("/ss-baseline-traffic/stream")
async def stream_ss_baseline():
    """Stream ss_baseline_traffic results via SSE"""
    model = SSBaselineTraffic()
    return EventSourceResponse(model.run_stream())

class SplunkMCP:
    """Simplified MCP client for backward compatibility"""
    
    def __init__(self):
        self.df_model = DFBaselineTraffic()
        self.ss_model = SSBaselineTraffic()
    
    async def search(self, query: str) -> dict:
        """Simple search method for agent compatibility"""
        if "df_baseline_traffic" in query.lower():
            return await self.df_model.run()
        elif "ss_baseline_traffic" in query.lower():
            return await self.ss_model.run()
        else:
            return {"error": "Unknown model requested"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)