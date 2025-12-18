# Claude Code Training Programme

A structured learning path for mastering Claude Code, from fundamentals to advanced workflows.

---

## Programme Overview

This training programme is designed to take developers from Claude Code beginners to power users. It covers installation, core concepts, best practices, and advanced integrations.

**Prerequisites:**
- Basic command line familiarity
- Git fundamentals
- An Anthropic API key or Claude subscription (for API mode)

**Programme Structure:**
- **Module 1-2:** Foundations (Day 1)
- **Module 3-4:** Information Architecture & Context Management (Day 2)
- **Module 5-6:** Advanced Prompting & Workflows (Day 3)
- **Module 7-9:** Subagents, Multi-modality & Large Files (Day 4)
- **Module 10-12:** SDK, Automation & Enterprise (Day 5)

---

## Module 1: Introduction to Agentic Coding

### Learning Objectives
- Understand what agentic coding is and how it differs from traditional AI coding tools
- Recognise the paradigm shift from autocomplete to autonomous task execution
- Identify use cases where Claude Code excels

### Core Reading
- [Introduction to Agentic Coding](https://claude.com/blog/introduction-to-agentic-coding)
- [Claude Code Landing Page](https://www.anthropic.com/claude-code)

### Key Concepts
1. **Autocomplete vs Agentic**: Traditional tools suggest line-by-line; agentic tools execute multi-step tasks autonomously
2. **Context-Aware Execution**: Claude Code reads your codebase, understands patterns, and makes informed decisions
3. **Human-in-the-Loop**: You maintain control while delegating complex tasks

### Practical Exercise
1. Install Claude Code: `npm install -g @anthropic-ai/claude-code`
2. Navigate to a project directory
3. Run `claude` and explore the help menu
4. Ask Claude Code to explain the structure of your codebase

---

## Module 2: Getting Started with Claude Code

### Learning Objectives
- Install and configure Claude Code
- Navigate the CLI interface
- Execute basic commands and understand outputs
- Configure permissions and settings

### Core Reading
- [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code Settings](https://docs.claude.com/en/docs/claude-code/settings)

### Key Commands
```bash
# Start a session
claude

# Start with a specific prompt
claude "explain this codebase"

# Resume previous session
claude --continue

# Run in non-interactive mode
claude -p "list all TODO comments"

# Compact mode for reduced context usage
claude --compact
```

### Configuration Basics
- **Permission levels**: Understand what Claude Code can and cannot do by default
- **API configuration**: Setting up your Anthropic API key
- **Session management**: How context is maintained across sessions

### Practical Exercise
1. Start a Claude Code session in a project
2. Ask it to find all files of a specific type
3. Request an explanation of a complex function
4. Exit and resume the session with `--continue`

---

## Module 3: CLAUDE.md & Information Routing Architecture

### Learning Objectives
- Understand the CLAUDE.md hierarchy and file locations
- Design effective information routing using document references
- Create modular documentation structures
- Optimise context loading through strategic file placement

### Core Reading
- [Using CLAUDE.md Files: Customizing Claude Code for Your Codebase](https://claude.com/blog/using-claude-md-files)
- [Claude Code: Best Practices for Agentic Coding](https://www.anthropic.com/engineering/claude-code-best-practices)

### CLAUDE.md Hierarchy

Claude Code reads CLAUDE.md files from multiple locations in priority order:

```
~/.claude/CLAUDE.md              # Global (all projects)
├── Personal preferences
├── Common patterns you use
└── Global tool configurations

./CLAUDE.md                       # Project root (this project)
├── Project overview
├── Architecture decisions
├── Build/test commands
└── References to detailed docs

./src/CLAUDE.md                   # Directory-specific
├── Module-specific patterns
├── Local conventions
└── Component documentation

./.claude/settings.json           # Claude Code settings
```

### Information Routing with References

Instead of putting everything in one massive CLAUDE.md, use **references** to route Claude to relevant documentation:

```markdown
# CLAUDE.md (Project Root)

## Project Overview
E-commerce platform built with Next.js and PostgreSQL.

## Quick Reference
- Build: `npm run build`
- Test: `npm test`
- Dev: `npm run dev`

## Detailed Documentation
For specific topics, refer to:
- API Design: See `docs/api-design.md`
- Database Schema: See `docs/database-schema.md`
- Authentication: See `docs/auth-flow.md`
- Component Patterns: See `src/components/CLAUDE.md`
- Testing Strategy: See `tests/CLAUDE.md`

## When Working On...
- **API endpoints**: Read `docs/api-design.md` first
- **Database changes**: Consult `docs/database-schema.md`
- **New components**: Follow patterns in `src/components/CLAUDE.md`
```

### Strategic Document Placement

```
project/
├── CLAUDE.md                    # High-level overview, routing
├── docs/
│   ├── api-design.md            # Detailed API documentation
│   ├── database-schema.md       # Schema details, migrations
│   ├── auth-flow.md             # Authentication architecture
│   └── deployment.md            # Deployment procedures
├── src/
│   ├── CLAUDE.md                # Source code conventions
│   ├── components/
│   │   └── CLAUDE.md            # Component patterns
│   ├── services/
│   │   └── CLAUDE.md            # Service layer patterns
│   └── utils/
│       └── CLAUDE.md            # Utility conventions
└── tests/
    └── CLAUDE.md                # Testing conventions
```

### Benefits of Information Routing
1. **Reduced Token Usage**: Claude only loads what's needed
2. **Maintainability**: Update docs independently
3. **Clarity**: Each doc has a single responsibility
4. **Scalability**: Works for large codebases

### Conditional Loading Pattern
```markdown
# CLAUDE.md

## Context-Specific Documentation

When working on authentication:
1. First read `docs/auth-flow.md`
2. Check `src/middleware/auth/CLAUDE.md` for implementation details

When working on the API:
1. Read `docs/api-design.md` for conventions
2. See `src/routes/CLAUDE.md` for route patterns

When debugging:
1. Check `docs/troubleshooting.md`
2. Review `logs/README.md` for log locations
```

### Practical Exercise
1. Audit your current project documentation
2. Create a CLAUDE.md hierarchy with routing
3. Split monolithic docs into focused files
4. Test by asking Claude about different areas
5. Measure context usage before/after

---

## Module 4: Context Management & Economy

### Learning Objectives
- Understand how context windows work in Claude Code
- Implement strategies to minimise token usage
- Work effectively within context limitations
- Use compaction and summarisation effectively

### Key Concepts

#### The Context Window
- Claude has a finite context window (tokens it can "remember")
- Everything counts: your prompts, file contents, tool outputs, Claude's responses
- When context fills up, older information may be summarised or dropped

#### Context Costs by Activity
| Activity | Context Cost | Notes |
|----------|--------------|-------|
| Reading small file | Low | Hundreds of tokens |
| Reading large file | High | Can be thousands of tokens |
| Codebase search | Medium | Results add to context |
| Long conversation | Cumulative | Builds over time |
| Subagent spawning | Isolated | Separate context window |

### Strategies for Context Economy

#### 1. Start Fresh for New Tasks
```bash
# Don't continue when switching tasks
claude                    # Fresh start

# Only continue for related follow-ups
claude --continue         # Same task continuation
```

#### 2. Use Compact Mode
```bash
# Reduced verbosity, smaller context footprint
claude --compact

# Or mid-session
/compact
```

#### 3. Be Specific in Requests
```
# BAD: Vague, leads to broad exploration
"Help me understand this codebase"

# GOOD: Focused, minimal context needed
"Explain how user authentication works in src/auth/"
```

#### 4. Use Subagents for Exploration
```
# Instead of exploring yourself (adds to YOUR context)
# Let a subagent explore (uses SEPARATE context)
"Search the codebase for all error handling patterns"
# Claude spawns subagent, only summary returns to main context
```

#### 5. Clear Context When Needed
```bash
/clear                    # Clear conversation history
/compact                  # Summarise and compress context
```

#### 6. Structured Queries Save Tokens
```
# BAD: Multiple back-and-forths
"What files handle auth?"
"Now show me the login function"
"What about the logout?"

# GOOD: Single comprehensive request
"Show me the login and logout functions in the auth module"
```

### Working Around Context Limitations

#### Chunked Processing
For large tasks, break them into independent chunks:
```
"Review files in src/components/ for accessibility issues"
# Complete, then fresh session:
"Review files in src/pages/ for accessibility issues"
```

#### Summary Checkpoints
Ask Claude to summarise progress before context fills:
```
"Summarise what we've found so far about the API structure"
# Save this summary externally
# Start fresh session with summary as starting context
```

#### External Memory
Use CLAUDE.md as external memory:
```markdown
# CLAUDE.md - Session Notes

## Recent Findings (Updated: 2025-01-15)
- Auth uses JWT tokens stored in httpOnly cookies
- Rate limiting implemented in middleware/rateLimit.ts
- Database connections pooled via pg-pool
```

### Practical Exercise
1. Start a session and check context usage with `/status`
2. Perform various operations and observe context growth
3. Practice using `/compact` to reduce context
4. Compare context usage: direct exploration vs subagent delegation
5. Design a workflow for a task that exceeds context limits

---

## Module 5: Working with Large Files

### Learning Objectives
- Strategies for handling files too large to read entirely
- Chunked reading and targeted extraction
- Refactoring large files with Claude's help
- Avoiding context overflow with big files

### The Large File Problem
- Large files (1000+ lines) can consume significant context
- Reading entire files may not be necessary
- Strategic partial reads are more effective

### Strategies for Large Files

#### 1. Targeted Reading
```
# BAD: Read entire file
"Read src/legacy/monolith.js"

# GOOD: Read specific sections
"Read lines 1-50 of src/legacy/monolith.js to see the imports"
"Read the UserService class in src/legacy/monolith.js"
"Find and show me the handlePayment function in src/legacy/monolith.js"
```

#### 2. Structural Overview First
```
"Give me an outline of src/legacy/monolith.js - list all classes,
functions, and their line numbers without reading the full content"
```

#### 3. Search Before Reading
```
"Search for 'validateUser' in src/legacy/monolith.js and show
me just that function with 10 lines of context"
```

#### 4. Chunked Processing
```
"Read src/large-file.ts in chunks:
1. First, show me lines 1-200
2. I'll ask for more sections as needed"
```

#### 5. Use Subagents for Large File Analysis
```
"Analyse src/legacy/monolith.js and create a summary of:
- All exported functions and their purposes
- Dependencies and imports
- Potential issues or code smells
Don't show me the full file, just the analysis."
```

### Refactoring Large Files
```
# Step 1: Understand structure
"Outline the structure of src/legacy/giant-component.tsx"

# Step 2: Identify extraction candidates
"Identify functions in src/legacy/giant-component.tsx that could
be extracted into separate modules"

# Step 3: Extract incrementally
"Extract the validation logic (lines 150-220) from
src/legacy/giant-component.tsx into a new src/utils/validation.ts"
```

### Large File Patterns

#### Configuration Files
```
"Find the database configuration section in config/app-config.json"
"Show me only the 'authentication' key from config/settings.yaml"
```

#### Log Files
```
"Search for ERROR entries in logs/app.log from the last section"
"Find the most recent stack trace in logs/error.log"
```

#### Data Files
```
"Show me the schema/structure of data/users.json (first few entries)"
"Count the number of entries in data/products.csv"
```

### Practical Exercise
1. Find a large file (500+ lines) in your project
2. Practice getting a structural overview without reading it all
3. Use search to find specific functions
4. Extract a section into a new file
5. Compare context usage: full read vs targeted approach

---

## Module 6: Advanced Prompting Techniques

### Learning Objectives
- Master different prompting regimes (plan mode, direct execution)
- Write effective prompts for complex tasks
- Use extended thinking appropriately
- Chain prompts for multi-step workflows

### Prompting Regimes

#### 1. Direct Execution Mode (Default)
For straightforward tasks where you trust Claude's approach:
```
"Add input validation to the signup form"
"Fix the null pointer exception in UserService.getUser()"
"Write unit tests for the calculateTotal function"
```

#### 2. Plan Mode
For complex tasks where you want to review the approach first:
```
"I want to add a caching layer to the API. Enter plan mode and
design an approach before implementing."

# Or explicitly:
/plan "Refactor the authentication system to use OAuth2"
```

**When to use Plan Mode:**
- Architectural changes
- Multi-file refactoring
- Unfamiliar codebases
- Irreversible operations
- When multiple valid approaches exist

#### 3. Exploration Mode
When you need information before deciding on action:
```
"Before making any changes, explore how error handling currently
works across the codebase and summarise the patterns used."
```

#### 4. Extended Thinking Mode
For complex reasoning tasks:
```
"Think deeply about how to optimise this database query.
Consider indexes, query structure, and caching strategies."

# Triggers deeper analysis before responding
```

### Prompt Patterns for Common Scenarios

#### The Context-Setting Pattern
```
"Context: We're building a REST API for a mobile app.
Constraint: Must support offline-first architecture.
Task: Design the sync mechanism for user data.
Output: Implementation plan with code examples."
```

#### The Step-by-Step Pattern
```
"Implement user authentication:
1. First, show me your planned approach
2. Wait for my approval
3. Then implement step by step
4. Test each component before moving on"
```

#### The Constraint Pattern
```
"Refactor this function with these constraints:
- No external dependencies
- Must remain backwards compatible
- Keep under 50 lines
- Include error handling"
```

#### The Example-Driven Pattern
```
"Add a new API endpoint following the exact pattern used in
src/routes/users.ts - same structure, error handling, and response format"
```

#### The Negative Pattern (What NOT to do)
```
"Update the database schema.
Do NOT:
- Drop any existing columns
- Change column types
- Modify indexes on production tables"
```

### Iterative Refinement
```
# Round 1: Broad request
"Improve the performance of the search feature"

# Round 2: Focus based on findings
"Focus on the database query - add appropriate indexes"

# Round 3: Polish
"Now add caching for repeated searches"
```

### Multi-Step Workflow Prompts
```
"Let's refactor the payment module:

Phase 1 - Analysis:
- Map all payment-related files
- Identify dependencies
- Document current flow

Phase 2 - Planning:
- Propose new structure
- Identify breaking changes
- Plan migration path

Phase 3 - Implementation:
- Implement changes incrementally
- Update tests after each change
- Verify no regressions

Start with Phase 1 and wait for my go-ahead before each phase."
```

### Practical Exercise
1. Take a complex task and write it as a direct execution prompt
2. Rewrite the same task for plan mode
3. Practice the context-setting pattern
4. Use extended thinking on an algorithmic problem
5. Design a multi-phase prompt for a refactoring task

---

## Module 7: Subagents - Distributed Task Execution

### Learning Objectives
- Understand how Claude Code spawns and manages subagents
- Know when to use subagents vs direct execution
- Configure subagent behaviour
- Design effective subagent workflows

### What Are Subagents?

Subagents are separate Claude instances that Claude Code spawns to handle specific tasks. They:
- Have their **own context window** (isolated from main conversation)
- Can run in **parallel** for independent tasks
- Return **summarised results** to the main agent
- Are ideal for **exploration** and **research** tasks

### How Subagents Work

```
┌─────────────────────────────────────────────────────────┐
│                    Main Claude Session                   │
│                    (Your conversation)                   │
│                                                          │
│  "Find all security vulnerabilities in the codebase"    │
│                          │                               │
│                          ▼                               │
│              ┌──────────────────────┐                   │
│              │   Spawns Subagent    │                   │
│              └──────────────────────┘                   │
│                          │                               │
└──────────────────────────┼───────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Subagent Context                      │
│                 (Separate, isolated)                     │
│                                                          │
│  - Reads multiple files                                  │
│  - Searches codebase                                     │
│  - Analyses patterns                                     │
│  - Builds comprehensive understanding                    │
│                                                          │
│              All this stays HERE                         │
│              (doesn't fill main context)                 │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
                    Summary returned
                    to main session
```

### When to Use Subagents

**Good for Subagents:**
- Codebase exploration ("How does X work?")
- Pattern searching ("Find all uses of Y")
- Research tasks ("What libraries handle Z?")
- Parallel independent tasks
- Tasks requiring reading many files

**Keep in Main Session:**
- Actual code editing
- Interactive decision-making
- Tasks requiring conversation context
- Sequential dependent operations

### Subagent Types

Claude Code uses different subagent types for different tasks:

| Type | Use Case | Tools Available |
|------|----------|-----------------|
| `Explore` | Codebase exploration | Read, Glob, Grep |
| `Plan` | Architecture planning | All tools |
| `general-purpose` | Complex multi-step tasks | All tools |

### Triggering Subagents

Subagents are triggered automatically when appropriate, but you can encourage their use:

```
"Search the entire codebase for deprecated API usage"
# Claude will likely spawn a subagent

"Explore how the caching layer works across all services"
# Good candidate for subagent exploration

"In parallel, analyse both the frontend and backend for
performance bottlenecks"
# May spawn multiple subagents
```

### Parallel Subagents
```
"Analyse these three areas in parallel:
1. Authentication security
2. API rate limiting
3. Data validation

Give me a summary of findings from each."
# Claude may spawn 3 parallel subagents
```

### Subagent Results
Subagents return summaries, not full context:
```
Main Session: "How does the payment system work?"

[Subagent explores: reads 15 files, traces code paths]

Subagent Summary returned:
"The payment system uses Stripe. Entry point is
src/payments/processor.ts. Flow: validateCart() →
createPaymentIntent() → confirmPayment() → updateOrder()"

# Main session gets summary, not all 15 files
```

### Practical Exercise
1. Ask Claude to explore a complex part of your codebase
2. Observe when subagents are spawned (check output)
3. Compare context usage: direct exploration vs subagent
4. Practice requesting parallel subagent tasks
5. Design a task that benefits from multiple subagents

---

## Module 8: Multi-Modal Capabilities - Screenshots & Images

### Learning Objectives
- Understand Claude's vision capabilities in Claude Code
- Analyse screenshots for debugging and design review
- Work with UI mockups and diagrams
- Extract information from images

### Claude's Vision Capabilities

Claude Code can analyse images including:
- Screenshots of UI/applications
- Error message screenshots
- Design mockups and wireframes
- Architecture diagrams
- Charts and graphs
- Photos of whiteboards
- Documentation images

### Providing Images to Claude Code

#### Method 1: File Path
```
"Analyse the screenshot at ./screenshots/error.png"
"Review the UI mockup at ./designs/homepage-v2.png"
```

#### Method 2: Drag and Drop
In terminal emulators that support it, drag an image into the session.

#### Method 3: Clipboard (where supported)
```
"Analyse the image I just copied to clipboard"
```

### Use Cases for Screenshot Analysis

#### 1. Debugging Visual Issues
```
"Here's a screenshot of the bug: ./screenshots/layout-broken.png
The sidebar should be on the left but it's overlapping the content.
Find and fix the CSS issue."
```

#### 2. UI Review
```
"Compare this screenshot ./screenshots/current.png with the design
mockup ./designs/expected.png. List all differences."
```

#### 3. Error Analysis
```
"This screenshot shows the error in my browser console:
./screenshots/console-error.png
Help me debug this issue."
```

#### 4. Design Implementation
```
"Implement this UI component based on the mockup at
./designs/card-component.png using our existing design system."
```

#### 5. Architecture Understanding
```
"Here's a diagram of our system architecture: ./docs/architecture.png
Explain how data flows from the user request to the database."
```

#### 6. Documentation Extraction
```
"Extract the configuration options from this documentation
screenshot: ./screenshots/api-docs.png"
```

### Best Practices for Image Analysis

1. **Provide Context**
```
# BAD
"What's wrong here?" + image

# GOOD
"This screenshot shows our checkout page. Users report the
'Submit' button is unresponsive. What might cause this?" + image
```

2. **Be Specific About What to Look For**
```
"In this screenshot, focus on:
- The error message in the red banner
- The network request that failed
- The console errors at the bottom"
```

3. **Combine with Code Context**
```
"The screenshot shows a rendering bug in our ProductCard component.
The component is at src/components/ProductCard.tsx.
Analyse the screenshot and fix the component."
```

### Image Analysis for Different Roles

#### For Developers
- Debug visual regressions
- Implement designs from mockups
- Understand error screenshots from users
- Review console/DevTools output

#### For Designers
- Compare implementation to designs
- Document UI inconsistencies
- Analyse competitor interfaces

#### For QA
- Document bugs with screenshots
- Verify visual requirements
- Track UI changes over time

### Practical Exercise
1. Take a screenshot of a UI bug in your application
2. Ask Claude to analyse and suggest fixes
3. Provide a design mockup and ask for implementation
4. Screenshot an error and ask for debugging help
5. Use a whiteboard photo of architecture for documentation

---

## Module 9: Claude Code SDK - Local & Custom Usage

### Learning Objectives
- Understand the Claude Code SDK architecture
- Run Claude Code locally without per-token API costs
- Build custom integrations and workflows
- Create specialised agents for your needs

### SDK vs CLI vs API

| Aspect | Claude Code CLI | Claude API | Claude Code SDK |
|--------|-----------------|------------|-----------------|
| Interface | Terminal | HTTP/REST | Programmatic |
| Billing | Subscription or API | Per token | Depends on setup |
| Customisation | Limited | Full | Full |
| Local models | No | No | Possible* |
| Best for | Interactive use | Custom apps | Automation, integration |

*With compatible local model providers

### Claude Code SDK Overview

The Claude Code SDK (also called Claude Agent SDK) allows you to:
- Build autonomous agents programmatically
- Integrate Claude Code capabilities into your applications
- Create custom tools and workflows
- Run in CI/CD pipelines

### Installation
```bash
npm install @anthropic-ai/claude-code-sdk
# or
pip install claude-code-sdk
```

### Basic SDK Usage

```javascript
import { ClaudeCode } from '@anthropic-ai/claude-code-sdk';

const claude = new ClaudeCode({
  // Uses existing Claude Code authentication
  // No separate API key needed if logged in
});

// Run a task
const result = await claude.run({
  prompt: "Explain the main function in src/index.ts",
  cwd: "/path/to/project"
});

console.log(result.response);
```

### Building Custom Agents

```javascript
import { Agent, Tool } from '@anthropic-ai/claude-code-sdk';

// Define custom tools
const databaseTool = new Tool({
  name: "query_database",
  description: "Run a read-only SQL query",
  parameters: {
    query: { type: "string", description: "SQL query to run" }
  },
  execute: async ({ query }) => {
    // Your database query logic
    return await db.query(query);
  }
});

// Create agent with custom tools
const agent = new Agent({
  tools: [databaseTool],
  systemPrompt: `You are a database analyst assistant.
    You can query the database to answer questions.
    Always explain your queries before running them.`
});

// Run the agent
const response = await agent.run(
  "What are the top 10 customers by order value?"
);
```

### Cost-Efficient SDK Patterns

#### 1. Batch Processing
```javascript
// Process multiple files without interactive overhead
const files = await glob("src/**/*.ts");

for (const file of files) {
  const result = await claude.run({
    prompt: `Add JSDoc comments to ${file}`,
    cwd: projectRoot
  });
  // Results cached, minimal token usage
}
```

#### 2. Template-Based Workflows
```javascript
// Reusable prompts reduce token usage
const reviewTemplate = `
Review this code for:
- Security issues
- Performance problems
- Code style violations

File: {file}
Focus areas: {focusAreas}
`;

async function reviewFile(file, focusAreas) {
  return claude.run({
    prompt: reviewTemplate
      .replace('{file}', file)
      .replace('{focusAreas}', focusAreas.join(', '))
  });
}
```

#### 3. Cached Context
```javascript
// Load context once, reuse across queries
const agent = new Agent({
  contextFiles: [
    'CLAUDE.md',
    'docs/architecture.md'
  ],
  // Context loaded once, not per-request
});
```

### SDK for CI/CD Integration

```yaml
# .github/workflows/code-review.yml
name: Automated Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Claude Code Review
        run: |
          npx claude-code-sdk review \
            --files "$(git diff --name-only origin/main)" \
            --output review-results.md

      - name: Post Review Comment
        uses: actions/github-script@v6
        with:
          script: |
            const review = fs.readFileSync('review-results.md');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: review
            });
```

### Local Model Integration (Advanced)

For organisations wanting to avoid per-token costs entirely:

```javascript
import { Agent } from '@anthropic-ai/claude-code-sdk';

// Configure to use a local/self-hosted model
const agent = new Agent({
  provider: 'local',
  modelEndpoint: 'http://localhost:8080/v1',
  model: 'your-local-model',
  // Falls back to Anthropic API if local unavailable
  fallback: true
});
```

**Note**: Local model support depends on the specific SDK version and model compatibility. Check documentation for supported configurations.

### Practical Exercise
1. Install the Claude Code SDK
2. Write a script that analyses multiple files
3. Create a custom tool for your specific workflow
4. Build an agent with a specialised system prompt
5. Integrate with your CI/CD pipeline

---

## Module 10: Custom Slash Commands & MCP Integration

### Learning Objectives
- Create custom slash commands for repetitive tasks
- Understand the Model Context Protocol (MCP)
- Configure MCP servers for extended capabilities
- Build project-specific automation

### Core Reading
- [Claude Code: Best Practices for Agentic Coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Claude Code Settings](https://docs.claude.com/en/docs/claude-code/settings)

### Custom Slash Commands

Create `.claude/commands/` directory with markdown files:

```markdown
# .claude/commands/review.md
Review the current changes for:
- Code quality issues
- Potential bugs
- Security vulnerabilities
- Performance concerns

Provide specific, actionable feedback.
```

Usage: `/project:review`

### Advanced Command Examples

```markdown
# .claude/commands/new-component.md
Create a new React component with:
- TypeScript types
- Unit tests
- Storybook story
- Following patterns in src/components/Button/

Component name: $ARGUMENTS
```

```markdown
# .claude/commands/debug.md
Debug the following issue:

1. First, identify relevant files
2. Trace the code path
3. Identify the root cause
4. Propose a fix
5. Wait for approval before implementing

Issue: $ARGUMENTS
```

### MCP Integration
MCP (Model Context Protocol) extends Claude Code's capabilities:
- **Database access**: Query and understand your database schema
- **External APIs**: Integrate with third-party services
- **Custom tools**: Build specialised tools for your workflow

### Practical Exercise
1. Create a custom slash command for your common workflow
2. Set up an MCP server (e.g., filesystem or database)
3. Test the integration with real queries
4. Share useful commands with your team

---

## Module 11: Security Reviews & Code Quality

### Learning Objectives
- Use Claude Code for automated security analysis
- Implement security review workflows
- Integrate security checks into development process
- Understand common vulnerability patterns

### Core Reading
- [Automate Security Reviews with Claude Code](https://www.anthropic.com/news/automate-security-reviews-with-claude-code)

### Security Review Command
```
/security-review
```

This command analyses your codebase for:
- OWASP Top 10 vulnerabilities
- Injection risks (SQL, command, XSS)
- Authentication/authorisation issues
- Sensitive data exposure
- Security misconfigurations

### Security Workflow
1. **Pre-commit**: Review changes before committing
2. **PR Review**: Automated security checks on pull requests
3. **Periodic Audits**: Regular full-codebase security scans
4. **Dependency Review**: Check for vulnerable dependencies

### Practical Exercise
1. Run `/security-review` on your project
2. Address any identified vulnerabilities
3. Create a custom security-focused slash command
4. Set up a pre-commit hook for security checks

---

## Module 12: GitHub Actions & CI/CD Integration

### Learning Objectives
- Set up Claude Code GitHub Action
- Automate code review on pull requests
- Implement automated issue triage
- Build CI/CD pipelines with Claude Code

### Core Reading
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)

### Basic GitHub Action Setup
```yaml
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          mode: review
```

### Use Cases
1. **Automated Code Review**: Get AI feedback on every PR
2. **Issue Triage**: Automatically label and prioritise issues
3. **Documentation Updates**: Auto-generate docs for code changes
4. **Security Scanning**: Run security reviews on PRs

### Practical Exercise
1. Add the Claude Code Action to a repository
2. Configure it for automated PR reviews
3. Create a workflow for issue triage
4. Set up security review automation

---

## Module 13: Real-World Case Studies

### Learning Objectives
- Learn from Anthropic's internal usage patterns
- Understand cross-functional applications
- Identify opportunities in your own work

### Core Reading
- [How Anthropic Teams Use Claude Code](https://www.anthropic.com/news/how-anthropic-teams-use-claude-code)

### Case Study Highlights

**Engineering Teams**
- Rapid prototyping and iteration
- Legacy code modernisation
- Cross-language migrations

**Legal/Compliance**
- Contract review automation
- Policy compliance checking
- Documentation analysis

**Marketing/Content**
- Content generation workflows
- Data-driven insights
- Campaign analysis

**Data Science**
- Visualisation generation
- Data pipeline development
- Analysis automation

### Reflection Exercise
1. Identify three tasks in your role that Claude Code could help with
2. Design a workflow for each task
3. Implement and test the most impactful one
4. Share learnings with your team

---

## Module 14: Claude Code on the Web

### Learning Objectives
- Access Claude Code through browser interface
- Understand when to use web vs CLI
- Collaborate using web-based sessions

### Core Reading
- [Claude Code on the Web](https://www.anthropic.com/news/claude-code-on-the-web)

### Web vs CLI
| Feature | Web | CLI |
|---------|-----|-----|
| File system access | Limited/sandboxed | Full access |
| Terminal commands | Sandboxed | Full access |
| Collaboration | Easier sharing | Local only |
| Setup required | None | Installation |
| Best for | Quick tasks, sharing | Full development |

### When to Use Web
- Quick explorations without local setup
- Sharing sessions with team members
- Working on unfamiliar machines
- Demonstrating Claude Code capabilities

### Practical Exercise
1. Access Claude Code on the web
2. Complete a simple coding task
3. Compare the experience with CLI
4. Identify scenarios where each excels

---

## Quick Reference: Context Economy Cheatsheet

### Token-Saving Techniques

| Technique | Savings | When to Use |
|-----------|---------|-------------|
| Subagents for exploration | High | Research, codebase understanding |
| Targeted file reading | Medium | Working with specific functions |
| `/compact` mode | Medium | Long sessions |
| Fresh sessions | High | Switching tasks |
| Strategic CLAUDE.md routing | Medium | Large projects |
| Avoiding full file reads | High | Large files (500+ lines) |

### Prompting Efficiency

```
# Inefficient (multiple rounds)
"What files handle auth?" → "Show me login" → "Show me logout"

# Efficient (single comprehensive request)
"Show me the login and logout implementations in the auth module"
```

### Context Red Flags
- Reading entire large files unnecessarily
- Long exploratory conversations without clear goals
- Not using subagents for research tasks
- Continuing sessions across unrelated tasks

---

## Quick Reference: Prompting Patterns

### Task Patterns
| Pattern | Example | Use Case |
|---------|---------|----------|
| Direct | "Add validation to form" | Simple, clear tasks |
| Plan | "/plan Refactor auth system" | Complex changes |
| Explore | "How does caching work here?" | Understanding code |
| Extended | "Think deeply about optimising..." | Complex reasoning |

### Constraint Patterns
```
"Do X with these constraints: ..."
"Do X but do NOT: ..."
"Do X following the pattern in Y"
```

### Multi-Phase Pattern
```
"Phase 1: Analyse... [wait for approval]
 Phase 2: Plan... [wait for approval]
 Phase 3: Implement..."
```

---

## Assessment & Certification

### Knowledge Check
Complete these tasks to demonstrate proficiency:

1. **Foundation** (Modules 1-2)
   - [ ] Successfully install and configure Claude Code
   - [ ] Complete a basic codebase exploration

2. **Information Architecture** (Modules 3-4)
   - [ ] Create a CLAUDE.md hierarchy with routing
   - [ ] Demonstrate context-efficient workflows
   - [ ] Work with a large file using targeted approaches

3. **Advanced Prompting** (Modules 5-6)
   - [ ] Use plan mode for a complex task
   - [ ] Write multi-phase workflow prompts
   - [ ] Use extended thinking effectively

4. **Subagents & Multi-Modal** (Modules 7-8)
   - [ ] Trigger and utilise subagents appropriately
   - [ ] Analyse screenshots for debugging
   - [ ] Design parallel subagent workflows

5. **SDK & Automation** (Modules 9-12)
   - [ ] Build a custom workflow with the SDK
   - [ ] Set up GitHub Actions integration
   - [ ] Create custom slash commands

### Final Project
Create a complete Claude Code setup for a project including:
- Optimised CLAUDE.md hierarchy with document routing
- Custom slash commands for team workflows
- SDK scripts for automation
- GitHub Actions integration
- Context management strategy documentation
- Documentation for team onboarding

---

## Additional Resources

### Official Documentation
- [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Release Notes](https://support.claude.com/en/articles/12138966-release-notes)

### Learning Platforms
- [Anthropic Academy: Build with Claude](https://www.anthropic.com/learn/build-with-claude)

### Repositories
- [anthropics/claude-code](https://github.com/anthropics/claude-code)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)

### Community
- GitHub Issues for questions and feedback
- Anthropic Discord (if available)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 2025 | Initial programme release |
| 1.1 | December 2025 | Added: Subagents, Information Routing, SDK deep-dive, Context Economy, Large Files, Multi-modality, Advanced Prompting |

---

*This training programme is based on official Anthropic documentation and resources. For the latest updates, always refer to the official documentation.*
