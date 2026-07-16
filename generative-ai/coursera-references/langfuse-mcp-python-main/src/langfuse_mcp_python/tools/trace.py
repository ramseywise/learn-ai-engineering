"""
Enhanced Get, Update, Delete Trace Tool
FIXED: Proper metrics, better error handling, cache support
"""

from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

GET_TRACE_TOOL_SPEC = Tool(
    name="get_trace",
    description="Retrieve detailed execution trace with all observations and metrics.",
    inputSchema={
        "type": "object",
        "properties": {
            "trace_id": {
                "type": "string",
                "description": "Trace ID to retrieve",
            },
            "include_observations": {
                "type": "boolean",
                "default": True,
            },
            "depth": {
                "type": "string",
                "enum": ["minimal", "summary", "full"],
                "default": "full",
            },
        },
        "required": ["trace_id"],
    },
)

UPDATE_TRACE_TOOL_SPEC = Tool(
    name="update_trace",
    description="Update trace metadata, tags, or other properties.",
    inputSchema={
        "type": "object",
        "properties": {
            "trace_id": {"type": "string", "description": "Trace ID to update"},
            "name": {"type": "string", "description": "Update trace name"},
            "user_id": {"type": "string", "description": "Update user ID"},
            "session_id": {"type": "string", "description": "Update session ID"},
            "metadata": {"type": "object", "description": "Update metadata (merges with existing)"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Update tags"},
            "public": {"type": "boolean", "description": "Make trace public/private"},
            "release": {"type": "string", "description": "Release/version identifier"},
        },
        "required": ["trace_id"],
    },
)

DELETE_TRACE_TOOL_SPEC = Tool(
    name="delete_trace",
    description="Delete a trace and all its associated observations.",
    inputSchema={
        "type": "object",
        "properties": {
            "trace_id": {"type": "string", "description": "Trace ID to delete"},
        },
        "required": ["trace_id"],
    },
)

class GetTraceTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            trace_id = args["trace_id"]
            depth = args.get("depth", "full")
            
            # Try cache first for full traces
            cache_key = self.cache.make_key("trace", trace_id, depth)
            
            def fetch_trace():
                return self.langfuse.api.trace.get(trace_id)
            
            # Use cache for frequently accessed traces
            if depth == "minimal":
                trace = await self._fetch_with_retry(fetch_trace)
            else:
                trace = self._get_cached_or_fetch(cache_key, fetch_trace, ttl=60)
            
            if not trace:
                return f"Trace not found: {trace_id}"
            
            response = f"[SEARCH] **Trace Details**\n\n"
            response += f"**ID**: {trace.id}\n"
            response += f"**Agent**: {trace.metadata.get('agent_name', 'unknown')}\n"
            response += f"**Session**: {trace.session_id or 'N/A'}\n"
            response += f"**User**: {trace.user_id or 'N/A'}\n"
            response += f"**Started**: {self._format_datetime(trace.timestamp)}\n"
            response += f"**Status**: {self._get_trace_status(trace)}\n\n"
            
            if depth in ["summary", "full"]:
                # FIXED: Use proper metrics calculation
                metrics = self._calculate_trace_metrics(trace)
                
                response += f"**Performance Metrics**:\n"
                response += f"  - Duration: {self._format_duration(metrics['latency_ms'])}\n"
                response += f"  - Tokens: {self._format_tokens(metrics['tokens'])}\n"
                response += f"  - Cost: {self._format_cost(metrics['cost'])}\n"
                response += f"  - Observations: {metrics['observation_count']}\n\n"
            
            if depth == "full" and args.get("include_observations", True):
                observations = await self._fetch_with_retry(
                    self.langfuse.api.observations.get_many,
                    trace_id=trace_id,
                )
                
                response += f"**Execution Steps** ({len(observations.data)} observations):\n\n"
                
                for i, obs in enumerate(observations.data[:20], 1):
                    obs_metrics = self._calculate_observation_metrics(obs)
                    
                    response += f"{i}. **{obs.name}** ({obs.type})\n"
                    response += f"   - Duration: {self._format_duration(obs_metrics['latency_ms'])}\n"
                    
                    if obs.type == "GENERATION" and hasattr(obs, 'model'):
                        response += f"   - Model: {obs.model}\n"
                        response += f"   - Tokens: {self._format_tokens(obs_metrics['tokens'])}\n"
                    
                    response += "\n"
            
            return response
        except Exception as e:
            self.logger.error("Error fetching trace", trace_id=trace_id, error=str(e))
            return f"Error fetching trace: {str(e)}"
        
class UpdateTraceTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            trace_id = args.pop("trace_id")
            
            # Build update payload
            update_data = {}
            if args.get("name"):
                update_data["name"] = args["name"]
            if args.get("user_id"):
                update_data["user_id"] = args["user_id"]
            if args.get("session_id"):
                update_data["session_id"] = args["session_id"]
            if args.get("metadata"):
                update_data["metadata"] = args["metadata"]
            if args.get("tags"):
                update_data["tags"] = args["tags"]
            if "public" in args:
                update_data["public"] = args["public"]
            if args.get("release"):
                update_data["release"] = args["release"]
            
            # Update trace
            trace = await self._fetch_with_retry(
                self.langfuse.api.trace.update,
                trace_id=trace_id,
                **update_data
            )
            
            # Invalidate cache for this trace
            cache_key = self.cache.make_key("trace", trace_id)
            self.cache.invalidate(cache_key)
            
            return f"[OK] Trace updated successfully\nID: {trace.id}\nName: {trace.name}"
        except Exception as e:
            return f"Error updating trace: {str(e)}"

class DeleteTraceTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            trace_id = args["trace_id"]
            
            # Delete trace
            result = await self._fetch_with_retry(
                self.langfuse.api.trace.delete,
                trace_id=trace_id
            )
            
            # Invalidate cache
            self.cache.invalidate("trace")
            
            return f"[OK] Trace deleted successfully\nID: {trace_id}"
        except Exception as e:
            return f"Error deleting trace: {str(e)}"
