"""
Metrics Tool - Aggregated Analytics via Langfuse Metrics API
CRITICAL: This was completely missing - replaced broken manual calculations

The Metrics API provides pre-aggregated analytics:
- Much faster than fetching all traces and calculating manually
- Supports percentiles (p50, p95, p99) for latency
- Multi-dimensional grouping
- Powerful filtering
- Time-series analysis
"""

from typing import Any, Dict, List, Optional
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool


# ============================================================================
# TOOL SPEC
# ============================================================================

METRICS_TOOL_SPEC = Tool(
    name="get_metrics",
    description=(
        "Get aggregated metrics and analytics from Langfuse. "
        "Use this for performance analysis, cost tracking, and usage patterns. "
        "Much faster and more powerful than manual calculation. "
        "Supports grouping by multiple dimensions, percentile calculations, and time-series data."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "view": {
                "type": "string",
                "enum": ["traces", "observations", "scores"],
                "default": "observations",
                "description": "Data view to query (observations recommended for most use cases)",
            },
            "metrics": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "trace_count",
                        "observation_count",
                        "total_cost",
                        "latency_p50",
                        "latency_p75",
                        "latency_p90",
                        "latency_p95",
                        "latency_p99",
                        "input_tokens",
                        "output_tokens",
                        "total_tokens",
                        "usage_count",
                    ],
                },
                "default": ["trace_count", "total_cost", "latency_p50", "latency_p95"],
                "description": "Metrics to calculate",
            },
            "dimensions": {
                "type": "array",
                "items": {"type": "string"},
                "default": [],
                "description": "Dimension fields to include (e.g., 'model', 'user_id', 'trace_name')",
            },
            "group_by": {
                "type": "array",
                "items": {"type": "string"},
                "default": [],
                "description": "Fields to group results by (e.g., ['model', 'user_id'])",
            },
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "column": {"type": "string"},
                        "operator": {
                            "type": "string",
                            "enum": ["=", "!=", ">", ">=", "<", "<=", "contains", "not_contains"],
                        },
                        "value": {},
                    },
                },
                "default": [],
                "description": "Filter conditions (e.g., [{column: 'trace_tags', operator: 'contains', value: 'production'}])",
            },
            "time_range": {
                "type": "object",
                "properties": {
                    "from": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Start timestamp (ISO 8601)",
                    },
                    "to": {
                        "type": "string",
                        "format": "date-time",
                        "description": "End timestamp (ISO 8601)",
                    },
                },
                "description": "Time range for the query",
            },
            "granularity": {
                "type": "string",
                "enum": ["hour", "day", "week", "month"],
                "description": "Time granularity for time-series results",
            },
            "preset": {
                "type": "string",
                "enum": [
                    "performance_overview",
                    "cost_analysis",
                    "model_comparison",
                    "user_activity",
                    "latency_analysis",
                ],
                "description": "Use a preset configuration for common use cases",
            },
        },
    },
)


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

METRIC_PRESETS = {
    "performance_overview": {
        "view": "observations",
        "metrics": [
            "trace_count",
            "observation_count",
            "total_cost",
            "latency_p50",
            "latency_p95",
            "latency_p99",
            "total_tokens",
        ],
        "group_by": ["model"],
    },
    "cost_analysis": {
        "view": "observations",
        "metrics": [
            "trace_count",
            "total_cost",
            "input_tokens",
            "output_tokens",
            "total_tokens",
        ],
        "group_by": ["model", "user_id"],
    },
    "model_comparison": {
        "view": "observations",
        "metrics": [
            "observation_count",
            "total_cost",
            "latency_p50",
            "latency_p95",
            "total_tokens",
        ],
        "group_by": ["model"],
    },
    "user_activity": {
        "view": "traces",
        "metrics": ["trace_count", "total_cost"],
        "group_by": ["user_id"],
    },
    "latency_analysis": {
        "view": "observations",
        "metrics": [
            "observation_count",
            "latency_p50",
            "latency_p75",
            "latency_p90",
            "latency_p95",
            "latency_p99",
        ],
        "group_by": ["model", "observation_name"],
    },
}

VIEW_MAP = {
    "traces": "traces",
    "observations": "observations",
    "scores": "scores-numeric",
    "scores-numeric": "scores-numeric",
    "scores-categorical": "scores-categorical",
}

FIELD_MAP = {
    "user_id": "userId",
    "session_id": "sessionId",
    "trace_id": "traceId",
    "trace_name": "traceName",
    "trace_release": "traceRelease",
    "trace_version": "traceVersion",
    "trace_tags": "tags",
    "observation_name": "name",
    "observation_type": "type",
    "model": "providedModelName",
}

FIELD_MAP_TRACES = {
    "trace_name": "name",
    "trace_release": "release",
    "trace_version": "version",
    "trace_tags": "tags",
    "user_id": "userId",
    "session_id": "sessionId",
}

