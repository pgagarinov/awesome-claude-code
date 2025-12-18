"""Test that the Claude Agent SDK imports correctly."""

import pytest


def test_basic_imports():
    """Test that basic SDK components can be imported."""
    from claude_agent_sdk import query, ClaudeAgentOptions

    assert query is not None
    assert ClaudeAgentOptions is not None


def test_message_type_imports():
    """Test that message types can be imported."""
    from claude_agent_sdk import (
        Message,
        TextBlock,
        ToolUseBlock,
        ToolResultBlock,
        AssistantMessage,
        ResultMessage,
    )

    assert Message is not None
    assert TextBlock is not None
    assert ToolUseBlock is not None
    assert ToolResultBlock is not None
    assert AssistantMessage is not None
    assert ResultMessage is not None


def test_client_import():
    """Test that the SDK client can be imported."""
    from claude_agent_sdk import ClaudeSDKClient

    assert ClaudeSDKClient is not None


def test_options_creation():
    """Test that ClaudeAgentOptions can be instantiated."""
    from claude_agent_sdk import ClaudeAgentOptions

    # Default options
    options = ClaudeAgentOptions()
    assert options is not None

    # With parameters
    options = ClaudeAgentOptions(
        cwd="/tmp",
        model="sonnet",
        max_turns=5,
    )
    assert options.cwd == "/tmp"
    assert options.model == "sonnet"
    assert options.max_turns == 5


def test_options_with_system_prompt():
    """Test options with system prompt."""
    from claude_agent_sdk import ClaudeAgentOptions

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
    )
    assert options.system_prompt == "You are a helpful assistant."


def test_query_is_async():
    """Test that query is an async function."""
    import asyncio
    from claude_agent_sdk import query

    # query should return an async iterator
    result = query(prompt="test")
    assert hasattr(result, '__anext__')


def test_version_available():
    """Test that SDK version is available."""
    import claude_agent_sdk

    assert hasattr(claude_agent_sdk, '__version__')
    assert claude_agent_sdk.__version__  # Not empty
