# MCP Servers vs Python Libraries

## The Question

If Claude Code can write and execute Python scripts, why do we need MCP servers? Can't we just ask Claude to write a Playwright script instead of using the Playwright MCP server?

## Short Answer

Both approaches work. MCP servers provide **real-time interactive tools**, while Python libraries enable **scriptable automation**. Choose based on your workflow.

## Detailed Comparison

| Aspect | MCP Server | Python Library |
|--------|------------|----------------|
| **Interaction model** | Conversational, real-time | Script-based, batch |
| **Setup** | One-time `claude mcp add` | Install library, write code |
| **Usage** | Natural language commands | Claude writes/runs scripts |
| **State management** | Server maintains browser state | Script manages own state |
| **Iteration speed** | Immediate feedback loop | Write → Run → Review → Repeat |
| **Reproducibility** | Commands in chat history | Scripts saved to files |
| **CI/CD integration** | Requires Claude session | Runs independently |

## When to Use MCP Servers

**Interactive exploration and debugging:**
```
> Open staging.example.com and show me the login page
> Enter "testuser" and "password123", then click login
> What error message appeared?
> Take a screenshot
> Now try with "admin" instead
```

MCP excels when you're:
- Exploring a website interactively
- Debugging UI issues in real-time
- Not sure what you're looking for yet
- Want immediate visual feedback
- Need to make decisions based on what you see

**Key advantage:** The browser stays open between commands. Claude can see the current state and respond to what's actually on screen.

## When to Use Python Libraries

**Automated, reproducible tasks:**
```
> Write a Python script that:
  1. Logs into staging.example.com
  2. Navigates to the user list
  3. Exports all users to CSV
  4. Takes a screenshot of each page
  Save it as scripts/export_users.py
```

Python excels when you're:
- Building automation that runs repeatedly
- Need to integrate with CI/CD pipelines
- Want version-controlled, reviewable scripts
- Need complex logic (loops, error handling, retries)
- Running headless on servers without Claude

**Key advantage:** Scripts are artifacts you keep. Run them tomorrow, next month, or in your CI pipeline.

## Hybrid Approach

Often the best workflow combines both:

1. **Explore with MCP** - Use conversational commands to understand the UI, find the right selectors, test the flow
2. **Codify with Python** - Once you know what works, ask Claude to write a reusable script

```
> [Using MCP] Open the admin panel and show me how to export users
> [After exploring] Now write a Python script that automates this export
```

## It's Not About Skill Level

MCP servers aren't "for non-programmers." Even experienced developers benefit from:

- **Faster feedback loops** - No write/run/check cycle
- **Less boilerplate** - No script setup, imports, cleanup
- **Conversational refinement** - "Actually, click the other button"
- **Visual debugging** - See what Claude sees in real-time

The choice is about **workflow**, not capability.

## Example: Same Task, Both Ways

**Task:** Check if the login page shows an error for invalid credentials

### MCP Approach (Interactive)
```
> Open localhost:3000/login
> Enter "bad@email.com" and "wrongpass", click submit
> What error message is shown?

Claude: The page displays "Invalid credentials. Please try again." in a red banner.
```

### Python Approach (Scripted)
```
> Write a script to test login error handling on localhost:3000/login

Claude writes and runs:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("localhost:3000/login")
    page.fill("#email", "bad@email.com")
    page.fill("#password", "wrongpass")
    page.click("button[type=submit]")
    error = page.locator(".error-banner").text_content()
    print(f"Error message: {error}")
    browser.close()
```

Both work. MCP is faster for one-off checks. Python is better if you'll run this test repeatedly.
