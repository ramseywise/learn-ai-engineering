# Monitoring and observability MCP Server

A Model Context Protocol (MCP) server for comprehensive monitoring and observability of systems using Langfuse.

## 🎯 What This Does

This MCP server allows you to:

- **Monitor** all your agents in real-time
- **Track** performance metrics (latency, cost, token usage)
- **Debug** failed executions with detailed traces
- **Analyze** agent performance across time periods
- **Compare** different agent versions via metadata filters
- **Manage** costs and set budget alerts
- **Visualize** agent workflows

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- A Langfuse account ([sign up here](https://langfuse.com))
- agents instrumented with Langfuse

### 2. Installation

```bash
# Install via pip
pip install -r requirements.txt

# Or install from source
git clone https://github.com/yourusername/langfuse-mcp-python.git
cd langfuse-mcp-python
pip install -e .
```

### 3. Configuration

Create a `.env` file with your Langfuse credentials:

```bash
cp .env.example .env
# Edit .env and add your credentials
```

Your `.env` should look like:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 4. Run As Streamable HTTP (URL)

If you want a Streamable HTTP URL that works across all tools, run the server with the Streamable HTTP transport:

```bash
python -m langfuse_mcp_python --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

```bash
python -m langfuse_mcp_python --transport sse --host 127.0.0.1 --port 8000
```

You can then connect any Streamable HTTP-compatible MCP client to:

```
http://127.0.0.1:8000/mcp
```

If you are using Claude Desktop or Cursor, keep the default `stdio` transport in their configs.

### 4b. Set Up MCP Client

#### For Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "langfuse-monitor": {
      "command": "uvx",
      "args": ["--python", "3.11", "langfuse-mcp-python"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-xxxxx",
        "LANGFUSE_SECRET_KEY": "sk-lf-xxxxx",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  }
}
```

#### For Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "langfuse-monitor": {
      "command": "python",
      "args": ["-m", "langfuse_mcp_python"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-xxxxx",
        "LANGFUSE_SECRET_KEY": "sk-lf-xxxxx"
      }
    }
  }
}
```

### 5. Instrument Your Agents

Make sure your agents send traces to Langfuse:

```python
from langfuse.langchain import CallbackHandler
from langgraph.graph import StateGraph

# Create Langfuse callback handler
langfuse_handler = CallbackHandler(
    public_key="pk-lf-xxxxx",
    secret_key="sk-lf-xxxxx",
    host="https://cloud.langfuse.com"
)

# Create your agent
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
app = workflow.compile()

# Run with Langfuse monitoring
result = app.invoke(
    {"input": "user query"},
    config={
        "callbacks": [langfuse_handler],
        "metadata": {
            "agent_name": "my_planner_agent",
            "version": "v1.0"
        }
    }
)
```

## Project Structure

- `src/langfuse_mcp_python/server.py` CLI entrypoint and stdio transport
- `src/langfuse_mcp_python/http_server.py` Streamable HTTP and SSE transport
- `src/langfuse_mcp_python/utils/tool_registry.py` Tool setup and registration
- `src/langfuse_mcp_python/tools/` Tool implementations and specs
- `src/langfuse_mcp_python/integrations/langfuse_client.py` Langfuse API client
- `src/langfuse_mcp_python/core/base_tool.py` Shared cache and metrics

## Available Tools

### Monitoring and Analytics

- `watch_agents` Monitor active agents
- `get_trace` Fetch a trace by ID
- `analyze_performance` Aggregate performance over time
- `get_metrics` Aggregate metrics (latency, cost, tokens)

### Scores and Evaluation

- `get_scores` Fetch scores
- `submit_score` Create a score
- `get_score_configs` List score configurations

### Prompts

- `get_prompts` List prompts
- `create_prompt` Create a prompt
- `delete_prompt` Delete a prompt

### Sessions

- `get_sessions` List sessions

### Datasets

- `get_datasets` List datasets
- `create_dataset` Create a dataset
- `create_dataset_item` Add an item to a dataset

### Models

- `get_models` List models
- `create_model` Create a model
- `delete_model` Delete a model

### Comments

- `get_comments` List comments
- `add_comment` Add a comment

### Traces

- `delete_trace` Delete a trace

### Annotation Queues

- `get_annotation_queues` List annotation queues
- `create_annotation_queue` Create a queue
- `get_queue_items` List queue items
- `resolve_queue_item` Resolve a queue item

### Blob Storage Integrations

- `get_blob_storage_integrations` List integrations
- `upsert_blob_storage_integration` Create or update an integration
- `get_blob_storage_integration_status` Fetch integration status
- `delete_blob_storage_integration` Delete an integration

### LLM Connections

- `get_llm_connections` List connections
- `upsert_llm_connection` Create or update a connection

### Projects

- `get_projects` List projects
- `create_project` Create a project
- `update_project` Update a project
- `delete_project` Delete a project

### Example: `watch_agents`

Monitor all active agents in real-time.

**Example:**
```
Show me all active agents from the last hour
```

**Response:**
```
Active Agent Monitoring (last_1h)

