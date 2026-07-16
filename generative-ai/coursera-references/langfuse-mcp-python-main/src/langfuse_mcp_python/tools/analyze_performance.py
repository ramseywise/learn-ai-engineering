"""
Enhanced Analyze Performance Tool
Uses Observations v1 API directly (no Metrics API, no v2).
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from mcp.types import Tool
from ..core.base_tool import BaseLangfuseTool
ANALYZE_PERFORMANCE_TOOL_SPEC = Tool(
    name="analyze_performance",
    description="Analyze agent performance by aggregating observations directly (no Metrics API).",
    inputSchema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string"},
            "time_window": {
                "type": "string",
                "enum": ["last_1h", "last_24h", "last_7d", "last_10d"],
                "description": "Convenience time window (used if time_range not provided).",
            },
            "time_range": {
                "type": "object",
                "properties": {
                    "from": {"type": "string", "format": "date-time"},
                    "to": {"type": "string", "format": "date-time"},
                },
            },
            "group_by": {
                "type": "string",
                "enum": ["hour", "day", "model", "user"],
                "default": "day",
            },
            "breakdown_by": {
                "type": "string",
                "enum": ["observation_name", "model", "trace_id", "user_id"],
                "default": "observation_name",
            },
            "top_n": {"type": "integer", "default": 5},
            "include_tokens": {"type": "boolean", "default": True},
        },
    },
)

class AnalyzePerformanceTool(BaseLangfuseTool):
    async def execute(self, args: Dict[str, Any]) -> str:
        try:
            # Use Observations API directly (no Metrics API)
            agent_name = args.get("agent_name")
            
            # Resolve time range
            time_range = args.get("time_range")
            if not time_range and args.get("time_window"):
                hours_map = {"last_1h": 1, "last_24h": 24, "last_7d": 168, "last_10d": 240}
                hours = hours_map.get(args["time_window"], 24)
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(hours=hours)
                time_range = {
                    "from": start_time.isoformat(),
                    "to": end_time.isoformat(),
                }
            if not time_range:
                # Default to last 7 days to avoid unbounded scans
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(hours=168)
                time_range = {
                    "from": start_time.isoformat(),
                    "to": end_time.isoformat(),
                }
            
            include_tokens = args.get("include_tokens", True)

            # --- Breakdown selection ---
            if "breakdown_by" in args and args.get("breakdown_by"):
                breakdown_by = args.get("breakdown_by")
            else:
                group_by_fallback = args.get("group_by")
                if group_by_fallback == "model":
                    breakdown_by = "model"
                elif group_by_fallback == "user":
                    breakdown_by = "user_id"
                else:
                    breakdown_by = "observation_name"
            
            response = f"[OBS] **Performance Analysis**\n\n"
            
            if agent_name:
                response += f"**Agent**: {agent_name} (note: observations API does not support tag filtering here)\n"
            
            if time_range:
                response += f"**Time Range**: {time_range.get('from', 'start')} to {time_range.get('to', 'now')}\n"
            response += "**Source**: observations\n"
            
            response += "\n**Totals (All Observations)**\n"
            obs_totals, obs_groups, obs_token_groups = await self._aggregate_from_observations(
                time_range=time_range,
                include_tokens=include_tokens,
                breakdown_by=breakdown_by,
                top_n=int(args.get("top_n", 5)),
            )
            observation_count = obs_totals.get("observation_count", 0)
            total_cost = obs_totals.get("total_cost", 0.0)
            total_tokens = obs_totals.get("total_tokens", 0)
            
            response += f"- Observations: {int(observation_count):,}\n"
            response += f"- Total Cost: {self._format_cost(float(total_cost))}\n"
            if include_tokens:
                response += f"- Total Tokens: {int(total_tokens):,}\n"
            
            # Breakdown section
            response += f"\n**Top by {breakdown_by.replace('_', ' ')}**\n"
            response += "Top Cost Items:\n"
            for idx, (label, cost, tokens) in enumerate(obs_groups, 1):
                line = f"{idx}. {label} | Cost: {self._format_cost(float(cost))}"
                if include_tokens:
                    line += f" | Tokens: {int(tokens):,}"
                response += line + "\n"
            
            if include_tokens:
                response += "Top Token Items:\n"
                for idx, (label, tokens, cost) in enumerate(obs_token_groups, 1):
                    line = f"{idx}. {label} | Tokens: {int(tokens):,} | Cost: {self._format_cost(float(cost))}"
                    response += line + "\n"
            
            return response
        except Exception as e:
            return f"Error analyzing performance: {str(e)}"

    async def _aggregate_from_observations(
        self,
        time_range: Optional[Dict[str, str]],
        include_tokens: bool,
        breakdown_by: str,
        top_n: int,
    ) -> tuple[Dict[str, Any], List[tuple], List[tuple]]:
        observations = await self._fetch_all_observations_v1(time_range=time_range)
        
        total_cost = 0.0
        total_tokens = 0
        cost_by_key: Dict[str, float] = {}
        tokens_by_key: Dict[str, int] = {}
        
        for obs in observations:
            cost = self._extract_observation_cost(obs)
            tokens = self._extract_observation_tokens(obs)
            total_cost += cost
            if include_tokens:
                total_tokens += tokens
            
            key = self._extract_observation_key(obs, breakdown_by)
            cost_by_key[key] = cost_by_key.get(key, 0.0) + cost
            if include_tokens:
                tokens_by_key[key] = tokens_by_key.get(key, 0) + tokens
        
        top_n = max(1, int(top_n))
        top_cost_items = sorted(cost_by_key.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_token_items = sorted(tokens_by_key.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        top_cost_render = []
        for key, cost in top_cost_items:
            top_cost_render.append((key, cost, tokens_by_key.get(key, 0)))
        
        top_token_render = []
        for key, tokens in top_token_items:
            top_token_render.append((key, tokens, cost_by_key.get(key, 0.0)))
        
        totals = {
            "observation_count": len(observations),
            "total_cost": total_cost,
            "total_tokens": total_tokens,
        }
        return totals, top_cost_render, top_token_render

    async def _fetch_all_observations_v1(
        self,
        time_range: Optional[Dict[str, str]],
        limit: int = 100,
        max_pages: int = 1000,
    ) -> List[Any]:
        page = 1
        all_items: List[Any] = []
        
        while page <= max_pages:
            response = await self._fetch_with_retry(
                self._fetch_observations_v1_page,
                page=page,
                limit=limit,
                time_range=time_range,
            )
            
            data = response.get("data", []) if isinstance(response, dict) else []
            if not data:
                break
            
            all_items.extend(data)
            
            meta = response.get("meta", {}) if isinstance(response, dict) else {}
            total_pages = meta.get("totalPages") or meta.get("total_pages")
            if total_pages is not None and page >= int(total_pages):
                break
            
            # If totalPages is missing, stop when fewer than limit returned
            if total_pages is None and len(data) < limit:
                break
            
            page += 1
        
        return all_items

    def _fetch_observations_v1_page(
        self,
        *,
        page: int,
        limit: int,
        time_range: Optional[Dict[str, str]],
    ) -> Dict[str, Any]:
        client_wrapper = self.langfuse.client.api._client_wrapper
        params: Dict[str, Any] = {
            "page": page,
            "limit": limit,
        }
        
        if time_range:
            if time_range.get("from"):
                params["fromTimestamp"] = time_range["from"]
                params["fromStartTime"] = time_range["from"]
            if time_range.get("to"):
                params["toTimestamp"] = time_range["to"]
                params["toStartTime"] = time_range["to"]
        
        response = client_wrapper.httpx_client.request(
            "api/public/observations",
            method="GET",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _extract_observation_cost(obs: Any) -> float:
        for key in ("total_cost", "totalCost", "calculated_total_cost", "calculatedTotalCost"):
            if hasattr(obs, key):
                val = getattr(obs, key)
                if val is not None:
                    return float(val)
            if isinstance(obs, dict) and key in obs and obs[key] is not None:
                return float(obs[key])
        
        # costDetails.total
        cost_details = None
        if hasattr(obs, "costDetails"):
            cost_details = getattr(obs, "costDetails")
        elif isinstance(obs, dict):
            cost_details = obs.get("costDetails")
        if isinstance(cost_details, dict):
            total = cost_details.get("total")
            if total is not None:
                return float(total)
        
        # calculatedInputCost + calculatedOutputCost
        input_cost = None
        output_cost = None
        if hasattr(obs, "calculatedInputCost"):
            input_cost = getattr(obs, "calculatedInputCost")
        elif isinstance(obs, dict):
            input_cost = obs.get("calculatedInputCost")
        if hasattr(obs, "calculatedOutputCost"):
            output_cost = getattr(obs, "calculatedOutputCost")
        elif isinstance(obs, dict):
            output_cost = obs.get("calculatedOutputCost")
        if input_cost is not None or output_cost is not None:
            return float(input_cost or 0) + float(output_cost or 0)
        
        return 0.0

    @staticmethod
    def _extract_observation_tokens(obs: Any) -> int:
        for key in ("total_tokens", "totalTokens"):
            if hasattr(obs, key):
                val = getattr(obs, key)
                if val is not None:
                    return int(val)
            if isinstance(obs, dict) and key in obs and obs[key] is not None:
                return int(obs[key])
        
        usage = None
        if hasattr(obs, "usage"):
            usage = getattr(obs, "usage")
        elif isinstance(obs, dict):
            usage = obs.get("usage")
        if isinstance(usage, dict):
            total = usage.get("total")
            if total is not None:
                return int(total)
        
        usage_details = None
        if hasattr(obs, "usageDetails"):
            usage_details = getattr(obs, "usageDetails")
        elif isinstance(obs, dict):
            usage_details = obs.get("usageDetails")
        if isinstance(usage_details, dict):
            total = usage_details.get("total")
            if total is not None:
                return int(total)
        
        prompt_tokens = 0
        completion_tokens = 0
        if hasattr(obs, "promptTokens"):
            prompt_tokens = getattr(obs, "promptTokens") or 0
        elif isinstance(obs, dict):
            prompt_tokens = obs.get("promptTokens") or 0
        if hasattr(obs, "completionTokens"):
            completion_tokens = getattr(obs, "completionTokens") or 0
        elif isinstance(obs, dict):
            completion_tokens = obs.get("completionTokens") or 0
        if prompt_tokens or completion_tokens:
            return int(prompt_tokens) + int(completion_tokens)
        
        return 0

    @staticmethod
    def _extract_observation_key(obs: Any, breakdown_by: str) -> str:
        if breakdown_by == "observation_name":
            if hasattr(obs, "name"):
                return getattr(obs, "name") or "unknown"
            if isinstance(obs, dict):
                return obs.get("name") or "unknown"
        if breakdown_by == "model":
            if hasattr(obs, "model") and getattr(obs, "model"):
                return getattr(obs, "model")
            if isinstance(obs, dict) and obs.get("model"):
                return obs.get("model")
            # Attempt to read from metadata attributes
            metadata = obs.get("metadata") if isinstance(obs, dict) else getattr(obs, "metadata", None)
            if isinstance(metadata, dict):
                attributes = metadata.get("attributes", {})
                if isinstance(attributes, dict):
                    return attributes.get("gen_ai.response.model") or attributes.get("gen_ai.request.model") or "unknown"
        if breakdown_by == "trace_id":
            if hasattr(obs, "traceId") and getattr(obs, "traceId"):
                return getattr(obs, "traceId")
            if isinstance(obs, dict):
                return obs.get("traceId") or "unknown"
        if breakdown_by == "user_id":
            if hasattr(obs, "userId") and getattr(obs, "userId"):
                return getattr(obs, "userId")
            if isinstance(obs, dict):
                return obs.get("userId") or "unknown"
        return "unknown"
