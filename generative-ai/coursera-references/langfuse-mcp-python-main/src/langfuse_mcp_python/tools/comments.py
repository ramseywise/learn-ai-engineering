"""
Comments Tool - Add, Update, Delete, and View Comments on Traces
Important for collaboration and annotation
"""

from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

GET_COMMENTS_TOOL_SPEC = Tool(
    name="get_comments",
    description="Retrieve comments for a trace or observation.",
    inputSchema={
        "type": "object",
        "properties": {
            "object_id": {"type": "string", "description": "Trace or observation ID"},
            "object_type": {"type": "string", "enum": ["TRACE", "OBSERVATION", "SESSION", "PROMPT"]},
        },
        "required": ["object_id"],
    },
)

ADD_COMMENT_TOOL_SPEC = Tool(
    name="add_comment",
    description="Add a comment to a trace or observation.",
    inputSchema={
        "type": "object",
        "properties": {
            "object_id": {"type": "string"},
            "object_type": {"type": "string", "enum": ["TRACE", "OBSERVATION", "SESSION", "PROMPT"], "default": "TRACE"},
            "content": {"type": "string"},
        },
        "required": ["object_id", "content"],
    },
)

class GetCommentsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            # Try get_many first, fallback to list if needed
            try:
                comments = await self._fetch_with_retry(
                    lambda: self.langfuse.api.comments.get(
                        object_id=args["object_id"],
                        object_type=args.get("object_type", "TRACE"),
                    )
                )
            except AttributeError:
                # Fallback to list if get_many doesn't exist
                comments = await self._fetch_with_retry(
                    lambda: self.langfuse.api.comments.get(
                        object_id=args["object_id"],
                        object_type=args.get("object_type", "TRACE"),
                    )
                )
            
            response = f"💬 **Comments** ({len(comments.data) if hasattr(comments, 'data') else len(comments)} found):\n\n"
            comment_list = comments.data if hasattr(comments, 'data') else comments
            
            for i, comment in enumerate(comment_list, 1):
                response += f"{i}. {comment.content}\n"
                if hasattr(comment, 'author_user_id') and comment.author_user_id:
                    response += f"   By: {comment.author_user_id}\n"
            return response
        except Exception as e:
            return f"Error fetching comments: {str(e)}"

class AddCommentTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            # Get project_id from langfuse client
            project_id = None
            if hasattr(self.langfuse.client, "_get_project_id"):
                project_id = self.langfuse.client._get_project_id()
            
            if not project_id:
                # Try to get from the first available project
                try:
                    projects = await self._fetch_with_retry(
                        lambda: self.langfuse.api.projects.get()
                    )
                    if projects and len(projects.data) > 0:
                        project_id = projects.data[0].id
                except:
                    pass
            
            if not project_id:
                return "Error: Unable to determine project_id. Please ensure your Langfuse credentials are valid."
            
            comment = await self._fetch_with_retry(
                lambda: self.langfuse.api.comments.create(
                    project_id=project_id,
                    object_id=args["object_id"],
                    object_type=args.get("object_type", "TRACE"),
                    content=args["content"],
                )
            )
            return f"✅ Comment added successfully\nID: {comment.id}"
        except Exception as e:
            return f"Error adding comment: {str(e)}"
