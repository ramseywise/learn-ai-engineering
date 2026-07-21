"""Output formatting utilities"""

from typing import Dict, Any


def format_trace(trace, depth: str = "full") -> str:
    """Format a trace for display"""
    output = f"""
🔍 **Trace Details**

**ID**: {trace.id}
**Agent**: {trace.metadata.get('agent_name', 'unknown')}
**Session**: {trace.session_id or 'N/A'}
**Timestamp**: {trace.timestamp.isoformat()}
"""
    return output


def format_performance_report(metrics: Dict[str, Any]) -> str:
    """Format performance metrics as a report"""
    return f"""
📈 **Performance Report**

**Total Runs**: {metrics.get('total_traces', 0)}
**Avg Latency**: {metrics.get('avg_latency_ms', 0):.0f}ms
**Total Cost**: ${metrics.get('total_cost', 0):.4f}
**Error Rate**: {metrics.get('error_rate', 0)*100:.2f}%
"""


def format_cost_breakdown(costs: Dict[str, float]) -> str:
    """Format cost breakdown"""
    output = "💰 **Cost Breakdown**\n\n"
    for entity, cost in costs.items():
        output += f"- {entity}: ${cost:.4f}\n"
    return output
