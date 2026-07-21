from typing import Any, Dict, List, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent

# All tool implementations - READ operations
from ..tools.scores import (
    GetScoresTool,
    SubmitScoreTool,
    GET_SCORES_TOOL_SPEC,
    SUBMIT_SCORE_TOOL_SPEC,
)
from ..tools.metrics import GetMetricsTool, METRICS_TOOL_SPEC
from ..tools.prompts import GetPromptsTool, PROMPTS_TOOL_SPEC, CreatePromptTool, CREATE_PROMPT_TOOL_SPEC, DeletePromptTool, DELETE_PROMPT_TOOL_SPEC
from ..tools.sessions import GetSessionsTool, SESSIONS_TOOL_SPEC
from ..tools.datasets import GetDatasetsTool, DATASETS_TOOL_SPEC
from ..tools.models import GetModelsTool, MODELS_TOOL_SPEC, CreateModelTool, CREATE_MODEL_TOOL_SPEC, DeleteModelTool, DELETE_MODEL_TOOL_SPEC
from ..tools.comments import (
    GetCommentsTool,
    AddCommentTool,
    GET_COMMENTS_TOOL_SPEC,
    ADD_COMMENT_TOOL_SPEC,
)
from ..tools.score_configs import GetScoreConfigsTool, SCORE_CONFIGS_TOOL_SPEC
from ..tools.watch_agents import WatchAgentsTool, WATCH_AGENTS_TOOL_SPEC
from ..tools.trace import GetTraceTool, GET_TRACE_TOOL_SPEC, DeleteTraceTool, DELETE_TRACE_TOOL_SPEC
from ..tools.analyze_performance import AnalyzePerformanceTool, ANALYZE_PERFORMANCE_TOOL_SPEC
from ..tools.cost_metrics import GetCostMetricsTool, GET_COST_METRICS_TOOL_SPEC

# CRUD operations - CREATE/UPDATE/DELETE
from ..tools.datasets import (
    CreateDatasetTool,
    CreateDatasetItemTool,
    CREATE_DATASET_TOOL_SPEC,
    CREATE_DATASET_ITEM_TOOL_SPEC,
)

from ..tools.annotation_queues import (
    GetAnnotationQueuesTool,
    CreateAnnotationQueueTool,
    GetQueueItemsTool,
    ResolveQueueItemTool,
    GET_ANNOTATION_QUEUES_TOOL_SPEC,
    CREATE_ANNOTATION_QUEUE_TOOL_SPEC,
    GET_QUEUE_ITEMS_TOOL_SPEC,
    RESOLVE_QUEUE_ITEM_TOOL_SPEC,
)
from ..tools.blob_storage_integrations import (
    GetBlobStorageIntegrationsTool,
    UpsertBlobStorageIntegrationTool,
    GetBlobStorageIntegrationStatusTool,
    DeleteBlobStorageIntegrationTool,
    GET_BLOB_STORAGE_INTEGRATIONS_TOOL_SPEC,
    UPSERT_BLOB_STORAGE_INTEGRATION_TOOL_SPEC,
    GET_BLOB_STORAGE_INTEGRATION_STATUS_TOOL_SPEC,
    DELETE_BLOB_STORAGE_INTEGRATION_TOOL_SPEC,
)
from ..tools.llm_connections import (
    GetLlmConnectionsTool,
    UpsertLlmConnectionTool,
    GET_LLM_CONNECTIONS_TOOL_SPEC,
    UPSERT_LLM_CONNECTION_TOOL_SPEC,
)
from ..tools.projects import (
    GetProjectsTool,
    CreateProjectTool,
    UpdateProjectTool,
    DeleteProjectTool,
    GET_PROJECTS_TOOL_SPEC,
    CREATE_PROJECT_TOOL_SPEC,
    UPDATE_PROJECT_TOOL_SPEC,
    DELETE_PROJECT_TOOL_SPEC,
)


