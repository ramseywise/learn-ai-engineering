"""
Cost Metrics Tool - Dynamic cost and token analytics via Langfuse Metrics API v1.
"""

import json
from typing import Any, Dict, List, Optional
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool


# ============================================================================
# CONSTANTS — verified against actual Langfuse Metrics API v1 behavior
# ============================================================================

VIEW_MEASURES = {
    "traces":             ["count", "observationsCount", "scoresCount", "latency", "totalTokens", "totalCost"],
    "observations":       ["count", "latency", "totalTokens", "totalCost", "timeToFirstToken", "countScores"],
    "scores-numeric":     ["count", "value"],
    "scores-categorical": ["count"],
}

VIEW_DIMENSIONS = {
    "traces": [
        "name", "tags", "userId", "sessionId", "release", "version",
        "environment", "observationName", "scoreName",
    ],
    "observations": [
        "traceName", "environment", "parentObservationId", "type",
        "name", "level", "version", "providedModelName", "promptName",
        "promptVersion", "userId", "sessionId", "traceRelease", "traceVersion", "scoreName",
    ],
    "scores-numeric": [
        "name", "environment", "source", "dataType", "traceId", "traceName",
        "userId", "sessionId", "observationId", "observationName",
        "observationModelName", "observationPromptName", "observationPromptVersion", "configId",
    ],
    "scores-categorical": [
        "name", "environment", "source", "dataType", "traceId", "traceName",
        "userId", "sessionId", "observationId", "observationName",
        "observationModelName", "observationPromptName", "observationPromptVersion",
        "configId", "stringValue",
    ],
}

# Actual operators accepted by the API (verified from 400 error responses)
# String fields: =, contains, does not contain, starts with, ends with
# Numeric/datetime fields: =, <, >, <=, >=
FILTER_OPERATORS_STRING   = ["=", "contains", "does not contain", "starts with", "ends with"]
FILTER_OPERATORS_NUMERIC  = ["=", "<", ">", "<=", ">="]
FILTER_OPERATORS_DATETIME = ["=", "<", ">", "<=", ">="]

# High-cardinality fields: valid in filters but NOT as dimensions
HIGH_CARDINALITY_FIELDS = {"id", "traceId", "observationId"}


# ============================================================================
# TOOL SPEC
# ============================================================================

