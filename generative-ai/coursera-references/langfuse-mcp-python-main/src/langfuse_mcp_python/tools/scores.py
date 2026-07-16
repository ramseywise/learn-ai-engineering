"""
Scores Tool - Get and Submit Evaluation Scores
CRITICAL: This was completely missing in the original implementation

Langfuse Scores are the core of evaluation-driven development:
- Track model quality over time
- Compare different prompt versions
- A/B test improvements
- Measure success metrics
"""

from typing import Any, Dict, Optional
from mcp.types import Tool
from langfuse.api.commons.types.score_data_type import ScoreDataType
from ..core.base_tool import BaseLangfuseTool


# ============================================================================
# TOOL SPEC - GET SCORES
# ============================================================================

GET_SCORES_TOOL_SPEC = Tool(
    name="get_scores",
    description=(
        "Retrieve evaluation scores for traces. "
        "Scores represent quality metrics like accuracy, relevance, helpfulness, etc. "
        "Use this to analyze agent quality, compare versions, and track improvements."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "trace_id": {
                "type": "string",
                "description": "Filter scores for a specific trace",
            },
            "observation_id": {
                "type": "string",
                "description": "Filter scores for a specific observation",
            },
            "score_name": {
                "type": "string",
                "description": "Filter by score name (e.g., 'accuracy', 'relevance', 'helpfulness')",
            },
            "data_type": {
                "type": "string",
                "enum": ["NUMERIC", "CATEGORICAL", "BOOLEAN"],
                "description": "Filter by score data type",
            },
            "operator": {
                "type": "string",
                "enum": ["gte", "lte", "eq", "gt", "lt"],
                "description": "Comparison operator for value filter",
            },
            "value": {
                "type": "number",
                "description": "Value to compare against (used with operator)",
            },
            "user_id": {
                "type": "string",
                "description": "Filter scores by user ID",
            },
            "from_timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Filter scores created after this timestamp",
            },
            "to_timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Filter scores created before this timestamp",
            },
            "limit": {
                "type": "integer",
                "default": 50,
                "minimum": 1,
                "maximum": 1000,
                "description": "Maximum number of scores to return",
            },
            "include_statistics": {
                "type": "boolean",
                "default": True,
                "description": "Include statistical summary (avg, min, max, distribution)",
            },
        },
    },
)


# ============================================================================
# TOOL SPEC - SUBMIT SCORE
# ============================================================================

SUBMIT_SCORE_TOOL_SPEC = Tool(
    name="submit_score",
    description=(
        "Submit an evaluation score for a trace or observation. "
        "Use this to programmatically add quality metrics, "
        "implement LLM-as-a-judge evaluations, or record user feedback."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Optional score ID (client-generated)"},
            "trace_id": {"type": "string", "description": "Trace ID to score"},
            "session_id": {"type": "string", "description": "Session ID to score"},
            "observation_id": {"type": "string", "description": "Observation ID to score"},
            "dataset_run_id": {"type": "string", "description": "Dataset run ID to score"},
            "name": {
                "type": "string",
                "description": "Score name (e.g., 'accuracy', 'relevance', 'quality')",
            },
            "value": {
                "description": "Score value (number for NUMERIC, string for CATEGORICAL, boolean for BOOLEAN)",
            },
            "data_type": {
                "type": "string",
                "enum": ["NUMERIC", "CATEGORICAL", "BOOLEAN"],
                "default": "NUMERIC",
                "description": "Type of score",
            },
            "comment": {
                "type": "string",
                "description": "Optional comment explaining the score",
            },
            "metadata": {"type": "object", "description": "Optional metadata"},
            "environment": {"type": "string", "description": "Optional environment label"},
            "queue_id": {"type": "string", "description": "Optional annotation queue ID"},
            "config_id": {"type": "string", "description": "Optional score config ID"},
        },
        "required": ["name", "value"],
    },
)


# ============================================================================
# TOOL IMPLEMENTATION - GET SCORES
# ============================================================================