def setup_tools(langfuse_client: Any, cache: Any, metrics: Any) -> Dict[str, Any]:
    """Initialize all tool instances with shared cache and metrics."""

    def create_tool(tool_class):
        return tool_class(
            langfuse_client=langfuse_client,
            cache=cache,
            metrics=metrics,
        )

    tools = {
        # Monitoring & Analytics
        "watch_agents": create_tool(WatchAgentsTool),
        "get_trace": create_tool(GetTraceTool),
        "analyze_performance": create_tool(AnalyzePerformanceTool),
        "get_cost_metrics": create_tool(GetCostMetricsTool),

        # Scores & Evaluation (READ/WRITE)
        "get_scores": create_tool(GetScoresTool),
        "submit_score": create_tool(SubmitScoreTool),
        "get_score_configs": create_tool(GetScoreConfigsTool),

        # Metrics & Analytics
        "get_metrics": create_tool(GetMetricsTool),

        # Prompts (READ/WRITE)
        "get_prompts": create_tool(GetPromptsTool),
        "create_prompt": create_tool(CreatePromptTool),
        "delete_prompt": create_tool(DeletePromptTool),

        # Sessions
        "get_sessions": create_tool(GetSessionsTool),

        # Datasets (CRUD)
        "get_datasets": create_tool(GetDatasetsTool),
        "create_dataset": create_tool(CreateDatasetTool),
        "create_dataset_item": create_tool(CreateDatasetItemTool),

        # Models (READ/WRITE)
        "get_models": create_tool(GetModelsTool),
        "create_model": create_tool(CreateModelTool),
        "delete_model": create_tool(DeleteModelTool),

        # Comments (CRUD)
        "get_comments": create_tool(GetCommentsTool),
        "add_comment": create_tool(AddCommentTool),

        # Traces (UPDATE/DELETE)
        "delete_trace": create_tool(DeleteTraceTool),

        # Annotation Queues (CRUD)
        "get_annotation_queues": create_tool(GetAnnotationQueuesTool),
        "create_annotation_queue": create_tool(CreateAnnotationQueueTool),
        "get_queue_items": create_tool(GetQueueItemsTool),
        "resolve_queue_item": create_tool(ResolveQueueItemTool),

        # Exports / Blob Storage Integrations
        "get_blob_storage_integrations": create_tool(GetBlobStorageIntegrationsTool),
        "upsert_blob_storage_integration": create_tool(UpsertBlobStorageIntegrationTool),
        "get_blob_storage_integration_status": create_tool(GetBlobStorageIntegrationStatusTool),
        "delete_blob_storage_integration": create_tool(DeleteBlobStorageIntegrationTool),

        # LLM Connections
        "get_llm_connections": create_tool(GetLlmConnectionsTool),
        "upsert_llm_connection": create_tool(UpsertLlmConnectionTool),

        # Projects
        "get_projects": create_tool(GetProjectsTool),
        "create_project": create_tool(CreateProjectTool),
        "update_project": create_tool(UpdateProjectTool),
        "delete_project": create_tool(DeleteProjectTool),
    }

    print(f"[OK] Initialized {len(tools)} tools")

    read_tools = len(
        [
            t
            for t in tools.keys()
            if t.startswith("get_") or t == "watch_agents" or t == "analyze_performance"
        ]
    )
    write_tools = len(
        [
            t
            for t in tools.keys()
            if any(t.startswith(p) for p in ["create_", "update_", "submit_", "add_"])
        ]
    )
    delete_tools = len(
        [t for t in tools.keys() if t.startswith("delete_") or t.startswith("resolve_")]
    )

    print(f"   [DOCS] READ operations: {read_tools}")
    print(f"   [WRITE]  WRITE operations: {write_tools}")
    print(f"   [DELETE]  DELETE operations: {delete_tools}")

    return tools


def register_tools(server: Server, tools: Dict[str, Any]) -> List[Tool]:
    """Register all MCP tools with the server."""

    tool_specs = [
        # Monitoring & Analytics
        WATCH_AGENTS_TOOL_SPEC,
        GET_TRACE_TOOL_SPEC,
        ANALYZE_PERFORMANCE_TOOL_SPEC,
        GET_COST_METRICS_TOOL_SPEC,
        METRICS_TOOL_SPEC,

        # Scores & Evaluation
        GET_SCORES_TOOL_SPEC,
        SUBMIT_SCORE_TOOL_SPEC,
        SCORE_CONFIGS_TOOL_SPEC,

        # Prompts
        PROMPTS_TOOL_SPEC,
        CREATE_PROMPT_TOOL_SPEC,
        DELETE_PROMPT_TOOL_SPEC,

        # Sessions
        SESSIONS_TOOL_SPEC,

        # Datasets
        DATASETS_TOOL_SPEC,
        CREATE_DATASET_TOOL_SPEC,
        CREATE_DATASET_ITEM_TOOL_SPEC,

        # Models
        MODELS_TOOL_SPEC,
        CREATE_MODEL_TOOL_SPEC,
        DELETE_MODEL_TOOL_SPEC,

        # Comments
        GET_COMMENTS_TOOL_SPEC,
        ADD_COMMENT_TOOL_SPEC,

        # Traces
        DELETE_TRACE_TOOL_SPEC,

        # Annotation Queues
        GET_ANNOTATION_QUEUES_TOOL_SPEC,
        CREATE_ANNOTATION_QUEUE_TOOL_SPEC,
        GET_QUEUE_ITEMS_TOOL_SPEC,
        RESOLVE_QUEUE_ITEM_TOOL_SPEC,

        # Exports / Blob Storage Integrations
        GET_BLOB_STORAGE_INTEGRATIONS_TOOL_SPEC,
        UPSERT_BLOB_STORAGE_INTEGRATION_TOOL_SPEC,
        GET_BLOB_STORAGE_INTEGRATION_STATUS_TOOL_SPEC,
        DELETE_BLOB_STORAGE_INTEGRATION_TOOL_SPEC,

        # LLM Connections
        GET_LLM_CONNECTIONS_TOOL_SPEC,
        UPSERT_LLM_CONNECTION_TOOL_SPEC,

        # Projects
        GET_PROJECTS_TOOL_SPEC,
        CREATE_PROJECT_TOOL_SPEC,
        UPDATE_PROJECT_TOOL_SPEC,
        DELETE_PROJECT_TOOL_SPEC,
    ]

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available monitoring tools."""
        return tool_specs

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute MCP tool with error handling."""
        print(f"[CONFIG] Tool invoked: {name}")

        tool = tools.get(name)
        if not tool:
            error_msg = f"Unknown tool: {name}. Available tools: {', '.join(tools.keys())}"
            return [TextContent(type="text", text=error_msg)]

        try:
            result = await tool.execute(arguments)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            error_msg = f"Error executing {name}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return [TextContent(type="text", text=error_msg)]

    print(f"[OK] Registered {len(tool_specs)} MCP tools")
    return tool_specs
