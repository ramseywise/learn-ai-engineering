"""
Sessions Tool - FIXED to use correct Sessions API
Original version incorrectly used Traces API
"""

from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

SESSIONS_TOOL_SPEC = Tool(
    name="get_sessions",
    description=(
        "Retrieve multi-turn agent sessions. "
        "Track conversational agents and session-level metrics."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "session_id": {"type": "string"},
            "user_id": {"type": "string"},
            "from_timestamp": {"type": "string", "format": "date-time"},
            "to_timestamp": {"type": "string", "format": "date-time"},
            "limit": {"type": "integer", "default": 50},
        },
    },
)

class GetSessionsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            # If a specific session_id is provided, fetch directly
            if args.get("session_id"):
                session = await self._fetch_with_retry(
                    self.langfuse.api.sessions.get,
                    args["session_id"],
                )
                sessions = [session]
            else:
                from_ts = self._parse_datetime(args.get("from_timestamp"))
                to_ts = self._parse_datetime(args.get("to_timestamp"))

                # FIXED: Use correct Sessions API instead of Traces API
                sessions_response = await self._fetch_with_retry(
                    self.langfuse.api.sessions.list,
                    page=1,
                    limit=args.get("limit", 50),
                    from_timestamp=from_ts,
                    to_timestamp=to_ts,
                )
                sessions = sessions_response.data
            
            # Client-side filter for user_id (not supported server-side)
            if args.get("user_id"):
                sessions = [
                    s for s in sessions
                    if hasattr(s, "user_id") and s.user_id == args["user_id"]
                ]
            
            if not sessions:
                return "No sessions found."
            
            response = f"[RETRY] **Agent Sessions** ({len(sessions)} found):\n\n"
            
            for i, session in enumerate(sessions[:20], 1):
                response += f"{i}. **Session {session.id[:12]}...**\n"
                if hasattr(session, 'user_id') and session.user_id:
                    response += f"   - User: {session.user_id}\n"
                if hasattr(session, 'created_at'):
                    response += f"   - Created: {self._format_datetime(session.created_at)}\n"
                if hasattr(session, 'trace_count'):
                    response += f"   - Traces: {session.trace_count}\n"
                response += "\n"
            
            return response
        except Exception as e:
            return f"Error fetching sessions: {str(e)}"
