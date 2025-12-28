# Part 19: Running Agents in Parallel

## The Performance Challenge

When using the Claude Agent SDK, each `query()` call spawns a Claude CLI subprocess. Sequential execution becomes a bottleneck when you need to process many items:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SEQUENTIAL vs PARALLEL EXECUTION                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  SEQUENTIAL (slow):                                                             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                                  │
│  │ Q1   │→│ Q2   │→│ Q3   │→│ Q4   │→│ Q5   │  Total: 5 × 30s = 150s           │
│  │ 30s  │ │ 30s  │ │ 30s  │ │ 30s  │ │ 30s  │                                  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘                                  │
│                                                                                 │
│  PARALLEL (fast):                                                               │
│  ┌──────┐                                                                       │
│  │ Q1   │──┐                                                                    │
│  └──────┘  │                                                                    │
│  ┌──────┐  │                                                                    │
│  │ Q2   │──┤                                                                    │
│  └──────┘  ├──→ Total: ~35s (limited by slowest + overhead)                     │
│  ┌──────┐  │                                                                    │
│  │ Q3   │──┤                                                                    │
│  └──────┘  │                                                                    │
│  ┌──────┐  │                                                                    │
│  │ Q4   │──┤                                                                    │
│  └──────┘  │                                                                    │
│  ┌──────┐  │                                                                    │
│  │ Q5   │──┘                                                                    │
│  └──────┘                                                                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Key Insight: Use anyio, Not asyncio

The Claude Agent SDK is built on **anyio**, not asyncio. Using `asyncio.gather()` causes conflicts:

```python
# WRONG - causes "Attempted to exit cancel scope in a different task" error
async def run_parallel():
    await asyncio.gather(
        query_1(),
        query_2(),
        query_3(),
    )
```

The correct approach uses **anyio's structured concurrency**:

```python
# CORRECT - uses anyio's task groups
import anyio

async def run_parallel():
    async with anyio.create_task_group() as tg:
        tg.start_soon(query_1)
        tg.start_soon(query_2)
        tg.start_soon(query_3)
```

## Basic Pattern: Parallel Queries with anyio

```python
import anyio
from functools import partial
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def run_single_query(prompt: str, results: list, idx: int) -> None:
    """Run a single query and store result."""
    options = ClaudeAgentOptions(model="sonnet")

    result_text: str | None = None
    # IMPORTANT: Must fully consume the async generator
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, ResultMessage) and msg.result:
            result_text = msg.result if isinstance(msg.result, str) else str(msg.result)

    results[idx] = result_text

async def run_parallel_queries(prompts: list[str]) -> list[str | None]:
    """Run multiple queries in parallel."""
    results: list[str | None] = [None] * len(prompts)

    async with anyio.create_task_group() as tg:
        for i, prompt in enumerate(prompts):
            tg.start_soon(run_single_query, prompt, results, i)

    return results

def main():
    prompts = [
        "What is Python?",
        "What is Rust?",
        "What is Go?",
    ]
    results = anyio.run(partial(run_parallel_queries, prompts))
    for prompt, result in zip(prompts, results):
        print(f"{prompt}: {result[:100]}...")

if __name__ == "__main__":
    main()
```

## Rate Limiting with Semaphore

Don't overwhelm the API - limit concurrent requests:

```python
import anyio

MAX_CONCURRENT = 10  # Limit parallel requests

async def run_with_rate_limit(prompts: list[str]) -> list[str | None]:
    """Run queries with rate limiting."""
    results: list[str | None] = [None] * len(prompts)
    sem = anyio.Semaphore(MAX_CONCURRENT)

    async def rate_limited_query(idx: int, prompt: str) -> None:
        async with sem:  # Only MAX_CONCURRENT can run simultaneously
            options = ClaudeAgentOptions(model="sonnet")
            result_text: str | None = None

            async for msg in query(prompt=prompt, options=options):
                if isinstance(msg, ResultMessage) and msg.result:
                    result_text = msg.result if isinstance(msg.result, str) else str(msg.result)

            results[idx] = result_text
            print(f"[{idx + 1}] Done")

    async with anyio.create_task_group() as tg:
        for i, prompt in enumerate(prompts):
            tg.start_soon(rate_limited_query, i, prompt)

    return results
```

## Critical Rule: Don't Exit Early

The async generator from `query()` must be fully consumed. Early exits break anyio's cleanup:

```python
# WRONG - early return breaks structured concurrency
async def bad_query(prompt: str) -> str:
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, ResultMessage):
            return msg.result  # DON'T DO THIS

# CORRECT - store result, continue iterating
async def good_query(prompt: str) -> str | None:
    result: str | None = None
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, ResultMessage) and msg.result:
            result = msg.result if isinstance(msg.result, str) else str(msg.result)
    return result  # Return AFTER loop completes
```

## Real-World Example: Parallel Documentation Audit

