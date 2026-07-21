# Internet Search Agent

This repository contains a sophisticated AI-powered search agent implementation that can crawl the internet for information and create detailed reports. The agent supports two main modes: simple search queries and comprehensive workflow-based report generation.

## ✨ Features

- **Two Agent Types**:
  - **Simple Search Agent**: Quick answers to sustainability-focused questions with web search integration
  - **Workflow Agent**: Comprehensive report generation with structured outlines and multi-section analysis

- **Web Search Integration**:
  - Bing Search API integration for real-time information retrieval
  - Intelligent search query formulation based on context
  - Retry logic with query refinement for better results

- **Content Crawling**:
  - Optional web crawling using crawl4ai for detailed content extraction
  - Full webpage content analysis beyond search snippets

- **Persistence Support**:
  - PostgreSQL for production environments
  - SQLite for local development
  - In-memory for LangGraph Studio development

- **FastAPI REST API**:
  - Complete API with chat endpoints, history management, and agent status
  - CORS-enabled for web application integration
  - Background task support for long-running operations

## 🏗️ Project Structure

```txt
src/
├── clients/                 # External service clients
│   ├── llm_client.py       # Azure OpenAI client
│   └── search_client.py    # Bing Search client
├── graphs/                 # LangGraph agent implementations
│   ├── simple_search_agent.py    # Quick Q&A agent
│   ├── workflow_agent.py         # Report generation agent
│   └── get_agents.py            # Agent selection and management
├── models/                 # Pydantic schemas
│   ├── chat_schemas.py     # Chat and message models
│   ├── history_schemas.py  # History-related models
│   ├── search_schemas.py   # Search result models
│   ├── state_schemas.py    # Agent state models
│   └── schemas.py          # General schemas
├── routes/                 # FastAPI route handlers
│   ├── chat_route.py       # Chat endpoints
│   ├── health_route.py     # Health check
│   ├── history_route.py    # Chat history
│   ├── info_route.py       # Service metadata
│   ├── status_route.py     # Agent state inspection
│   └── threads_route.py    # Thread management
├── services/               # Business logic services
│   └── state_parser.py     # State history parsing
├── config.py              # Environment configuration
├── main.py                # FastAPI application
├── persistence.py         # Database checkpointer setup
└── utils.py               # Utility functions
```

## 🔧 Installation Guide

### Prerequisites

- Python 3.11+
- UV package manager
- Azure OpenAI account with API access
- Bing Search API subscription

### Setup the environment

#### Working with uv

- [ ] Clone the repository and navigate to the project directory
- [ ] Sync dependencies with `uv sync`
- [ ] Install `pre-commit` with `uv run pre-commit install`
- [ ] Add your dependencies with `uv add ...`
- [ ] Add your development dependencies with `uv add --dev ...`
- [ ] Remove unneeded dependencies with `uv remove ...`
- [ ] Run ruff with `uv run ruff check --fix`

### 🌍 Environment Variables

Create a `.env` file in the root directory with the following variables:

#### Required Variables

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Bing Search Configuration  
BING_SUBSCRIPTION_KEY=your_bing_subscription_key
BING_SEARCH_URL=https://api.bing.microsoft.com/v7.0/search  # Optional, uses default if not set
```

#### Optional Variables

```bash
# Database Configuration (choose one)
POSTGRES_URI=postgresql://user:password@localhost:5432/dbname?sslmode=disable
SQLITE_DB_LOCAL_PATH=state_db/example.db

# Web Crawler Configuration (optional)
CRAWLER_URL=http://localhost:11235  # crawl4ai service URL

# Agent Configuration
DEFAULT_AGENT=simple-search  # Options: simple-search, workflow
```

#### Running the application

1. Activate your virtual environment
2. Run langgraph studio with:

```bash
langgraph dev
```

### Checkpointer Configuration

The application supports different persistence methods based on your environment configuration:

* **PostgreSQL**: Used when the `POSTGRES_URI` environment variable is set.
* **SQLite**: Used when the `SQLITE_DB_LOCAL_PATH` environment variable is set.
* **No Checkpointer**: If neither of the above variables is set, no persistence is used (useful for LangGraph Studio).

#### For LangGraph Studio development:

```bash
# Make sure neither POSTGRES_URI nor SQLITE_DB_LOCAL_PATH are set
unset POSTGRES_URI
unset SQLITE_DB_LOCAL_PATH