Total Traces Found: 15
Showing: Top 10 traces

1. research_agent (Trace: trace-abc12...)
   - Status: completed
   - Session: session-xyz
   - Started: 2026-03-19T10:25:00Z
   - Latency: 1250ms
   - Tokens: 3420
   - Cost: $0.0234
```

## Advanced Usage

### Filtering Agents

```
Watch only my research_agent and planner_agent from the last 24 hours
```

### Performance Analysis

```
Analyze performance of my planner_agent over the last 24 hours
```

### Cost Monitoring

```
Show cost breakdown by agent for the last week
```

### Deep Debugging

```
Show trace details for trace-abc123
```

## Architecture

```
MCP Client (Claude, Cursor, etc.)
  -> Langfuse MCP Server (stdio/HTTP)
  -> Langfuse API
  -> Langfuse Platform
  -> Your Langfuse Agents
```

## Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Rotate API keys** regularly
3. **Use read-only keys** where possible
4. **Enable rate limiting** in production
5. **Mask sensitive data** in traces

## Example Monitoring Workflow

### Daily Agent Health Check

1. Check active agents: `watch_agents`
2. Review performance: `analyze_performance`
3. Check costs: `get_metrics`
4. Investigate failures: `get_trace`

### Agent Optimization Cycle

1. Establish baseline: `analyze_performance` for current version metadata
2. Deploy new version with different metadata
3. Compare versions by running `analyze_performance` with version filters
4. Make data-driven deployment decisions

### Cost Control

1. Track costs: `get_metrics` grouped by agent
2. Identify expensive agents
3. Optimize high-cost operations
4. Track savings over time

## Troubleshooting

### MCP Server Not Connecting

1. Check environment variables are set correctly
2. Verify Langfuse API keys are valid
3. Ensure Python 3.11+ is installed
4. Check logs: `tail -f ~/.mcp/logs/langfuse-monitor.log`

### No Traces Found

1. Verify agents are instrumented with Langfuse
2. Check `langfuse_handler` is passed to agent invocations
3. Ensure metadata includes `agent_name`
4. Verify time window is appropriate

### High Latency

1. Reduce number of traces fetched (use filters)
2. Enable caching: `CACHE_ENABLED=true`
3. Use "minimal" depth for trace details
4. Consider batch processing for large datasets

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Langfuse](https://langfuse.com) - Open-source LLM observability
- [LangGraph](https://python.langchain.com/docs/langgraph) - Agent framework
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification

## Roadmap

- [x] Core monitoring tools
- [x] Performance analysis
- [x] Cost tracking
- [x] Debugging utilities
- [ ] Real-time streaming updates
- [ ] Custom alert system
- [ ] Predictive analytics
- [ ] A/B testing support
- [ ] Multi-project support
- [ ] Export to data warehouses

---

**Version**: 1.0.0  
**Last Updated**: March 23, 2026  
**Status**: Production Ready