This pattern was used in `doc_audit.py` to check documentation routing for 50 questions in ~2.4 minutes instead of ~5 minutes:

```python
import anyio
import json
from functools import partial
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

CATEGORIES = [
    ("setup", "Installation and environment setup"),
    ("testing", "pytest, mocks, fixtures"),
    ("config", "Hydra, MLflow configuration"),
    # ... more categories
]

MAX_CONCURRENT = 10

async def generate_questions_for_category(
    category: str,
    description: str,
    count: int,
    sem: anyio.Semaphore,
) -> list[dict]:
    """Generate questions for one category."""
    async with sem:
        prompt = f"""Generate {count} realistic user questions about: {description}
Output as JSON array: [{{"category": "{category}", "question": "..."}}]"""

        options = ClaudeAgentOptions(model="sonnet", allowed_tools=[])
        result_text: str | None = None

        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, ResultMessage) and msg.result:
                result_text = str(msg.result)

        if result_text:
            return json.loads(result_text)
        return []

async def phase1_generate_all(per_category: int) -> list[dict]:
    """Phase 1: Generate questions for all categories in parallel."""
    results: list[list[dict]] = [[] for _ in CATEGORIES]
    sem = anyio.Semaphore(MAX_CONCURRENT)

    async def run_category(idx: int, cat: str, desc: str) -> None:
        questions = await generate_questions_for_category(cat, desc, per_category, sem)
        results[idx] = questions
        print(f"   {cat}: {len(questions)} questions")

    async with anyio.create_task_group() as tg:
        for i, (cat, desc) in enumerate(CATEGORIES):
            tg.start_soon(run_category, i, cat, desc)

    return [q for batch in results for q in batch]

async def check_single_question(
    idx: int,
    question: dict,
    context: dict,
    sem: anyio.Semaphore,
    results: list[dict],
) -> None:
    """Check routing for one question."""
    async with sem:
        prompt = f"""Check if CLAUDE.md routes to docs that answer: "{question['question']}"
Output JSON: {{"answered": "yes|partial|no", "obviousness": 1-10, "gap": "..."}}"""

        options = ClaudeAgentOptions(
            model="sonnet",
            allowed_tools=["Read", "Glob"],
            cwd=context["project_root"],
        )

        result_text: str | None = None
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, ResultMessage) and msg.result:
                result_text = str(msg.result)

        if result_text:
            results[idx] = json.loads(result_text)
            status = "✓" if results[idx].get("answered") == "yes" else "✗"
            print(f"   [{idx + 1}] {status} {question['question'][:50]}...")

async def phase2_check_routing(questions: list[dict], context: dict) -> list[dict]:
    """Phase 2: Check routing for all questions in parallel."""
    results: list[dict] = [{} for _ in questions]
    sem = anyio.Semaphore(MAX_CONCURRENT)

    async with anyio.create_task_group() as tg:
        for i, q in enumerate(questions):
            tg.start_soon(check_single_question, i, q, context, sem, results)

    return results

async def run_audit(sample_size: int = 50) -> None:
    """Main orchestration."""
    per_category = sample_size // len(CATEGORIES)

    print(f"Phase 1: Generating questions ({len(CATEGORIES)} categories parallel)...")
    questions = await phase1_generate_all(per_category)

    print(f"Phase 2: Checking {len(questions)} questions (max {MAX_CONCURRENT} parallel)...")
    results = await phase2_check_routing(questions, {"project_root": "."})

    # Phase 3: Aggregate results
    yes_count = sum(1 for r in results if r.get("answered") == "yes")
    print(f"\nResults: {yes_count}/{len(results)} fully answered")

def main():
    anyio.run(partial(run_audit, sample_size=50))

if __name__ == "__main__":
    main()
```

## Performance Results

| Metric | Sequential | Parallel (anyio) | Speedup |
|--------|------------|------------------|---------|
| Phase 1 (8 categories) | ~40s | ~9s | 4.4x |
| Phase 2 (50 questions) | ~200s | ~130s | 1.5x |
| **Total** | ~240s (4 min) | ~140s (2.4 min) | **1.7x** |

The speedup is limited by:
1. Rate limiting (MAX_CONCURRENT = 10)
2. Slowest query in each batch
3. API response time variance

## Summary

| Aspect | Guidance |
|--------|----------|
| Library | Use **anyio**, not asyncio |
| Parallel | Use `anyio.create_task_group()` |
| Rate limit | Use `anyio.Semaphore(N)` |
| Results | Pre-allocate list, pass index to tasks |
| Generators | **Never exit early** - fully consume |
| Entry point | Use `anyio.run(partial(func, args))` |

## Common Pitfalls

1. **Using asyncio.gather()** - Causes scope errors
2. **Early return/break in async for** - Breaks cleanup
3. **No rate limiting** - Overwhelms API
4. **Forgetting functools.partial** - anyio.run() doesn't accept kwargs
