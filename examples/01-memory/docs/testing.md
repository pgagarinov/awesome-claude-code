# Testing Standards

This is a **canonical doc** — the single source of truth for testing patterns.
Referenced by both backend and frontend rules.

## Core Principles

1. **Tests are truth** — never change assertions to make tests pass; fix the code
2. **TDD for bugs** — write a failing test before writing the fix
3. **No skipped tests** — fix or delete, never `@skip`

## Backend (pytest)

```python
def test_create_item(client: TestClient, db: FakeDatabase) -> None:
    response = client.post("/items", json={"name": "Widget"})

    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Widget"
```

## Frontend (Jest)

```typescript
test("renders item name", () => {
  render(<ItemCard item={{ id: 1, name: "Widget" }} />);
  expect(screen.getByText("Widget")).toBeInTheDocument();
});
```

## What NOT to Do

- Never mock what you don't own
- Never test implementation details
- Never use `sleep()` in tests — use proper async patterns
