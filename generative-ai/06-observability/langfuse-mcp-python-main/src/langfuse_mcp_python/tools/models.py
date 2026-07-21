"""
Models Tool - Get, Create, Update, and Delete Model Configurations and Pricing
Critical for accurate cost calculation
"""

from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

MODELS_TOOL_SPEC = Tool(
    name="get_models",
    description="Retrieve model configurations and pricing information.",
    inputSchema={
        "type": "object",
        "properties": {
            "model_id": {"type": "string"},
            "limit": {"type": "integer", "default": 50},
        },
    },
)

CREATE_MODEL_TOOL_SPEC = Tool(
    name="create_model",
    description="Create a custom model configuration with pricing.",
    inputSchema={
        "type": "object",
        "properties": {
            "model_name": {"type": "string", "description": "Model identifier"},
            "match_pattern": {"type": "string", "description": "Regex pattern to match model names"},
            "start_date": {"type": "string", "format": "date-time", "description": "When pricing starts"},
            "input_price": {"type": "number", "description": "Price per 1M input tokens (USD)"},
            "output_price": {"type": "number", "description": "Price per 1M output tokens (USD)"},
            "total_price": {"type": "number", "description": "Price per 1M total tokens (USD)"},
            "unit": {"type": "string", "enum": ["TOKENS", "CHARACTERS", "MILLISECONDS", "SECONDS", "IMAGES", "REQUESTS"]},
            "tokenizer_id": {"type": "string", "description": "Tokenizer to use"},
            "tokenizer_config": {"type": "object", "description": "Tokenizer configuration"},
        },
        "required": ["model_name", "match_pattern"],
    },
)

DELETE_MODEL_TOOL_SPEC = Tool(
    name="delete_model",
    description="Delete a custom model configuration.",
    inputSchema={
        "type": "object",
        "properties": {
            "model_id": {"type": "string", "description": "Model ID to delete"},
        },
        "required": ["model_id"],
    },
)

class GetModelsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            if args.get("model_id"):
                model = await self._fetch_with_retry(
                    self.langfuse.api.models.get,
                    id=args["model_id"],
                )
                return self._format_model(model)
            else:
                models = await self._fetch_with_retry(
                    self.langfuse.api.models.list,
                    page=1,
                    limit=args.get("limit", 50),
                )
                return self._format_models_list(models.data)
        except Exception as e:
            return f"Error fetching models: {str(e)}"
    
    def _format_model(self, model) -> str:
        response = f"[AGENT] **Model: {model.model_name}**\n\n"
        if hasattr(model, 'input_price'):
            response += f"  - Input Price: ${model.input_price}/1M tokens\n"
        if hasattr(model, 'output_price'):
            response += f"  - Output Price: ${model.output_price}/1M tokens\n"
        return response
    
    def _format_models_list(self, models) -> str:
        response = f"[AGENT] **Models** ({len(models)} found):\n\n"
        for model in models[:30]:
            response += f"  - {model.model_name}\n"
        return response

class CreateModelTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            model = await self._fetch_with_retry(
                self.langfuse.api.models.create,
                model_name=args["model_name"],
                match_pattern=args["match_pattern"],
                start_date=args.get("start_date"),
                input_price=args.get("input_price"),
                output_price=args.get("output_price"),
                total_price=args.get("total_price"),
                unit=args.get("unit", "TOKENS"),
                tokenizer_id=args.get("tokenizer_id"),
                tokenizer_config=args.get("tokenizer_config"),
            )
            return f"""[OK] Model created
Name: {model.model_name}
Input Price: ${model.input_price}/1M tokens
Output Price: ${model.output_price}/1M tokens
"""
        except Exception as e:
            return f"Error creating model: {str(e)}"

class DeleteModelTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            await self._fetch_with_retry(
                self.langfuse.api.models.delete,
                id=args["model_id"],
            )
            return f"[OK] Model deleted: {args['model_id']}"
        except Exception as e:
            return f"Error deleting model: {str(e)}"