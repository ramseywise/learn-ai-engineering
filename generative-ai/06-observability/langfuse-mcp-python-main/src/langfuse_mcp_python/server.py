"""
Production-Ready Langfuse MCP Server
Enhanced with comprehensive API coverage, retry logic, caching, and proper error handling

Features:
- 30+ tools covering all major Langfuse APIs
- Automatic retry with exponential backoff
- In-memory caching with TTL
- Structured logging
- Metrics collection
- Rate limiting
- Connection pooling
"""

import os
import asyncio
import argparse
from typing import Any, Dict
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

# Enhanced client and base
from .integrations.langfuse_client import EnhancedLangfuseClient
from .core.base_tool import InMemoryCache, MetricsCollector
from .utils.tool_registry import register_tools, setup_tools

# Load environment variables
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


class EnhancedLangfuseMonitoringServer:
    """
    Production-ready MCP Server for Langfuse monitoring
    
    Enhancements over original:
    - Comprehensive API coverage (20+ tools vs 6)
    - Retry logic with exponential backoff
    - Caching with TTL
    - Proper error handling
    - Metrics collection
    - Rate limiting
    - Structured logging
    """
    
    def __init__(self, enable_rate_limiting: bool = True):
        self.server = Server("langfuse-monitoring-enhanced")
        self.langfuse = None
        self.cache = InMemoryCache(default_ttl=300)  # 5-minute cache
        self.metrics = MetricsCollector()
        
        self._setup_langfuse(enable_rate_limiting)
        self.tools = setup_tools(self.langfuse, self.cache, self.metrics)
        self.tool_specs = register_tools(self.server, self.tools)
    
    def _setup_langfuse(self, enable_rate_limiting: bool):
        """Initialize enhanced Langfuse client"""
        try:
            self.langfuse = EnhancedLangfuseClient(
                enable_rate_limiting=enable_rate_limiting,
            )
            print("[OK] Langfuse client initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Langfuse client: {e}")
            raise
    
    async def run(self):
        """Run the MCP server with stdio transport"""
        print("[START] Starting Langfuse Monitoring MCP Server...")
        print(f"[METRICS] API Coverage: {len(self.tool_specs)} tools")
        print("[NOTE] Ready to accept requests\n")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "tools_count": len(self.tools),
            "cache_stats": {
                "size": len(self.cache.cache),
            },
            "metrics": self.metrics.get_stats(),
        }
    
    def close(self):
        """Cleanup resources"""
        if self.langfuse:
            self.langfuse.close()
        print("[OK] Server shutdown complete")


def main():
    """Entry point for the enhanced MCP server"""
    
    parser = argparse.ArgumentParser(
        description="Enhanced Langfuse Monitoring MCP Server"
    )
    
    # Transport options
    parser.add_argument(
        "--transport",
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        choices=["stdio", "streamable-http", "http", "sse"],
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", "127.0.0.1"),
        help="Host for HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8000")),
        help="Port for HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--path",
        default=os.getenv("MCP_PATH", "/mcp"),
        help="HTTP path for MCP endpoint (default: /mcp)",
    )
    
    # Server options
    parser.add_argument(
        "--no-rate-limit",
        action="store_true",
        help="Disable rate limiting (not recommended for production)",
    )
    parser.add_argument(
        "--json-response",
        action="store_true",
        default=os.getenv("MCP_JSON_RESPONSE", "").lower() in ("1", "true", "yes"),
        help="Force JSON-only responses for HTTP",
    )
    parser.add_argument(
        "--stateless",
        action="store_true",
        default=os.getenv("MCP_STATELESS", "").lower() in ("1", "true", "yes"),
        help="Run HTTP server in stateless mode (no sessions)",
    )
    
    # Info options
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print server statistics and exit",
    )
    
    args = parser.parse_args()
    
    try:
        # Create server instance
        server = EnhancedLangfuseMonitoringServer(
            enable_rate_limiting=not args.no_rate_limit,
        )
        
        # If stats mode, print stats and exit
        if args.stats:
            print("\n[METRICS] Server Statistics:")
            import json
            print(json.dumps(server.get_stats(), indent=2))
            return
        
        # Normalize transport
        transport = args.transport
        if transport == "http":
            transport = "streamable-http"
        
        # Run server with selected transport
        if transport == "stdio":
            # Standard stdio transport
            print("[START] Starting MCP Server (stdio transport)...")
            asyncio.run(server.run())
        
        elif transport in ("streamable-http", "sse"):
            # HTTP/SSE transport
            from .http_server import create_http_server
            
            http_server = create_http_server(
                mcp_server=server,
                tools=server.tools,
                host=args.host,
                port=args.port,
                path=args.path,
                json_response=args.json_response,
                stateless=args.stateless,
            )
            
            http_server.run(transport=transport)
        
        else:
            raise ValueError(f"Unsupported transport: {transport}")
    
    except KeyboardInterrupt:
        print("\n\n[WARN]  Server interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Server error: {e}")
        raise
    finally:
        if 'server' in locals():
            server.close()


if __name__ == "__main__":
    main()
