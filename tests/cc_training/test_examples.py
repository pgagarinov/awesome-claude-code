"""Tests for example modules - checking structure and imports."""

import pytest
import ast
from pathlib import Path


EXAMPLES_DIR = Path(__file__).parent.parent.parent / "src" / "cc_training" / "examples"


def get_example_files():
    """Get all example Python files."""
    return sorted(EXAMPLES_DIR.glob("*.py"))


def test_examples_directory_exists():
    """Test that examples directory exists."""
    assert EXAMPLES_DIR.exists()
    assert EXAMPLES_DIR.is_dir()


def test_example_files_exist():
    """Test that example files exist."""
    files = get_example_files()
    # Should have at least the init and a few examples
    assert len(files) >= 2


@pytest.mark.parametrize("example_file", get_example_files())
def test_example_has_docstring(example_file):
    """Test that each example file has a module docstring."""
    if example_file.name == "__init__.py":
        pytest.skip("Init file")

    content = example_file.read_text()
    tree = ast.parse(content)

    docstring = ast.get_docstring(tree)
    assert docstring is not None, f"{example_file.name} missing module docstring"
    assert len(docstring) > 20, f"{example_file.name} docstring too short"


@pytest.mark.parametrize("example_file", get_example_files())
def test_example_has_main_function(example_file):
    """Test that each example has a main() function."""
    if example_file.name == "__init__.py":
        pytest.skip("Init file")

    content = example_file.read_text()
    tree = ast.parse(content)

    function_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    assert "main" in function_names, f"{example_file.name} missing main() function"


@pytest.mark.parametrize("example_file", get_example_files())
def test_example_has_main_guard(example_file):
    """Test that each example has if __name__ == '__main__' guard."""
    if example_file.name == "__init__.py":
        pytest.skip("Init file")

    content = example_file.read_text()
    assert 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content, \
        f"{example_file.name} missing __main__ guard"


@pytest.mark.parametrize("example_file", get_example_files())
def test_example_imports_sdk(example_file):
    """Test that each example imports from claude_agent_sdk."""
    if example_file.name == "__init__.py":
        pytest.skip("Init file")

    content = example_file.read_text()
    assert "claude_agent_sdk" in content, f"{example_file.name} doesn't import SDK"


@pytest.mark.parametrize("example_file", get_example_files())
def test_example_syntax_valid(example_file):
    """Test that each example has valid Python syntax."""
    content = example_file.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"{example_file.name} has syntax error: {e}")


@pytest.mark.parametrize("example_file", get_example_files())
def test_example_uses_asyncio(example_file):
    """Test that examples use asyncio for async code."""
    if example_file.name == "__init__.py":
        pytest.skip("Init file")

    content = example_file.read_text()
    # Examples should use asyncio.run() to run async code
    assert "asyncio" in content, f"{example_file.name} doesn't import asyncio"


def test_examples_are_numbered():
    """Test that example files follow naming convention."""
    files = [f for f in get_example_files() if f.name != "__init__.py"]

    for f in files:
        # Should start with a number
        assert f.name[0].isdigit(), f"{f.name} doesn't start with a number"


def test_example_imports_are_importable():
    """Test that the examples module can be imported."""
    import cc_training.examples

    assert cc_training.examples is not None