GET_COST_METRICS_TOOL_SPEC = Tool(
    name="get_cost_metrics",
    description=(
        "Query Langfuse cost, token, latency, and usage analytics via the Metrics API. "
        "All aggregation is handled server-side. Use this for totals, breakdowns, time series, percentiles. "
        "\n\n"
        "REQUIRED: view, at least one metric, fromTimestamp, toTimestamp.\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "VIEW\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  traces         → trace-level: end-to-end cost, tokens, latency per request\n"
        "  observations   → observation-level: per LLM call; USE for model breakdowns (providedModelName)\n"
        "  scores-numeric → numeric/boolean evaluation scores\n"
        "  scores-categorical → categorical evaluation scores\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "MEASURES (by view)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "traces:       count, observationsCount, scoresCount, latency, totalTokens, totalCost\n"
        "observations: count, latency, totalTokens, totalCost, timeToFirstToken, countScores\n"
        "scores-numeric: count, value\n"
        "scores-categorical: count\n"
        "NEVER USE: inputTokens, outputTokens, promptTokens, completionTokens — these cause 400 errors.\n"
        "   Use totalTokens instead.\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "AGGREGATIONS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  sum, avg, count, max, min, p50, p75, p90, p95, p99\n"
        "  Use sum for cost/token totals. Use avg/p95/p99 for latency. Use count for record counts.\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "DIMENSIONS (group-by fields, by view)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "traces:       name, tags, userId, sessionId, release, version, environment, observationName, scoreName\n"
        "observations: providedModelName, type, name, level, version, environment, userId, sessionId,\n"
        "              traceName, traceRelease, traceVersion, promptName, promptVersion, scoreName\n"
        "HIGH CARDINALITY — cannot be dimensions, only filters: id, traceId, observationId\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "FILTERS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Each filter: { column, operator, value, type, key? }\n"
        "  column   → dimension field name (e.g. environment, userId, providedModelName, type, traceId)\n"
        "  type     → string | number | boolean | stringObject | datetime\n"
        "  operator → depends on type:\n"
        "    string/stringObject: =  |  contains  |  does not contain  |  starts with  |  ends with\n"
        "    number/datetime:     =  |  <  |  >  |  <=  |  >=\n"
        "  key      → only for type=stringObject (metadata key-value filters)\n"
        "NEVER USE for string fields: !=, not_contains, not_equals — these cause 400 errors.\n"
        "   To exclude a value, use a separate filter with a positive match on what you DO want.\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "SORTING (sort_by)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Sorting is applied CLIENT-SIDE after the API response.\n"
        "Provide sort_by: { field, direction } where field is a key in the response rows.\n"
        "Check the response row keys to find valid sort field names (they vary by query).\n"
        "Do NOT use orderBy in the API query — it causes 400 errors with unpredictable field naming.\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "EXAMPLES\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "'Total cost last 7 days'\n"
        "  view=traces, metrics=[{totalCost,sum}], fromTimestamp=..., toTimestamp=...\n\n"
        "'Daily cost trend this week'\n"
        "  view=traces, metrics=[{totalCost,sum},{count,count}],\n"
        "  timeDimension={day}, fromTimestamp=..., toTimestamp=...\n\n"
        "'Cost by model, highest first'\n"
        "  view=observations, metrics=[{totalCost,sum},{totalTokens,sum},{count,count}],\n"
        "  dimensions=[{providedModelName}], sort_by={field=<cost_field_from_response>, direction=desc}\n\n"
        "'Cost for user X this month'\n"
        "  view=traces, metrics=[{totalCost,sum},{totalTokens,sum}],\n"
        "  filters=[{column=userId, operator==, value=X, type=string}]\n\n"
        "'Only gpt-5-mini observations'\n"
        "  view=observations, metrics=[{totalCost,sum},{count,count}],\n"
        "  filters=[{column=providedModelName, operator==, value=gpt-5-mini, type=string}]\n\n"
        "'Production environment only'\n"
        "  filters=[{column=environment, operator==, value=production, type=string}]"
    ),
    inputSchema={
        "type": "object",
        "required": ["view", "metrics", "fromTimestamp", "toTimestamp"],
        "properties": {
            "view": {
                "type": "string",
                "enum": ["traces", "observations", "scores-numeric", "scores-categorical"],
                "description": (
                    "Dataset to query. Use 'observations' for model-level breakdowns (has providedModelName). "
                    "Use 'traces' for end-to-end request cost/latency."
                ),
            },
            "metrics": {
                "type": "array",
                "minItems": 1,
                "description": (
                    "Metrics to compute. Each needs measure + aggregation. Alias is optional. "
                    "Example: [{\"measure\": \"totalCost\", \"aggregation\": \"sum\", \"alias\": \"total_cost\"}]. "
                    "Only use measures valid for the chosen view. "
                    "inputTokens/outputTokens are invalid — use totalTokens."
                ),
                "items": {
                    "type": "object",
                    "required": ["measure", "aggregation"],
                    "properties": {
                        "measure": {
                            "type": "string",
                            "description": (
                                "What to measure. Must match the chosen view:\n"
                                "traces: count | observationsCount | scoresCount | latency | totalTokens | totalCost\n"
                                "observations: count | latency | totalTokens | totalCost | timeToFirstToken | countScores\n"
                                "scores-numeric: count | value\n"
                                "scores-categorical: count"
                            ),
                        },
                        "aggregation": {
                            "type": "string",
                            "enum": ["sum", "avg", "count", "max", "min", "p50", "p75", "p90", "p95", "p99"],
                            "description": "How to aggregate. sum for totals, avg/p95 for latency, count for record counts.",
                        },
                        "alias": {
                            "type": "string",
                            "description": "Optional label for this metric (e.g. 'total_cost', 'p95_latency').",
                        },
                    },
                },
            },
            "fromTimestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Query window start, ISO 8601 (e.g. '2026-03-18T00:00:00Z'). Required.",
            },
            "toTimestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Query window end, ISO 8601 (e.g. '2026-03-25T23:59:59Z'). Required.",
            },
            "dimensions": {
                "type": "array",
                "description": (
                    "Fields to group results by. Example: [{\"field\": \"providedModelName\"}]. "
                    "Valid fields differ by view — see tool description. "
                    "id, traceId, observationId cannot be dimensions (use them in filters instead)."
                ),
                "items": {
                    "type": "object",
                    "required": ["field"],
                    "properties": {
                        "field": {"type": "string"},
                    },
                },
            },
            "filters": {
                "type": "array",
                "description": (
                    "Narrow records before aggregation. "
                    "CRITICAL: string operators are ONLY: =, contains, does not contain, starts with, ends with. "
                    "numeric/datetime operators are ONLY: =, <, >, <=, >=. "
                    "!=, not_contains, not_equals cause 400 errors on string fields."
                ),
                "items": {
                    "type": "object",
                    "required": ["column", "operator", "value", "type"],
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "Field to filter on (e.g. environment, userId, providedModelName, traceId).",
                        },
                        "operator": {
                            "type": "string",
                            "description": (
                                "Comparison operator. "
                                "For string/stringObject type: use ONLY =, contains, 'does not contain', 'starts with', 'ends with'. "
                                "For number/datetime type: use ONLY =, <, >, <=, >=. "
                                "Never use != or not_contains for string fields."
                            ),
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to compare against.",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["string", "number", "boolean", "stringObject", "datetime"],
                            "description": "Data type. Use 'stringObject' with 'key' for metadata filters.",
                        },
                        "key": {
                            "type": "string",
                            "description": "Only for type=stringObject: the metadata key to filter on.",
                        },
                    },
                },
            },
            "timeDimension": {
                "type": "object",
                "description": (
                    "Add time series axis to results. Omit for a single rolled-up total. "
                    "Include for trends (daily cost, hourly latency, etc.)."
                ),
                "required": ["granularity"],
                "properties": {
                    "granularity": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "auto"],
                        "description": "Time bucket size. Use 'auto' for Langfuse to decide based on range.",
                    },
                },
            },
            "sort_by": {
                "type": "object",
                "description": (
                    "CLIENT-SIDE sort applied after the API returns results. "
                    "Provide the exact field name as it appears in the response rows and a direction. "
                    "Do NOT use API-level orderBy — it causes 400 errors due to unpredictable field naming."
                ),
                "properties": {
                    "field": {
                        "type": "string",
                        "description": "Response row key to sort by. Inspect result rows to find valid keys.",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                    },
                },
                "required": ["field", "direction"],
            },
        },
    },
)


