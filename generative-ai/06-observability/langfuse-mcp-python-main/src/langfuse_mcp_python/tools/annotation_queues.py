"""
Annotation Queues - Complete CRUD operations
NEW: Important for human-in-the-loop workflows
"""

from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

GET_ANNOTATION_QUEUES_TOOL_SPEC = Tool(
    name="get_annotation_queues",
    description="List all annotation queues for human review.",
    inputSchema={"type": "object", "properties": {"limit": {"type": "integer", "default": 50}}},
)

CREATE_ANNOTATION_QUEUE_TOOL_SPEC = Tool(
    name="create_annotation_queue",
    description="Create a new annotation queue.",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Queue name"},
            "description": {"type": "string", "description": "Queue description"},
            "score_config_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Score configs to use"
            },
        },
        "required": ["name", "score_config_ids"],
    },
)

UPDATE_ANNOTATION_QUEUE_TOOL_SPEC = Tool(
    name="update_annotation_queue",
    description="Update annotation queue properties.",
    inputSchema={
        "type": "object",
        "properties": {
            "queue_id": {"type": "string"},
            "name": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": ["queue_id"],
    },
)

DELETE_ANNOTATION_QUEUE_TOOL_SPEC = Tool(
    name="delete_annotation_queue",
    description="Delete an annotation queue.",
    inputSchema={
        "type": "object",
        "properties": {"queue_id": {"type": "string"}},
        "required": ["queue_id"],
    },
)

GET_QUEUE_ITEMS_TOOL_SPEC = Tool(
    name="get_queue_items",
    description="Get items in an annotation queue.",
    inputSchema={
        "type": "object",
        "properties": {
            "queue_id": {"type": "string"},
            "status": {"type": "string", "enum": ["PENDING", "COMPLETED"]},
            "limit": {"type": "integer", "default": 50},
        },
        "required": ["queue_id"],
    },
)

RESOLVE_QUEUE_ITEM_TOOL_SPEC = Tool(
    name="resolve_queue_item",
    description="Mark an annotation queue item as resolved (status=COMPLETED).",
    inputSchema={
        "type": "object",
        "properties": {
            "queue_id": {"type": "string"},
            "item_id": {"type": "string"},
        },
        "required": ["queue_id", "item_id"],
    },
)

class GetAnnotationQueuesTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            queues = await self._fetch_with_retry(
                self.langfuse.api.annotation_queues.list_queues,
                limit=args.get("limit", 50),
            )
            response = f"[LIST] **Annotation Queues** ({len(queues.data)} found):\n\n"
            for queue in queues.data:
                response += f"**{queue.name}** (ID: {queue.id})\n"
                if queue.description:
                    response += f"  {queue.description}\n"
            return response
        except Exception as e:
            return f"Error fetching queues: {str(e)}"

class CreateAnnotationQueueTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            queue = await self._fetch_with_retry(
                self.langfuse.api.annotation_queues.create_queue,
                name=args["name"],
                description=args.get("description"),
                score_config_ids=args.get("score_config_ids", []),
            )
            return f"[OK] Annotation queue created\nName: {queue.name}\nID: {queue.id}"
        except Exception as e:
            return f"Error creating queue: {str(e)}"

class UpdateAnnotationQueueTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            queue = await self._fetch_with_retry(
                self.langfuse.api.annotation_queues.update_queue,
                queue_id=args["queue_id"],
                name=args.get("name"),
                description=args.get("description"),
            )
            return f"[OK] Queue updated: {queue.name}"
        except Exception as e:
            return f"Error updating queue: {str(e)}"

class DeleteAnnotationQueueTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            await self._fetch_with_retry(
                self.langfuse.api.annotation_queues.delete_queue,
                queue_id=args["queue_id"],
            )
            return f"[OK] Queue deleted: {args['queue_id']}"
        except Exception as e:
            return f"Error deleting queue: {str(e)}"

class GetQueueItemsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            items = await self._fetch_with_retry(
                self.langfuse.api.annotation_queues.list_queue_items,
                queue_id=args["queue_id"],
                status=args.get("status"),
                limit=args.get("limit", 50),
            )
            response = f"[NOTE] **Queue Items** ({len(items.data)} found):\n\n"
            for item in items.data:
                response += f"- {item.id} (Status: {item.status})\n"
            return response
        except Exception as e:
            return f"Error fetching items: {str(e)}"

class ResolveQueueItemTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            await self._fetch_with_retry(
                self.langfuse.api.annotation_queues.update_queue_item,
                queue_id=args["queue_id"],
                item_id=args["item_id"],
                status="COMPLETED",
            )
            return f"[OK] Queue item resolved: {args['item_id']}"
        except Exception as e:
            return f"Error resolving item: {str(e)}"