ALLOWED_DIMENSIONS_BY_VIEW = {
    "traces": {
        "id",
        "name",
        "tags",
        "userId",
        "sessionId",
        "release",
        "version",
        "environment",
        "timestampMonth",
    },
}

METRIC_MAP = {
    "trace_count": ("count", "count"),
    "observation_count": ("count", "count"),
    "total_cost": ("totalCost", "sum"),
    "latency_p50": ("latency", "p50"),
    "latency_p75": ("latency", "p75"),
    "latency_p90": ("latency", "p90"),
    "latency_p95": ("latency", "p95"),
    "latency_p99": ("latency", "p99"),
    "input_tokens": ("inputTokens", "sum"),
    "output_tokens": ("outputTokens", "sum"),
    "total_tokens": ("totalTokens", "sum"),
    "usage_count": ("count", "count"),
}

OPERATOR_MAP = {
    "not_contains": "does not contain",
}

def _infer_filter_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "arrayOptions"
    return "string"

def _map_field(field: str, view: Optional[str] = None) -> str:
    if view == "traces":
        return FIELD_MAP_TRACES.get(field, FIELD_MAP.get(field, field))
    return FIELD_MAP.get(field, field)

def _build_query_filters(filters: List[Dict[str, Any]], view: Optional[str] = None) -> List[Dict[str, Any]]:
    normalized = []
    for f in filters:
        if not f or "column" not in f or "operator" not in f:
            continue
        column = _map_field(f["column"], view)
        operator = OPERATOR_MAP.get(f["operator"], f["operator"])
        value = f.get("value")
        normalized.append({
            "column": column,
            "operator": operator,
            "value": value,
            "type": _infer_filter_type(value),
        })
    return normalized

