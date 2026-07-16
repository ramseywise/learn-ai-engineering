# Contributing to Monitoring MCP

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit bug fixes
- ✨ Add new features
- 🧪 Write tests

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/langfuse-mcp-python.git
cd langfuse-mcp-python
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

### Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Update README.md if adding features
- Add examples for new functionality

Example:

```python
def fetch_agent_traces(agent_name: str, limit: int = 100) -> List[Trace]:
    """
    Fetch traces for a specific agent.
    
    Args:
        agent_name: Name of the agent to fetch traces for
        limit: Maximum number of traces to return (default: 100)
    
    Returns:
        List of trace objects
    
    Raises:
        ValueError: If agent_name is empty
        LangfuseError: If API request fails
    
    Example:
        >>> traces = fetch_agent_traces("research_agent", limit=50)
        >>> print(len(traces))
        50
    """
    pass
```

### 2. Commit Messages

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```bash
git commit -m "feat(tools): add compare_agent_versions tool"
git commit -m "fix(metrics): correct latency calculation"
git commit -m "docs(readme): update installation instructions"
```

### 3. Submit Pull Request

1. Push your branch: `git push origin feature/your-feature-name`
2. Go to GitHub and create a Pull Request
3. Fill out the PR template
4. Link any related issues
5. Wait for review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Added tests
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No breaking changes (or documented)

## Related Issues
Fixes #123
```

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try the latest version
3. Collect relevant information

### Bug Report Template

```markdown
**Describe the Bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Run '...'
3. See error

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., macOS 13.0]
- Python: [e.g., 3.11.5]
- Package version: [e.g., 1.0.0]

**Additional Context**
- Error messages
- Logs
- Screenshots
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Mockups, examples, etc.
```

## 🏗️ Project Structure

```
LANGFUSE-MCP-PYTHON/
├── src/
│   └── langfuse-mcp-python/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       ├── tools/             # Individual MCP tools
│       ├── integrations/      # External service integrations
│       └── utils/             # Utility functions
├── pyproject.toml            # Package configuration
└── README.md                 # Main documentation
```

## 🎨 Adding New MCP Tools

### 1. Create Tool File

Create `src/langfuse-mcp-python/tools/your_tool.py`:

```python
"""Your Tool - Description"""

from typing import Any, Dict


class YourTool:
    """Tool description"""
    
    def __init__(self, langfuse_client):
        self.langfuse = langfuse_client
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Execute the tool"""
        # Implementation
        return "Result"
```

### 2. Register in Server

Add to `server.py`:

```python
Tool(
    name="your_tool",
    description="Tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        }
    }
)
```

### 3. Add Tests

Create tests in `tests/test_your_tool.py`

### 4. Update Documentation

- Add to README.md
- Add examples
- Update QUICK_REFERENCE.md

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Langfuse Docs](https://langfuse.com/docs)
- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## 🙏 Thank You!

Every contribution, no matter how small, is valuable. Thank you for helping make this project better!

---

**Happy Contributing!** 🎉
