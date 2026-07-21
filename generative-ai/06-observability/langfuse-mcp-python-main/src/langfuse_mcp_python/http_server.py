"""
HTTP/SSE Server Implementation for Langfuse MCP
Supports multiple transport modes:
- stdio (default)
- streamable-http (HTTP with SSE)
- sse (Server-Sent Events only)
"""

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import mcp.types as mcp_types
from mcp.shared.version import SUPPORTED_PROTOCOL_VERSIONS


class HTTPMCPServer:
    """
    HTTP/SSE transport for MCP server
    Provides Streamable HTTP endpoint compatible with all MCP clients
    """
    
    def __init__(
        self,
        mcp_server,
        tools: Dict[str, Any],
        host: str = "127.0.0.1",
        port: int = 8000,
        path: str = "/mcp",
        json_response: bool = False,
        stateless: bool = False,
    ):
        self.mcp_server = mcp_server
        self.tools = tools
        self.host = host
        self.port = port
        self.path = path
        self.json_response = json_response
        self.stateless = stateless
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Langfuse MCP Server",
            description="Production-ready MCP server with HTTP/SSE transport",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Session storage for stateful mode
        self.sessions = {} if not stateless else None
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register HTTP endpoints"""
        
        @self.app.get("/")
        async def root():
            """Server info endpoint"""
            return {
                "name": "Langfuse MCP Server",
                "version": "1.0.0",
                "transport": "http/sse",
                "tools_count": len(self.tools),
                "endpoint": self.path,
                "stateless": self.stateless,
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "tools": len(self.tools),
            }
        
        @self.app.get(self.path)
        async def mcp_sse(request: Request):
            """SSE endpoint for MCP communication"""
            return StreamingResponse(
                self._sse_stream(request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
        
        @self.app.post(self.path)
        async def mcp_post(request: Request):
            """HTTP POST endpoint for MCP requests"""
            try:
                body = await request.json()
                response = await self._handle_request(body, request)
                
                if self.json_response:
                    return JSONResponse(response)
                else:
                    return response
            
            except Exception as e:
                return JSONResponse(
                    {"error": str(e), "type": "internal_error"},
                    status_code=500
                )
        
        @self.app.get("/tools")
        async def list_tools():
            """List all available tools"""
            tool_list = []
            for name, tool_instance in self.tools.items():
                tool_list.append({
                    "name": name,
                    "type": tool_instance.__class__.__name__,
                })
            
            return {
                "tools": tool_list,
                "count": len(tool_list)
            }
        
        @self.app.post("/tools/{tool_name}")
        async def execute_tool(tool_name: str, request: Request):
            """Execute a specific tool directly"""
            try:
                body = await request.json()
                
                if tool_name not in self.tools:
                    return JSONResponse(
                        {"error": f"Tool not found: {tool_name}"},
                        status_code=404
                    )
                
                tool = self.tools[tool_name]
                result = await tool.execute(body)
                
                return {
                    "tool": tool_name,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            except Exception as e:
                return JSONResponse(
                    {"error": str(e)},
                    status_code=500
                )
    
    async def _sse_stream(self, request: Request):
        """SSE stream generator"""
        session_id = None
        
        if not self.stateless:
            # Create session
            session_id = f"session_{len(self.sessions)}"
            self.sessions[session_id] = {
                "created": datetime.utcnow(),
                "client": request.client.host,
            }
        
        try:
            # Send initial connection event
            yield self._format_sse_message("connected", {
                "server": "Langfuse MCP",
                "version": "1.0.0",
                "session_id": session_id,
                "tools_count": len(self.tools),
            })
            
            # Keep connection alive
            while True:
                # Send heartbeat every 30 seconds
                await asyncio.sleep(30)
                yield self._format_sse_message("heartbeat", {
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        except asyncio.CancelledError:
            # Client disconnected
            if session_id and self.sessions:
                del self.sessions[session_id]
            raise
    
    def _format_sse_message(self, event: str, data: Dict[str, Any]) -> str:
        """Format SSE message"""
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"
    
    async def _handle_request(self, body: Any, request: Request) -> Any:
        """Handle MCP request (JSON-RPC 2.0 or legacy)"""
        
        # Batch support
        if isinstance(body, list):
            responses = []
            for item in body:
                response = await self._handle_single_request(item, request)
                if response is not None:
                    responses.append(response)
            return responses
        
        return await self._handle_single_request(body, request)
    
    def _is_jsonrpc(self, body: Any) -> bool:
        """Detect JSON-RPC 2.0 requests"""
        return isinstance(body, dict) and body.get("jsonrpc") == "2.0"
    
    def _jsonrpc_result(self, request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }
    
    def _jsonrpc_error(self, request_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
        error_obj = {
            "code": code,
            "message": message,
        }
        if data is not None:
            error_obj["data"] = data
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error_obj,
        }
    
    async def _handle_single_request(self, body: Any, request: Request) -> Any:
        """Handle a single MCP request"""
        
        # JSON-RPC 2.0 (Streamable HTTP / SSE via MCP Inspector)
        if self._is_jsonrpc(body):
            request_id = body.get("id")
            method = body.get("method")
            params = body.get("params") or {}
            
            if not isinstance(method, str):
                return self._jsonrpc_error(request_id, -32600, "Invalid Request")
            
            if method == "tools/list":
                tool_specs = []
                for spec in self.mcp_server.tool_specs:
                    tool_specs.append({
                        "name": spec.name,
                        "description": spec.description,
                        "inputSchema": spec.inputSchema,
                    })
                
                return self._jsonrpc_result(request_id, {"tools": tool_specs})

            if method == "initialize":
                params = params or {}
                requested_version = params.get("protocolVersion")
                if requested_version in SUPPORTED_PROTOCOL_VERSIONS:
                    protocol_version = requested_version
                else:
                    protocol_version = mcp_types.LATEST_PROTOCOL_VERSION

                init_options = self.mcp_server.server.create_initialization_options()
                capabilities = init_options.capabilities.model_dump(exclude_none=True)

                server_info = {
                    "name": init_options.server_name,
                    "version": init_options.server_version,
                }
                if init_options.website_url is not None:
                    server_info["websiteUrl"] = init_options.website_url
                if init_options.icons is not None:
                    server_info["icons"] = init_options.icons

                result = {
                    "protocolVersion": protocol_version,
                    "capabilities": capabilities,
                    "serverInfo": server_info,
                }
                if init_options.instructions is not None:
                    result["instructions"] = init_options.instructions
                return self._jsonrpc_result(request_id, result)

            if method == "notifications/initialized":
                # No response required for notifications
                return None

            if method == "ping":
                return self._jsonrpc_result(request_id, {})
            
            if method == "tools/call":
                if not isinstance(params, dict):
                    return self._jsonrpc_error(request_id, -32602, "Invalid params")
                
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name not in self.tools:
                    return self._jsonrpc_result(
                        request_id,
                        {
                            "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                            "isError": True,
                        },
                    )
                
                try:
                    tool = self.tools[tool_name]
                    result = await tool.execute(arguments)
                    
                    return self._jsonrpc_result(
                        request_id,
                        {"content": [{"type": "text", "text": result}]},
                    )
                
                except Exception as e:
                    return self._jsonrpc_result(
                        request_id,
                        {"content": [{"type": "text", "text": str(e)}], "isError": True},
                    )
            
            return self._jsonrpc_error(request_id, -32601, f"Method not found: {method}")
        
        # Legacy (non-JSON-RPC) request format
        if not isinstance(body, dict):
            return {"error": "Invalid request body", "isError": True}
        
        method = body.get("method")
        params = body.get("params", {})
        
        if method == "tools/list":
            tool_specs = []
            for spec in self.mcp_server.tool_specs:
                tool_specs.append({
                    "name": spec.name,
                    "description": spec.description,
                    "inputSchema": spec.inputSchema,
                })
            
            return {"tools": tool_specs}
        
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in self.tools:
                return {"error": f"Unknown tool: {tool_name}", "isError": True}
            
            try:
                tool = self.tools[tool_name]
                result = await tool.execute(arguments)
                return {"content": [{"type": "text", "text": result}]}
            except Exception as e:
                return {"error": str(e), "isError": True}
        
        return {"error": f"Unknown method: {method}", "isError": True}
    
    def run(self, transport: str = "streamable-http"):
        """Run the HTTP server"""
        
        print(f"\n[WEB] Starting HTTP MCP Server")
        print(f"   Transport: {transport}")
        print(f"   Host: {self.host}")
        print(f"   Port: {self.port}")
        print(f"   Endpoint: {self.path}")
        print(f"   Stateless: {self.stateless}")
        print(f"   Tools: {len(self.tools)}")
        print(f"\n[WATCH] Server URL: http://{self.host}:{self.port}{self.path}")
        print(f"[LIST] Tools List: http://{self.host}:{self.port}/tools")
        print(f"[LOVE]  Health Check: http://{self.host}:{self.port}/health")
        print(f"\n[NOTE] Server is ready!\n")
        
        # Run uvicorn server
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
        )


def create_http_server(
    mcp_server,
    tools: Dict[str, Any],
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp",
    json_response: bool = False,
    stateless: bool = False,
) -> HTTPMCPServer:
    """
    Factory function to create HTTP MCP server
    
    Args:
        mcp_server: MCP server instance
        tools: Dictionary of tool instances
        host: Host to bind to
        port: Port to bind to
        path: HTTP path for MCP endpoint
        json_response: Force JSON-only responses
        stateless: Run in stateless mode (no sessions)
    
    Returns:
        HTTPMCPServer instance
    """
    return HTTPMCPServer(
        mcp_server=mcp_server,
        tools=tools,
        host=host,
        port=port,
        path=path,
        json_response=json_response,
        stateless=stateless,
    )
