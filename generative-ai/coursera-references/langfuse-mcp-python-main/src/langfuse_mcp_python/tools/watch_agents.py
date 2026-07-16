"""
Enhanced Watch Agents Tool
FIXED: Server-side filtering, proper metrics, retry logic
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

WATCH_AGENTS_TOOL_SPEC = Tool(
    name="watch_agents",
    description="Monitor active agents in real-time with performance metrics.",
    inputSchema={
        "type": "object",
        "properties": {
            "session_ids": {
                "type": "array",
                "items": {"type": "string"},
            },
            "agent_names": {
                "type": "array",
                "items": {"type": "string"},
            },
            "time_window": {
                "type": "string",
                "enum": ["last_1h", "last_24h", "last_7d"],
                "default": "last_1h",
            },
            "summary_only": {
                "type": "boolean",
                "default": False,
                "description": "Return only aggregated cost summary (no per-trace details).",
            },
            "include_summary": {
                "type": "boolean",
                "default": False,
                "description": "Include aggregated cost summary along with per-trace details.",
            },
            "user_id": {"type": "string"},
            "tags": {
                "type": "array",
                "items": {"type": "string"},
            },
            "limit": {"type": "integer", "default": 10},
            "include_tokens": {
                "type": "boolean",
                "default": False,
                "description": "Include token counts in per-trace details.",
            },
        },
    },
)

class WatchAgentsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            time_window = args.get("time_window", "last_1h")
            hours_map = {"last_1h": 1, "last_24h": 24, "last_7d": 168}
            hours = hours_map.get(time_window, 1)
            
            # Calculate time range
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            summary_only = bool(args.get("summary_only"))
            include_summary = bool(args.get("include_summary")) or summary_only
            include_tokens = bool(args.get("include_tokens"))
            
            # FIXED: Use server-side filtering instead of client-side
            fetch_args = {
                "from_timestamp": start_time,
                "to_timestamp": end_time,
            }
            
            if not summary_only:
                fetch_args["limit"] = args.get("limit", 10)
            
            if args.get("user_id"):
                fetch_args["user_id"] = args["user_id"]
            
            if args.get("tags"):
                fetch_args["tags"] = args["tags"]
            
            # Fetch traces with server-side filtering
            if include_summary:
                traces = await self._fetch_all_paginated(
                    self.langfuse.api.trace.list,
                    **fetch_args
                )
            else:
                traces_response = await self._fetch_with_retry(
                    self.langfuse.api.trace.list,
                    **fetch_args
                )
                traces = traces_response.data
            
            # Client-side filter for session_ids and agent_names (not supported server-side)
            
            if args.get("session_ids"):
                traces = [t for t in traces if t.session_id in args["session_ids"]]
            
            if args.get("agent_names"):
                agent_names = set(args["agent_names"])
                traces = [
                    t for t in traces
                    if t.metadata and t.metadata.get("agent_name") in agent_names
                ]
            
            if not traces:
                return f"No active agents found in {time_window}"
            
            response = f"[SEARCH] **Active Agent Monitoring** ({time_window})\n\n"
            total_cost = self._sum_trace_costs(traces)
            response += f"**Total Cost (sum of traces)**: {self._format_cost(total_cost)}\n\n"
            
            if include_summary:
                summary = self._build_cost_summary(traces)
                response += summary + "\n"
            
            if summary_only:
                return response.rstrip() + "\n"
            
            response += f"**Total Traces**: {len(traces)}\n"
            response += f"**Showing**: Top {min(len(traces), args.get('limit', 10))}\n\n"
            
            for i, trace in enumerate(traces[:args.get("limit", 10)], 1):
                # FIXED: Use proper metrics calculation
                metrics = self._calculate_trace_metrics(trace)
                metadata = trace.metadata if hasattr(trace, "metadata") and trace.metadata else {}
                agent_name = "unknown"
                if isinstance(metadata, dict):
                    agent_name = metadata.get("agent_name") or metadata.get("agentName") or agent_name
                
                response += f"{i}. **{agent_name}** "
                response += f"(Trace: {trace.id[:12]}...)\n"
                response += f"   - Status: {self._get_trace_status(trace)}\n"
                response += f"   - Started: {self._format_datetime(trace.timestamp)}\n"
                response += f"   - Duration: {self._format_duration(metrics['latency_ms'])}\n"
                response += f"   - Cost: {self._format_cost(metrics['cost'])}\n"
                
                if include_tokens:
                    response += f"   - Tokens: {self._format_tokens(metrics['tokens'])}\n"
                
                if trace.session_id:
                    response += f"   - Session: {trace.session_id[:12]}...\n"
                
                response += "\n"
            
            return response
        except Exception as e:
            self.logger.error("Error watching agents", error=str(e))
            return f"Error watching agents: {str(e)}"

    def _build_cost_summary(self, traces: list[Any]) -> str:
        total_cost = self._sum_trace_costs(traces)
        cost_by_user: Dict[str, float] = {}
        cost_by_agent: Dict[str, float] = {}
        cost_by_trace_name: Dict[str, float] = {}
        
        for trace in traces:
            metrics = self._calculate_trace_metrics(trace)
            cost = metrics.get("cost", 0.0) or 0.0
            
            user_id = getattr(trace, "user_id", None) or getattr(trace, "userId", None)
            if user_id:
                cost_by_user[user_id] = cost_by_user.get(user_id, 0.0) + cost
            
            metadata = trace.metadata if hasattr(trace, "metadata") and trace.metadata else {}
            agent_name = "unknown"
            if isinstance(metadata, dict):
                agent_name = metadata.get("agent_name") or metadata.get("agentName") or agent_name
            if agent_name:
                cost_by_agent[agent_name] = cost_by_agent.get(agent_name, 0.0) + cost
            
            trace_name = getattr(trace, "name", None)
            if trace_name:
                cost_by_trace_name[trace_name] = cost_by_trace_name.get(trace_name, 0.0) + cost
        
        response = "**Cost Summary**\n"
        response += f"- Total Cost: {self._format_cost(total_cost)}\n"
        
        if cost_by_user:
            top_users = sorted(cost_by_user.items(), key=lambda x: x[1], reverse=True)[:5]
            response += "- Top Users by Cost:\n"
            for user_id, cost in top_users:
                response += f"  {user_id}: {self._format_cost(cost)}\n"
        
        if cost_by_agent:
            top_agent = max(cost_by_agent.items(), key=lambda x: x[1])
            response += f"- Highest Cost Agent: {top_agent[0]} ({self._format_cost(top_agent[1])})\n"
        
        if cost_by_trace_name:
            top_trace = max(cost_by_trace_name.items(), key=lambda x: x[1])
            response += f"- Highest Cost Trace Name: {top_trace[0]} ({self._format_cost(top_trace[1])})\n"
        
        return response

    def _sum_trace_costs(self, traces: list[Any]) -> float:
        total_cost = 0.0
        for trace in traces:
            metrics = self._calculate_trace_metrics(trace)
            total_cost += metrics.get("cost", 0.0) or 0.0
        return total_cost
