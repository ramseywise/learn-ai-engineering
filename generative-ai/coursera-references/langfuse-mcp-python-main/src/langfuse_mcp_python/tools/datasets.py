"""
Datasets Tool - Manage Datasets and Experiments
Critical for evaluation and experimentation
"""

from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

DATASETS_TOOL_SPEC = Tool(
    name="get_datasets",
    description="Retrieve datasets and dataset items for experiments and evaluations.",
    inputSchema={
        "type": "object",
        "properties": {
            "dataset_name": {"type": "string"},
            "include_items": {"type": "boolean", "default": False},
            "include_runs": {"type": "boolean", "default": False},
        },
    },
)

CREATE_DATASET_TOOL_SPEC = Tool(
    name="create_dataset",
    description="Create a new dataset for experiments and evaluations.",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Dataset name"},
            "description": {"type": "string", "description": "Dataset description"},
            "metadata": {"type": "object", "description": "Additional metadata"},
        },
        "required": ["name"],
    },
)

UPDATE_DATASET_TOOL_SPEC = Tool(
    name="update_dataset",
    description="Update dataset properties.",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Dataset name"},
            "description": {"type": "string", "description": "New description"},
            "metadata": {"type": "object", "description": "Updated metadata"},
        },
        "required": ["name"],
    },
)

DELETE_DATASET_TOOL_SPEC = Tool(
    name="delete_dataset",
    description="Delete a dataset and all its items.",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Dataset name to delete"},
        },
        "required": ["name"],
    },
)

CREATE_DATASET_ITEM_TOOL_SPEC = Tool(
    name="create_dataset_item",
    description="Add an item to a dataset.",
    inputSchema={
        "type": "object",
        "properties": {
            "dataset_name": {"type": "string", "description": "Dataset name"},
            "input": {"description": "Input data for this item"},
            "expected_output": {"description": "Expected output for evaluation"},
            "metadata": {"type": "object", "description": "Item metadata"},
        },
        "required": ["dataset_name", "input"],
    },
)

class GetDatasetsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            if args.get("dataset_name"):
                dataset = await self._fetch_with_retry(
                    self.langfuse.api.datasets.get,
                    dataset_name=args["dataset_name"],
                )
                response = f"[METRICS] **Dataset: {dataset.name}**\n\n"
                
                if args.get("include_items"):
                    items = await self._fetch_with_retry(
                        self.langfuse.api.dataset_items.list,
                        dataset_name=args["dataset_name"],
                    )
                    response += f"**Items:** {len(items.data)}\n"
                
            if args.get("include_runs"):
                runs = await self._fetch_with_retry(
                    self.langfuse.api.datasets.get_runs,
                    dataset_name=args["dataset_name"],
                )
                response += f"**Runs:** {len(runs.data)}\n"
                
                return response
            else:
                datasets = await self._fetch_with_retry(
                    self.langfuse.api.datasets.list,
                    page=1,
                    limit=50,
                )
                response = f"[METRICS] **Datasets** ({len(datasets.data)} found):\n\n"
                for i, ds in enumerate(datasets.data, 1):
                    response += f"{i}. {ds.name}\n"
                return response
        except Exception as e:
            return f"Error fetching datasets: {str(e)}"
        
class CreateDatasetTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            dataset = await self._fetch_with_retry(
                self.langfuse.api.datasets.create,
                name=args["name"],
                description=args.get("description"),
                metadata=args.get("metadata"),
            )
            return f"[OK] Dataset created: {dataset.name}"
        except Exception as e:
            return f"Error creating dataset: {str(e)}"

class UpdateDatasetTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            dataset = await self._fetch_with_retry(
                self.langfuse.api.datasets.update,
                name=args["name"],
                description=args.get("description"),
                metadata=args.get("metadata"),
            )
            return f"[OK] Dataset updated: {dataset.name}"
        except Exception as e:
            return f"Error updating dataset: {str(e)}"

class DeleteDatasetTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            await self._fetch_with_retry(
                self.langfuse.api.datasets.delete,
                name=args["name"],
            )
            return f"[OK] Dataset deleted: {args['name']}"
        except Exception as e:
            return f"Error deleting dataset: {str(e)}"

class CreateDatasetItemTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            item = await self._fetch_with_retry(
                self.langfuse.api.dataset_items.create,
                dataset_name=args["dataset_name"],
                input=args["input"],
                expected_output=args.get("expected_output"),
                metadata=args.get("metadata"),
            )
            return f"[OK] Dataset item created\nDataset: {args['dataset_name']}\nItem ID: {item.id}"
        except Exception as e:
            return f"Error creating dataset item: {str(e)}"