def build_metrics_query(args: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
    """Build a Langfuse metrics query (legacy v1/v2 compatible) from tool args."""
    view = VIEW_MAP.get(args.get("view", "observations"), args.get("view", "observations"))
    dropped_dimensions: List[str] = []

    metrics = []
    for metric_name in args.get("metrics", []):
        if metric_name not in METRIC_MAP:
            continue
        measure, aggregation = METRIC_MAP[metric_name]
        metrics.append({
            "measure": measure,
            "aggregation": aggregation,
            "alias": metric_name,
        })

    if not metrics:
        raise ValueError("No supported metrics requested")

    query: Dict[str, Any] = {
        "view": view,
        "metrics": metrics,
    }

    # Dimensions / group_by
    dimensions = []
    for field in (args.get("group_by") or []) + (args.get("dimensions") or []):
        mapped = _map_field(field, view)
        allowed = ALLOWED_DIMENSIONS_BY_VIEW.get(view)
        if allowed is not None and mapped not in allowed:
            dropped_dimensions.append(f"{field}->{mapped}")
            continue
        dimensions.append({"field": mapped})
    if dimensions:
        # De-duplicate while preserving order
        seen = set()
        deduped = []
        for d in dimensions:
            if d["field"] in seen:
                continue
            seen.add(d["field"])
            deduped.append(d)
        query["dimensions"] = deduped

    # Filters
    if args.get("filters"):
        query["filters"] = _build_query_filters(args["filters"], view)

    # Time range
    if args.get("time_range"):
        tr = args["time_range"]
        if tr.get("from"):
            query["fromTimestamp"] = tr["from"]
        if tr.get("to"):
            query["toTimestamp"] = tr["to"]

    # Time granularity
    if args.get("granularity"):
        query["timeDimension"] = {"granularity": args["granularity"]}

    return query, dropped_dimensions


# ============================================================================
# TOOL IMPLEMENTATION
# ============================================================================

class GetMetricsTool(BaseLangfuseTool):
    """Get aggregated metrics from Langfuse Metrics API"""
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Execute get_metrics tool"""
        
        try:
            # Handle preset configurations
            if args.get("preset"):
                preset_name = args["preset"]
                
                if preset_name not in METRIC_PRESETS:
                    return f"Unknown preset: {preset_name}"
                
                preset_config = METRIC_PRESETS[preset_name].copy()
                
                # Merge preset with user args (user args take precedence)
                for key, value in args.items():
                    if key != "preset" and value:
                        preset_config[key] = value
                
                args = preset_config
                self.logger.info("Using preset configuration", preset=preset_name)
            
            # Build metrics query
            query, dropped_dimensions = build_metrics_query(args)
            
            # Fetch metrics with retry
            self.logger.info("Fetching metrics", query=query)
            
            metrics_response = await self._fetch_with_retry(
                self.langfuse.get_metrics,
                query
            )
            
            # Format and return response
            response = self._format_metrics_response(
                metrics_response,
                args
            )
            if dropped_dimensions:
                response += "\n[WARN] Dropped unsupported dimensions for this view: "
                response += ", ".join(dropped_dimensions)
                response += "\n"
            
            return response
        
        except Exception as e:
            self.logger.error("Error fetching metrics", error=str(e))
            return f"Error fetching metrics: {str(e)}"
    
    def _format_metrics_response(
        self,
        metrics_response: Any,
        args: Dict[str, Any]
    ) -> str:
        """Format metrics into readable response"""
        
        response = "[STATS] **Aggregated Metrics**\n\n"
        
        # Add query info
        view = args.get("view", "observations")
        response += f"**View**: {view}\n"
        
        if args.get("preset"):
            response += f"**Preset**: {args['preset']}\n"
        
        if args.get("metrics"):
            response += f"**Metrics**: {', '.join(args['metrics'])}\n"
        
        if args.get("group_by"):
            response += f"**Grouped by**: {', '.join(args['group_by'])}\n"
        
        if args.get("time_range"):
            tr = args["time_range"]
            response += f"**Time Range**: {tr.get('from', 'start')} to {tr.get('to', 'now')}\n"
        
        response += "\n"
        
        # Handle different response formats
        if hasattr(metrics_response, 'data'):
            data = metrics_response.data
        else:
            data = metrics_response
        
        # Check if time-series or grouped data
        if isinstance(data, list):
            if args.get("granularity"):
                response += self._format_timeseries_metrics(data, args)
            else:
                response += self._format_grouped_metrics(data, args)
        else:
            response += self._format_single_metric(data, args)
        
        return response
    
    def _format_timeseries_metrics(
        self,
        data: List[Any],
        args: Dict[str, Any]
    ) -> str:
        """Format time-series metrics"""
        
        response = "**Time-Series Data:**\n\n"
        
        granularity = args.get("granularity", "day")
        metrics = args.get("metrics", [])
        
        for i, point in enumerate(data[:20], 1):  # Limit to 20 points
            timestamp = self._get_item_value(point, "timestamp")
            if timestamp is None:
                timestamp = self._get_item_value(point, "time")
            if timestamp is None:
                timestamp = self._get_item_value(point, "bucket")
            if timestamp is not None:
                response += f"**{timestamp}** ({granularity}):\n"
            else:
                response += f"**Period {i}**:\n"
            
            # Show each metric
            for metric in metrics:
                value = self._get_item_value(point, metric)
                if value is not None:
                    response += f"  - {metric}: {self._format_metric_value(metric, value)}\n"
            
            response += "\n"
        
        if len(data) > 20:
            response += f"... and {len(data) - 20} more data points\n"
        
        return response
    
    def _format_grouped_metrics(
        self,
        data: List[Any],
        args: Dict[str, Any]
    ) -> str:
        """Format grouped metrics"""
        
        response = "**Grouped Results:**\n\n"
        
        group_by = args.get("group_by", [])
        view = VIEW_MAP.get(args.get("view", "observations"), args.get("view", "observations"))
        metrics = args.get("metrics", [])
        
        for i, group in enumerate(data[:50], 1):  # Limit to 50 groups
            # Show group identifiers
            group_label = []
            for field in group_by:
                mapped_field = _map_field(field, view)
                value = self._get_item_value(group, mapped_field)
                if value is not None:
                    group_label.append(f"{field}={value}")
            
            if group_label:
                response += f"**{' | '.join(group_label)}**:\n"
            else:
                response += f"**Group {i}**:\n"
            
            # Show metrics for this group
            for metric in metrics:
                value = self._get_item_value(group, metric)
                if value is not None:
                    response += f"  - {metric}: {self._format_metric_value(metric, value)}\n"
            
            response += "\n"
        
        if len(data) > 50:
            response += f"... and {len(data) - 50} more groups\n"
        
        return response
    
    def _format_single_metric(
        self,
        data: Any,
        args: Dict[str, Any]
    ) -> str:
        """Format single aggregated metric result"""
        
        response = "**Aggregated Results:**\n\n"
        
        metrics = args.get("metrics", [])
        
        for metric in metrics:
            value = self._get_item_value(data, metric)
            if value is not None:
                response += f"  - **{metric}**: {self._format_metric_value(metric, value)}\n"
        
        return response
    
    def _format_metric_value(self, metric_name: str, value: Any) -> str:
        """Format metric value based on type"""
        
        if value is None:
            return "N/A"
        
        # Cost metrics
        if "cost" in metric_name.lower():
            return self._format_cost(float(value))
        
        # Latency metrics (in milliseconds)
        if "latency" in metric_name.lower():
            return self._format_duration(float(value))
        
        # Token metrics
        if "token" in metric_name.lower():
            return self._format_tokens(int(value))
        
        # Count metrics
        if "count" in metric_name.lower():
            return f"{int(value):,}"
        
        # Default: numeric with 2 decimals
        try:
            return f"{float(value):.2f}"
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _get_item_value(item: Any, key: str) -> Optional[Any]:
        if isinstance(item, dict):
            return item.get(key)
        return getattr(item, key, None)
