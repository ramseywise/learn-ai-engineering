"""
Score Configs Tool - Get Score Definitions
Important for understanding available scores
"""

from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

SCORE_CONFIGS_TOOL_SPEC = Tool(
    name="get_score_configs",
    description="Retrieve score configuration definitions. Includes available scores, their types, and descriptions. and score ids.",
    inputSchema={"type": "object", "properties": {}},
)

class GetScoreConfigsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            configs = await self._fetch_with_retry(
                self.langfuse.api.score_configs.get,
                page=1,
                limit=100,
            )
            response = f"[SETTINGS] **Score Configurations** ({len(configs.data)} found):\n\n"
            for config in configs.data:
                response += f"**{config.name}**\n"
                response += f"  - Type: {config.data_type}\n"
                if hasattr(config, 'description') and config.description:
                    response += f"  - Description: {config.description}\n"
                response += "\n"
            return response
        except Exception as e:
            return f"Error fetching score configs: {str(e)}"