# ============================================================================
# TOOL IMPLEMENTATION
# ============================================================================

class GetCostMetricsTool(BaseLangfuseTool):
    """Query Langfuse Metrics API v1 — delegates all aggregation to the API."""

    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            view = args["view"]

            # ── 1. Validate view ──────────────────────────────────────────────
            if view not in VIEW_MEASURES:
                return json.dumps({
                    "error": f"Invalid view '{view}'.",
                    "supported_views": list(VIEW_MEASURES.keys()),
                })

            # ── 2. Validate measures ──────────────────────────────────────────
            valid_measures = VIEW_MEASURES[view]
            invalid_metrics = []
            for m in args.get("metrics", []):
                if m["measure"] not in valid_measures:
                    invalid_metrics.append({
                        "measure": m["measure"],
                        "reason": f"Not supported for view='{view}'.",
                        "valid_measures": valid_measures,
                        "hint": (
                            "inputTokens/outputTokens/promptTokens/completionTokens are NOT valid. "
                            "Use 'totalTokens' with aggregation='sum' instead."
                            if m["measure"] in (
                                "inputTokens", "outputTokens",
                                "promptTokens", "completionTokens"
                            ) else None
                        ),
                    })
            if invalid_metrics:
                return json.dumps({
                    "error": "Invalid metrics for the selected view.",
                    "invalid_metrics": invalid_metrics,
                })

            # ── 3. Validate dimensions ────────────────────────────────────────
            valid_dims = VIEW_DIMENSIONS.get(view, [])
            invalid_dims = []
            for d in args.get("dimensions", []):
                field = d["field"]
                if field in HIGH_CARDINALITY_FIELDS:
                    invalid_dims.append({
                        "field": field,
                        "reason": "High-cardinality — cannot group by this field. Use it in filters instead.",
                    })
                elif field not in valid_dims:
                    invalid_dims.append({
                        "field": field,
                        "reason": f"Not a valid dimension for view='{view}'.",
                        "valid_dimensions": valid_dims,
                    })
            if invalid_dims:
                return json.dumps({
                    "error": "Invalid dimensions for the selected view.",
                    "invalid_dimensions": invalid_dims,
                })

            # ── 4. Validate filter operators ──────────────────────────────────
            invalid_filters = []
            for i, f in enumerate(args.get("filters", [])):
                ftype = f.get("type", "string")
                op = f.get("operator", "")
                if ftype in ("string", "stringObject", "boolean"):
                    valid_ops = FILTER_OPERATORS_STRING
                elif ftype in ("number", "datetime"):
                    valid_ops = FILTER_OPERATORS_NUMERIC
                else:
                    valid_ops = FILTER_OPERATORS_STRING

                if op not in valid_ops:
                    invalid_filters.append({
                        "filter_index": i,
                        "column": f.get("column"),
                        "invalid_operator": op,
                        "valid_operators_for_type": valid_ops,
                        "hint": (
                            f"For type='{ftype}', valid operators are: {valid_ops}. "
                            "Note: '!=' and 'not_contains' are NOT supported for string fields."
                        ),
                    })
            if invalid_filters:
                return json.dumps({
                    "error": "Invalid filter operators detected.",
                    "invalid_filters": invalid_filters,
                })

            # ── 5. Build API query (no orderBy — causes 400s) ─────────────────
            query: Dict[str, Any] = {
                "view": view,
                "metrics": args["metrics"],
                "fromTimestamp": args["fromTimestamp"],
                "toTimestamp": args["toTimestamp"],
                "filters": args.get("filters", []),
            }
            if args.get("dimensions"):
                query["dimensions"] = args["dimensions"]
            if args.get("timeDimension"):
                query["timeDimension"] = args["timeDimension"]

            # ── 6. Call Metrics API ───────────────────────────────────────────
            self.logger.info("Fetching metrics", query=query)

            response = await self._fetch_with_retry(
                self.langfuse.api.legacy.metrics_v1.metrics,
                query=json.dumps(query),
            )

            # ── 7. Parse response — API returns plain dicts ───────────────────
            if not response or not response.data:
                return json.dumps({
                    "query": query,
                    "result": [],
                    "row_count": 0,
                    "summary": "No data returned for the given query parameters.",
                })

            data: List[Dict] = []
            for row in response.data:
                if isinstance(row, dict):
                    data.append(row)
                elif hasattr(row, "model_dump"):
                    data.append(row.model_dump())
                elif hasattr(row, "__dict__"):
                    data.append(row.__dict__)
                else:
                    data.append(str(row))

            # ── 8. Client-side sort (safe — operates on actual response keys) ──
            sort_by = args.get("sort_by")
            if sort_by and data:
                sort_field = sort_by["field"]
                reverse = sort_by["direction"] == "desc"
                if sort_field in (data[0] if data else {}):
                    try:
                        data = sorted(
                            data,
                            key=lambda r: float(r.get(sort_field) or 0),
                            reverse=reverse,
                        )
                    except (TypeError, ValueError):
                        data = sorted(
                            data,
                            key=lambda r: str(r.get(sort_field) or ""),
                            reverse=reverse,
                        )
                else:
                    # Tell the agent what fields are actually available
                    available_keys = list(data[0].keys()) if data else []
                    return json.dumps({
                        "query": query,
                        "result": data,
                        "row_count": len(data),
                        "sort_warning": (
                            f"sort_by field '{sort_field}' not found in response rows. "
                            f"Available fields: {available_keys}. "
                            "Results returned unsorted — retry with a valid field name."
                        ),
                    }, default=str)

            return json.dumps({
                "query": query,
                "result": data,
                "row_count": len(data),
            }, default=str)

        except Exception as e:
            self.logger.error("Error fetching metrics", error=str(e), error_type=type(e).__name__)
            return json.dumps({
                "error": str(e),
                "type": type(e).__name__,
                "hint": (
                    "Common causes: invalid measure for the view, unsupported filter operator "
                    "(string fields only accept: =, contains, 'does not contain', 'starts with', 'ends with'), "
                    "or high-cardinality field used as dimension."
                ),
            })