class GetScoresTool(BaseLangfuseTool):
    """Retrieve evaluation scores with filtering and statistics"""

    async def execute(self, args: Dict[str, Any]) -> str:
        """Execute get_scores tool"""

        try:
            # Build filter parameters
            filters = {}

            if args.get("trace_id"):
                filters["trace_id"] = args["trace_id"]

            if args.get("observation_id"):
                filters["observation_id"] = args["observation_id"]

            if args.get("score_name"):
                filters["name"] = args["score_name"]

            if args.get("data_type"):
                filters["data_type"] = args["data_type"]

            if args.get("operator") and args.get("value") is not None:
                filters["operator"] = args["operator"]
                filters["value"] = args["value"]

            if args.get("user_id"):
                filters["user_id"] = args["user_id"]

            if args.get("from_timestamp"):
                filters["from_timestamp"] = args["from_timestamp"]

            if args.get("to_timestamp"):
                filters["to_timestamp"] = args["to_timestamp"]

            limit = args.get("limit", 50)

            # Fetch scores with retry
            self.logger.info("Fetching scores", filters=filters, limit=limit)

            # Langfuse SDK uses get_many() not list() for scores
            scores_response = await self._fetch_with_retry(
                lambda: self.langfuse.api.scores.get_many(
                    page=1,
                    limit=limit,
                    **filters
                )
            )

            if not scores_response.data:
                return "No scores found matching the criteria."

            # Calculate statistics if requested
            statistics = None
            if args.get("include_statistics", True):
                statistics = self._calculate_score_statistics(scores_response.data)

            # Format response
            response = self._format_scores_response(
                scores_response.data,
                statistics,
                filters
            )

            return response

        except Exception as e:
            self.logger.error("Error fetching scores", error=str(e))
            return f"Error fetching scores: {str(e)}"

    def _calculate_score_statistics(self, scores) -> Dict[str, Any]:
        """Calculate statistical summary of scores"""

        stats = {
            "total_count": len(scores),
            "by_name": {},
            "by_data_type": {},
        }

        # Group by score name
        for score in scores:
            name = score.name
            data_type = score.data_type

            # Count by name
            if name not in stats["by_name"]:
                stats["by_name"][name] = {
                    "count": 0,
                    "data_type": data_type,
                    "values": [],
                }

            stats["by_name"][name]["count"] += 1

            # Collect numeric values for statistics
            if data_type == "NUMERIC" and hasattr(score, "value"):
                stats["by_name"][name]["values"].append(float(score.value))

            # Count by data type
            stats["by_data_type"][data_type] = stats["by_data_type"].get(data_type, 0) + 1

        # Calculate numeric statistics
        for name, data in stats["by_name"].items():
            if data["values"]:
                values = sorted(data["values"])
                data["min"] = min(values)
                data["max"] = max(values)
                data["avg"] = sum(values) / len(values)
                data["median"] = values[len(values) // 2]
                del data["values"]  # Remove raw values from output

        return stats

    def _format_scores_response(
        self,
        scores,
        statistics: Optional[Dict],
        filters: Dict
    ) -> str:
        """Format scores into readable response"""

        response = "📊 **Evaluation Scores**\n\n"

        # Add filter info
        if filters:
            response += "**Filters Applied:**\n"
            for key, value in filters.items():
                response += f"  - {key}: {value}\n"
            response += "\n"

        # Add statistics
        if statistics:
            response += "**Summary:**\n"
            response += f"  - Total Scores: {statistics['total_count']}\n"

            if statistics["by_data_type"]:
                response += "  - By Type: "
                type_counts = [f"{dt}({count})" for dt, count in statistics["by_data_type"].items()]
                response += ", ".join(type_counts) + "\n"

            response += "\n"

            # Show statistics by score name
            if statistics["by_name"]:
                response += "**Score Statistics:**\n\n"
                for name, data in statistics["by_name"].items():
                    response += f"**{name}** ({data['data_type']}):\n"
                    response += f"  - Count: {data['count']}\n"

                    if "avg" in data:
                        response += f"  - Average: {data['avg']:.3f}\n"
                        response += f"  - Min: {data['min']:.3f}\n"
                        response += f"  - Max: {data['max']:.3f}\n"
                        response += f"  - Median: {data['median']:.3f}\n"

                    response += "\n"

        # Show individual scores (up to 20)
        response += f"**Individual Scores** (showing {min(len(scores), 20)} of {len(scores)}):\n\n"

        for i, score in enumerate(scores[:20], 1):
            response += f"{i}. **{score.name}**: {score.value} ({score.data_type})\n"

            if hasattr(score, "trace_id") and score.trace_id:
                response += f"   - Trace: {score.trace_id[:12]}...\n"

            if hasattr(score, "observation_id") and score.observation_id:
                response += f"   - Observation: {score.observation_id[:12]}...\n"

            if hasattr(score, "timestamp"):
                response += f"   - Created: {self._format_datetime(score.timestamp)}\n"

            if hasattr(score, "comment") and score.comment:
                response += f"   - Comment: {score.comment}\n"

            response += "\n"

        if len(scores) > 20:
            response += f"... and {len(scores) - 20} more scores\n"

        return response


# ============================================================================
# TOOL IMPLEMENTATION - SUBMIT SCORE
# ============================================================================

class SubmitScoreTool(BaseLangfuseTool):
    """Submit evaluation scores programmatically"""

    async def execute(self, args: Dict[str, Any]) -> str:
        """Execute submit_score tool"""

        try:
            if not args.get("name"):
                return "Error: score name is required"

            if "value" not in args:
                return "Error: score value is required"

            # Prepare score data (matches POST /api/public/scores)
            score_data = {
                "id": args.get("id"),
                "trace_id": args.get("trace_id"),
                "session_id": args.get("session_id"),
                "observation_id": args.get("observation_id"),
                "dataset_run_id": args.get("dataset_run_id"),
                "name": args["name"],
                "value": args["value"],
                "data_type": args.get("data_type", "NUMERIC"),
                "comment": args.get("comment"),
                "metadata": args.get("metadata"),
                "environment": args.get("environment"),
                "queue_id": args.get("queue_id"),
                "config_id": args.get("config_id"),
            }

            # Submit score with retry via legacy score_v1 endpoint
            self.logger.info("Submitting score", score_data=score_data)

            score = await self._fetch_with_retry(
                lambda: self.langfuse.api.legacy.score_v1.create(
                    id=score_data.get("id"),
                    trace_id=score_data.get("trace_id"),
                    session_id=score_data.get("session_id"),
                    observation_id=score_data.get("observation_id"),
                    dataset_run_id=score_data.get("dataset_run_id"),
                    name=score_data["name"],
                    value=score_data["value"],
                    comment=score_data.get("comment"),
                    metadata=score_data.get("metadata"),
                    environment=score_data.get("environment"),
                    queue_id=score_data.get("queue_id"),
                    data_type=ScoreDataType(score_data.get("data_type", "NUMERIC")),
                    config_id=score_data.get("config_id"),
                )
            )

            response = "✅ **Score Submitted Successfully**\n\n"
            response += "**Score Details:**\n"
            response += f"  - Name: {score_data['name']}\n"
            response += f"  - Value: {score_data['value']}\n"
            response += f"  - Type: {score_data.get('data_type', 'NUMERIC')}\n"
            if score_data.get("trace_id"):
                response += f"  - Trace ID: {score_data['trace_id']}\n"
            if score_data.get("session_id"):
                response += f"  - Session ID: {score_data['session_id']}\n"
            if score_data.get("observation_id"):
                response += f"  - Observation ID: {score_data['observation_id']}\n"
            if score_data.get("dataset_run_id"):
                response += f"  - Dataset Run ID: {score_data['dataset_run_id']}\n"
            if hasattr(score, "id"):
                response += f"  - Score ID: {score.id}\n"
            if args.get("comment"):
                response += f"  - Comment: {args['comment']}\n"

            return response

        except Exception as e:
            self.logger.error("Error submitting score", error=str(e))
            return f"Error submitting score: {str(e)}"
