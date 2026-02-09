"""A simple module that Claude will be asked to modify."""


def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hi, {name}!"


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
