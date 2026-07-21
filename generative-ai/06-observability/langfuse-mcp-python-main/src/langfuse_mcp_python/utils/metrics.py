"""Metrics calculation utilities"""

from typing import Dict, Any, List
from datetime import datetime


def calculate_metrics(trace) -> Dict[str, Any]:
    """Calculate metrics for a single trace"""
    metrics = {
        "latency_ms": 0,
        "tokens": 0,
        "cost": 0.0,
        "observation_count": 0
    }
    
    # Calculate latency if timestamps available
    if hasattr(trace, 'timestamp') and hasattr(trace, 'end_time'):
        if trace.end_time:
            delta = trace.end_time - trace.timestamp
            metrics["latency_ms"] = delta.total_seconds() * 1000
    
    return metrics


def aggregate_metrics(traces: List) -> Dict[str, Any]:
    """Aggregate metrics across multiple traces"""
    if not traces:
        return {
            "total_traces": 0,
            "avg_latency_ms": 0,
            "total_cost": 0,
            "total_tokens": 0,
            "error_rate": 0
        }
    
    total_latency = 0
    total_cost = 0
    total_tokens = 0
    errors = 0
    
    for trace in traces:
        metrics = calculate_metrics(trace)
        total_latency += metrics.get("latency_ms", 0)
        total_cost += metrics.get("cost", 0)
        total_tokens += metrics.get("tokens", 0)
        
        if hasattr(trace, 'level') and trace.level == "ERROR":
            errors += 1
    
    return {
        "total_traces": len(traces),
        "avg_latency_ms": total_latency / len(traces),
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "error_rate": errors / len(traces)
    }


def calculate_observation_duration(observation) -> float:
    """Calculate duration of an observation in milliseconds"""
    if hasattr(observation, 'start_time') and hasattr(observation, 'end_time'):
        if observation.start_time and observation.end_time:
            delta = observation.end_time - observation.start_time
            return delta.total_seconds() * 1000
    return 0.0
