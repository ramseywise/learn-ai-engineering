"""
Projects Tools - Create, Update, Delete, and Get Projects
"""

from typing import Any, Dict
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool

GET_PROJECTS_TOOL_SPEC = Tool(
    name="get_projects",
    description="Get project(s) associated with the API key.",
    inputSchema={"type": "object", "properties": {}},
)

CREATE_PROJECT_TOOL_SPEC = Tool(
    name="create_project",
    description="Create a new project (requires organization-scoped API key).",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "retention": {"type": "integer", "description": "Days to retain data (0 or >= 3)"},
            "metadata": {"type": "object"},
        },
        "required": ["name"],
    },
)

UPDATE_PROJECT_TOOL_SPEC = Tool(
    name="update_project",
    description="Update a project by ID (requires organization-scoped API key).",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "name": {"type": "string"},
            "metadata": {"type": "object"},
            "retention": {"type": "integer"},
        },
        "required": ["project_id", "name"],
    },
)

DELETE_PROJECT_TOOL_SPEC = Tool(
    name="delete_project",
    description="Delete a project by ID (requires organization-scoped API key).",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
        },
        "required": ["project_id"],
    },
)


class GetProjectsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            projects = await self._fetch_with_retry(
                self.langfuse.api.projects.get
            )
            items = projects.data if hasattr(projects, "data") else []
            response = f"[LIST] **Projects** ({len(items)} found):\n\n"
            for item in items:
                response += f"- {item.id} {item.name}\n"
            return response
        except Exception as e:
            return f"Error fetching projects: {str(e)}"


class CreateProjectTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            project = await self._fetch_with_retry(
                self.langfuse.api.projects.create,
                name=args["name"],
                retention=args.get("retention", 0),
                metadata=args.get("metadata"),
            )
            return f"[OK] Project created\nID: {project.id}\nName: {project.name}"
        except Exception as e:
            return f"Error creating project: {str(e)}"


class UpdateProjectTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            project = await self._fetch_with_retry(
                self.langfuse.api.projects.update,
                project_id=args["project_id"],
                name=args["name"],
                metadata=args.get("metadata"),
                retention=args.get("retention"),
            )
            return f"[OK] Project updated\nID: {project.id}\nName: {project.name}"
        except Exception as e:
            return f"Error updating project: {str(e)}"


class DeleteProjectTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            response = await self._fetch_with_retry(
                self.langfuse.api.projects.delete,
                project_id=args["project_id"],
            )
            msg = response.message if hasattr(response, "message") else "Deletion queued"
            return f"[OK] Project deletion requested: {msg}"
        except Exception as e:
            return f"Error deleting project: {str(e)}"