# Then run LangGraph Studio
langgraph dev
```

#### For local development with SQLite:

```bash
# Set the SQLite URI
export SQLITE_DB_LOCAL_PATH=state_db/example.db

# Then run your application
uvicorn src.main:app --reload
```

#### For production with PostgreSQL:

```bash
# Set the PostgreSQL connection string
export POSTGRES_URI="postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable"

# Then run your application
uvicorn src.main:app --reload
```

The checkpointer configuration is handled by `src.persistence.get_checkpointer()`, which returns the appropriate saver based on these environment variables.

### Installing Graphviz on macOS ARM

I encountered some issues with Graphviz on macOS ARM. Here's the solution:

1. Install Graphviz via Homebrew:

    ```bash
    brew install graphviz
    ```

2. Build pygraphviz with uv, specifying the compiler flags:

    ```bash
    CFLAGS="-I$(brew --prefix graphviz)/include" \
    LDFLAGS="-L$(brew --prefix graphviz)/lib" \
    uv pip install pygraphviz
    ```

### Setting up crawl4ai (Optional)

To set up the crawl4ai web crawler for enhanced content extraction:

```bash
# Pull the Docker image
docker pull unclecode/crawl4ai:latest

# Run the container
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
```

Then set the `CRAWLER_URL` environment variable to `http://localhost:11235`.

## 🚀 Running the Application

### Development Mode

```bash
# Start the FastAPI server
fastapi dev src/main.py
```

### Production Mode

```bash
# Start with production settings
fastapi run src/main.py
```

## 🤖 Available Agents

### Simple Search Agent (`simple-search`)

- **Purpose**: Quick Q&A with web search integration
- **Best for**: Specific questions requiring current information
- **Process**: Decision → Search (if needed) → Answer
- **Example**: "What are the latest carbon capture technologies?"

### Workflow Agent (`workflow`)

- **Purpose**: Comprehensive report generation
- **Best for**: In-depth analysis and multi-section reports
- **Process**: Decision → Plan Outline → Search per Section → Draft Sections → Compile Report
- **Example**: "Create a comprehensive report on sustainability in the automotive industry"

## 🧪 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test categories
uv run pytest tests/test_routes.py  # API tests
uv run pytest tests/test_graphs.py  # Agent tests
uv run pytest tests/test_models.py  # Schema tests

# Run tests with verbose output
uv run pytest -v

# Run integration tests only
uv run pytest -m "not unit"
```

### Test Structure

```txt
tests/
├── test_routes.py     # FastAPI endpoint tests
├── test_graphs.py     # Agent workflow tests
├── test_models.py     # Pydantic schema tests
├── conftest.py        # Test fixtures and configuration
└── qna.md            # Test conversation examples
```

### Test Categories

- **Unit Tests**: Individual function and component testing
- **Integration Tests**: Full agent workflow testing
- **API Tests**: FastAPI endpoint testing with mocked dependencies
- **Schema Tests**: Pydantic model validation testing

## 🛠️ Development Tools

### Debugging LangGraph Studio

To debug LangGraph Studio:

1. Start LangGraph in debug mode:

    ```bash
    langgraph dev --debug-port 5678 --allow-blocking
    ```

2. Run the VSCode debugger with the appropriate configuration.

### Outputting requirements.txt when using uv

This is needed for langgraph studio:

```bash
uv export --format requirements-txt > requirements.txt
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code  
uv run ruff check --fix

# Type checking
uv run mypy src/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Development Workflow

1. Install dependencies: `uv sync`
2. Install pre-commit hooks: `uv run pre-commit install`
3. Make your changes
4. Run tests: `uv run pytest`
5. Check code quality: `uv run ruff check --fix`
6. Commit and push
