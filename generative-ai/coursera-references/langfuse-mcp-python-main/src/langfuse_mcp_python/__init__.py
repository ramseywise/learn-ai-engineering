"""
Multi-Agent Monitoring MCP Server

A Model Context Protocol (MCP) server for comprehensive monitoring
and observability of multi-agent systems using Langfuse.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import EnhancedLangfuseMonitoringServer, main

__all__ = ["EnhancedLangfuseMonitoringServer", "main"]
