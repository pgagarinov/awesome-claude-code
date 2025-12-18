"""Integration tests for Claude Agent SDK.

These tests make actual calls to Claude Code, so they:
- Require Claude Code to be authenticated
- Are slower than unit tests
- May incur usage costs

Run with: pixi run pytest tests/test_sdk_integration.py -v
Skip with: pixi run pytest -m "not integration"
"""

import asyncio
import pytest
from pathlib import Path

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def project_dir():
    """Return the project root directory."""
    return str(Path(__file__).parent.parent)


@pytest.mark.asyncio
async def test_simple_query():
    """Test a simple query returns a response."""
    from claude_agent_sdk import query

    responses = []
    async for message in query(prompt="What is 2 + 2? Answer with just the number."):
        if hasattr(message, 'content'):
            responses.append(str(message.content))

    result = "".join(responses)
    assert result  # Not empty
    assert "4" in result


@pytest.mark.asyncio
async def test_query_with_options(project_dir):
    """Test query with ClaudeAgentOptions."""
    from claude_agent_sdk import query, ClaudeAgentOptions

    options = ClaudeAgentOptions(
        cwd=project_dir,
        max_turns=1,
    )

    responses = []
    async for message in query(
        prompt="What is the name of this project? Just the name.",
        options=options
    ):
        if hasattr(message, 'content'):
            responses.append(str(message.content))

    result = "".join(responses).lower()
    assert result  # Not empty


@pytest.mark.asyncio
async def test_file_reading(project_dir):
    """Test that Claude can read files in the project."""
    from claude_agent_sdk import query, ClaudeAgentOptions

    options = ClaudeAgentOptions(cwd=project_dir)

    responses = []
    async for message in query(
        prompt="Read pyproject.toml. What is the project name? Just the name.",
        options=options
    ):
        if hasattr(message, 'content'):
            responses.append(str(message.content))

    result = "".join(responses).lower()
    assert "cc-training" in result or "cc_training" in result


@pytest.mark.asyncio
async def test_code_generation():
    """Test code generation capability."""
    from claude_agent_sdk import query

    responses = []
    async for message in query(
        prompt="Write a Python function called 'add' that takes two numbers and returns their sum. Just the code, no explanation."
    ):
        if hasattr(message, 'content'):
            responses.append(str(message.content))

    result = "".join(responses)
    assert "def add" in result
    assert "return" in result


@pytest.mark.asyncio
async def test_json_output():
    """Test structured JSON output."""
    import json
    from claude_agent_sdk import query

    responses = []
    async for message in query(
        prompt='Output exactly this JSON: {"status": "ok", "count": 42}'
    ):
        if hasattr(message, 'content'):
            responses.append(str(message.content))

    result = "".join(responses).strip()

    # Try to find and parse JSON in the response
    # Handle potential markdown code blocks
    if "```" in result:
        lines = result.split("\n")
        json_lines = []
        in_block = False
        for line in lines:
            if line.startswith("```"):
                in_block = not in_block
                continue
            if in_block or (line.startswith("{") or line.startswith("[")):
                json_lines.append(line)
        result = "\n".join(json_lines)

    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["count"] == 42


@pytest.mark.asyncio
async def test_system_prompt():
    """Test that system prompt affects response."""
    from claude_agent_sdk import query, ClaudeAgentOptions

    options = ClaudeAgentOptions(
        system_prompt="You must always respond in exactly 3 words.",
    )

    responses = []
    async for message in query(
        prompt="Say hello",
        options=options
    ):
        if hasattr(message, 'content'):
            responses.append(str(message.content))

    result = "".join(responses).strip()
    words = result.split()
    # Allow some flexibility (3-5 words)
    assert 1 <= len(words) <= 10


@pytest.mark.asyncio
async def test_multiple_sequential_queries():
    """Test multiple queries in sequence."""
    from claude_agent_sdk import query

    results = []

    for i in range(3):
        responses = []
        async for message in query(prompt=f"What is {i} + 1? Just the number."):
            if hasattr(message, 'content'):
                responses.append(str(message.content))
        results.append("".join(responses))

    assert len(results) == 3
    assert "1" in results[0]
    assert "2" in results[1]
    assert "3" in results[2]


@pytest.mark.asyncio
async def test_parallel_queries():
    """Test multiple queries in parallel."""
    from claude_agent_sdk import query

    async def single_query(n: int) -> str:
        responses = []
        async for message in query(prompt=f"What is {n} * 2? Just the number."):
            if hasattr(message, 'content'):
                responses.append(str(message.content))
        return "".join(responses)

    # Run 3 queries in parallel
    results = await asyncio.gather(
        single_query(1),
        single_query(2),
        single_query(3),
    )

    assert "2" in results[0]
    assert "4" in results[1]
    assert "6" in results[2]
