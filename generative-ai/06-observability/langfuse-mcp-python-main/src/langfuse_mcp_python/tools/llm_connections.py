"""
LLM Connections Tool - Manage LLM provider connections
"""

from typing import Any, Dict

from mcp.types import Tool
from langfuse.api.llm_connections.types.llm_adapter import LlmAdapter

from ..core.base_tool import BaseLangfuseTool

GET_LLM_CONNECTIONS_TOOL_SPEC = Tool(
    name="get_llm_connections",
    description="List all LLM connections for the project.",
    inputSchema={
        "type": "object",
        "properties": {
            "page": {"type": "integer", "default": 1},
            "limit": {"type": "integer", "default": 50},
        },
    },
)

UPSERT_LLM_CONNECTION_TOOL_SPEC = Tool(
    name="upsert_llm_connection",
    description="Create or update an LLM connection (upsert by provider).",
    inputSchema={
        "type": "object",
        "properties": {
            "provider": {"type": "string", "description": "Provider name (unique in project)"},
            "adapter": {
                "type": "string",
                "enum": [
                    "anthropic",
                    "openai",
                    "azure",
                    "bedrock",
                    "google-vertex-ai",
                    "google-ai-studio",
                ],
                "description": "Adapter type",
            },
            "secret_key": {"type": "string", "description": "Provider API key/secret"},
            "base_url": {"type": "string", "description": "Custom base URL"},
            "custom_models": {"type": "array", "items": {"type": "string"}},
            "with_default_models": {"type": "boolean"},
            "extra_headers": {"type": "object", "additionalProperties": {"type": "string"}},
            "config": {"type": "object", "description": "Adapter-specific config"},
        },
        "required": ["provider", "adapter", "secret_key"],
    },
)


class GetLlmConnectionsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            connections = await self._fetch_with_retry(
                self.langfuse.api.llm_connections.list,
                page=args.get("page", 1),
                limit=args.get("limit", 50),
            )
            items = connections.data if hasattr(connections, "data") else []
            response = f"[LIST] **LLM Connections** ({len(items)} found):\n\n"
            for item in items:
                response += f"- {item.id} provider={item.provider} adapter={item.adapter}\n"
            return response
        except Exception as e:
            return f"Error fetching LLM connections: {str(e)}"


class UpsertLlmConnectionTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            conn = await self._fetch_with_retry(
                self.langfuse.api.llm_connections.upsert,
                provider=args["provider"],
                adapter=LlmAdapter(args["adapter"]),
                secret_key=args["secret_key"],
                base_url=args.get("base_url"),
                custom_models=args.get("custom_models"),
                with_default_models=args.get("with_default_models"),
                extra_headers=args.get("extra_headers"),
                config=args.get("config"),
            )
            response = "[OK] LLM connection upserted\n"
            response += f"ID: {conn.id}\n"
            response += f"Provider: {conn.provider}\n"
            response += f"Adapter: {conn.adapter}\n"
            if hasattr(conn, "display_secret_key") and conn.display_secret_key:
                response += f"Display Key: {conn.display_secret_key}\n"
            return response
        except Exception as e:
            return f"Error upserting LLM connection: {str(e)}"
