"""
Exports / Blob Storage Integrations Tools
Aligned with Langfuse public API
"""

from typing import Any, Dict, Optional
from datetime import datetime

from mcp.types import Tool
from langfuse.api.blob_storage_integrations import (
    BlobStorageExportFrequency,
    BlobStorageExportMode,
    BlobStorageIntegrationFileType,
    BlobStorageIntegrationType,
)

from ..core.base_tool import BaseLangfuseTool


GET_BLOB_STORAGE_INTEGRATIONS_TOOL_SPEC = Tool(
    name="get_blob_storage_integrations",
    description="List all blob storage integrations (requires organization-scoped API key).",
    inputSchema={"type": "object", "properties": {}},
)

UPSERT_BLOB_STORAGE_INTEGRATION_TOOL_SPEC = Tool(
    name="upsert_blob_storage_integration",
    description="Create or update a blob storage integration (requires organization-scoped API key).",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Project ID"},
            "type": {"type": "string", "enum": ["S3", "S3_COMPATIBLE", "AZURE_BLOB_STORAGE"]},
            "bucket_name": {"type": "string", "description": "Bucket name"},
            "region": {"type": "string", "description": "Region"},
            "export_frequency": {"type": "string", "enum": ["hourly", "daily", "weekly"]},
            "enabled": {"type": "boolean"},
            "force_path_style": {"type": "boolean"},
            "file_type": {"type": "string", "enum": ["JSON", "CSV", "JSONL"]},
            "export_mode": {"type": "string", "enum": ["FULL_HISTORY", "FROM_TODAY", "FROM_CUSTOM_DATE"]},
            "endpoint": {"type": "string", "description": "Custom endpoint URL (required for S3_COMPATIBLE)"},
            "access_key_id": {"type": "string"},
            "secret_access_key": {"type": "string"},
            "prefix": {"type": "string", "description": "Path prefix for exported files (must end with /)"},
            "export_start_date": {"type": "string", "format": "date-time"},
        },
        "required": [
            "project_id",
            "type",
            "bucket_name",
            "region",
            "export_frequency",
            "enabled",
            "force_path_style",
            "file_type",
            "export_mode",
        ],
    },
)

GET_BLOB_STORAGE_INTEGRATION_STATUS_TOOL_SPEC = Tool(
    name="get_blob_storage_integration_status",
    description="Get sync status for a blob storage integration by ID.",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string"},
        },
        "required": ["id"],
    },
)

DELETE_BLOB_STORAGE_INTEGRATION_TOOL_SPEC = Tool(
    name="delete_blob_storage_integration",
    description="Delete a blob storage integration by ID.",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string"},
        },
        "required": ["id"],
    },
)


class GetBlobStorageIntegrationsTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            integrations = await self._fetch_with_retry(
                self.langfuse.api.blob_storage_integrations.get_blob_storage_integrations
            )
            items = integrations.data if hasattr(integrations, "data") else []
            response = f"[LIST] **Blob Storage Integrations** ({len(items)} found):\n\n"
            for item in items:
                response += f"- {item.id} ({item.type}) project={item.project_id}\n"
            return response
        except Exception as e:
            return f"Error fetching blob storage integrations: {str(e)}"


class UpsertBlobStorageIntegrationTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            export_start_date = self._parse_datetime(args.get("export_start_date"))
            integration = await self._fetch_with_retry(
                self.langfuse.api.blob_storage_integrations.upsert_blob_storage_integration,
                project_id=args["project_id"],
                type=BlobStorageIntegrationType(args["type"]),
                bucket_name=args["bucket_name"],
                region=args["region"],
                export_frequency=BlobStorageExportFrequency(args["export_frequency"]),
                enabled=args["enabled"],
                force_path_style=args["force_path_style"],
                file_type=BlobStorageIntegrationFileType(args["file_type"]),
                export_mode=BlobStorageExportMode(args["export_mode"]),
                endpoint=args.get("endpoint"),
                access_key_id=args.get("access_key_id"),
                secret_access_key=args.get("secret_access_key"),
                prefix=args.get("prefix"),
                export_start_date=export_start_date,
            )
            return (
                "[OK] Blob storage integration upserted\n"
                f"ID: {integration.id}\n"
                f"Project: {integration.project_id}\n"
                f"Type: {integration.type}\n"
                f"Bucket: {integration.bucket_name}\n"
            )
        except Exception as e:
            return f"Error upserting blob storage integration: {str(e)}"

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            if value.endswith("Z"):
                value = value.replace("Z", "+00:00")
            return datetime.fromisoformat(value)
        except Exception:
            return None


class GetBlobStorageIntegrationStatusTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            status = await self._fetch_with_retry(
                self.langfuse.api.blob_storage_integrations.get_blob_storage_integration_status,
                args["id"],
            )
            response = (
                "[INFO] Blob Storage Integration Status\n"
                f"ID: {status.id}\n"
                f"Project: {status.project_id}\n"
                f"Status: {status.sync_status}\n"
                f"Enabled: {status.enabled}\n"
                f"Last Sync: {self._format_datetime(status.last_sync_at) if hasattr(status, 'last_sync_at') else 'N/A'}\n"
                f"Next Sync: {self._format_datetime(status.next_sync_at) if hasattr(status, 'next_sync_at') else 'N/A'}\n"
            )
            return response
        except Exception as e:
            return f"Error fetching blob storage integration status: {str(e)}"


class DeleteBlobStorageIntegrationTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            response = await self._fetch_with_retry(
                self.langfuse.api.blob_storage_integrations.delete_blob_storage_integration,
                args["id"],
            )
            msg = response.message if hasattr(response, "message") else "Deleted"
            return f"[OK] Blob storage integration deleted: {msg}"
        except Exception as e:
            return f"Error deleting blob storage integration: {str(e)}"
