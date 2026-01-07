# Part 31: Output Styles

## What are Output Styles?

Output styles customize how Claude Code communicates - its tone, detail level, and focus areas. They're useful for adapting Claude to different use cases beyond software engineering.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT STYLES OVERVIEW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DEFAULT                    EXPLANATORY                LEARNING             │
│  ────────────────           ────────────────           ────────────────     │
│  • Concise responses        • Detailed explanations   • Teaching focus      │
│  • Code-focused             • Step-by-step            • Conceptual depth    │
│  • Minimal commentary       • Why behind decisions    • Practice prompts    │
│  • Fast iteration           • Context-rich            • Progressive         │
│                                                                             │
│  Best for:                  Best for:                  Best for:            │
│  Experienced devs           Code reviews               Learning new tech    │
│  Quick tasks                Documentation              Onboarding           │
│  Familiar codebases         Complex debugging          Understanding        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

Use the `/output-style` command to change styles:

```bash
# View current style and options
> /output-style

# Switch to explanatory mode
> /output-style explanatory

# Switch to learning mode
> /output-style learning

# Return to default
> /output-style default
```

## Built-in Styles

### Default Style

The default style optimizes for experienced developers working on familiar codebases:

- Concise, action-oriented responses
- Minimal explanation unless requested
- Focus on code changes and commands
- Assumes familiarity with tools and patterns

### Explanatory Style

Provides detailed context and reasoning:

- Explains the "why" behind decisions
- Step-by-step breakdowns
- Trade-off discussions
- Suitable for code reviews and documentation

### Learning Style

Optimized for understanding and skill development:

- Teaching-oriented explanations
- Conceptual foundations before implementation
- Practice suggestions and exercises
- Links to relevant documentation

## Custom Output Styles

Create custom styles by adding markdown files to `~/.claude/output-styles/`:

### Creating a Custom Style

```bash
mkdir -p ~/.claude/output-styles
```

Create a style file with YAML frontmatter:

```markdown
# ~/.claude/output-styles/security-auditor.md
---
name: security-auditor
description: Security-focused code analysis
keep-coding-instructions: true
---

You are a security auditor reviewing code for vulnerabilities.

## Response Guidelines

- Always check for OWASP Top 10 vulnerabilities
- Flag any hardcoded credentials or secrets
- Highlight input validation issues
- Note authentication and authorization concerns
- Suggest secure alternatives for risky patterns

## Output Format

For each finding:
1. **Severity**: Critical/High/Medium/Low
2. **Location**: File and line number
3. **Issue**: Description of the vulnerability
4. **Remediation**: How to fix it
```

### Using Custom Styles

```bash
# List available styles (including custom)
> /output-style

# Use your custom style
> /output-style security-auditor
```

### Style File Options

| Frontmatter Field | Type | Description |
|-------------------|------|-------------|
| `name` | string | Style identifier (used in command) |
| `description` | string | Shown in style list |
| `keep-coding-instructions` | boolean | Retain default coding capabilities |

### The `keep-coding-instructions` Option

```yaml
---
keep-coding-instructions: true  # Keeps file editing, bash, etc.
keep-coding-instructions: false # Pure conversation mode
---
```

When `true` (recommended for most custom styles):
- Claude retains ability to edit files, run commands
- Style adds to default behavior
- Best for specialized coding tasks

When `false`:
- Claude becomes conversational only
- No file editing or command execution
- Best for non-coding use cases (writing, research)

## Example Custom Styles

### Technical Writer

```markdown
# ~/.claude/output-styles/tech-writer.md
---
name: tech-writer
description: Documentation and technical writing focus
keep-coding-instructions: true
---

Focus on clear, well-structured documentation.

## Guidelines

- Use active voice
- Include code examples for all explanations
- Structure with clear headings
- Add diagrams or ASCII art when helpful
- Consider the audience's expertise level

## Output Standards

- Markdown formatting
- Consistent terminology
- Cross-references to related docs
```

### Code Reviewer

```markdown
# ~/.claude/output-styles/reviewer.md
---
name: reviewer
description: Thorough code review style
keep-coding-instructions: true
---

Provide comprehensive code review feedback.

## Review Checklist

1. **Correctness**: Does the code do what it's supposed to?
2. **Performance**: Are there any obvious inefficiencies?
3. **Security**: Any potential vulnerabilities?
4. **Maintainability**: Is the code readable and well-structured?
5. **Testing**: Are there adequate tests?

## Feedback Format

Use constructive, specific feedback:
- ✅ Good: "Consider using `map()` here for clarity"
- ❌ Avoid: "This is wrong"
```

### Minimalist

```markdown
# ~/.claude/output-styles/minimal.md
---
name: minimal
description: Extremely concise responses
keep-coding-instructions: true
---

Be extremely concise. Minimal words, maximum clarity.

- No preamble or pleasantries
- Code only when possible
- One-liners preferred
- Skip obvious explanations
```

## Comparison with Other Customization Methods

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               CUSTOMIZATION METHOD COMPARISON                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Method                  Scope           Persistence      Use Case          │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  Output Styles           Response style  Session/global   Tone & format     │
│  CLAUDE.md               Project context Permanent        Project rules     │
│  --append-system-prompt  Single run      None             One-off tweaks    │
│  --system-prompt         Single run      None             Full override     │
│  Custom agents           Full behavior   Permanent        Complex workflows │
│                                                                             │
│  Combine for best results:                                                  │
│  • CLAUDE.md for project-specific rules                                     │
│  • Output style for communication preferences                               │
│  • Agents for specialized tooling                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to Use Each

| Need | Solution |
|------|----------|
| Different tone/verbosity | Output Style |
| Project-specific context | CLAUDE.md |
| One-off instruction | `--append-system-prompt` |
| Complete behavior change | Custom Agent |
| File-specific rules | `.claude/rules/*.md` |

## Managing Styles

### List All Styles

```bash
> /output-style
# Shows: default, explanatory, learning, + custom styles
```

### Share Custom Styles

Custom styles are just markdown files - share them with your team:

```bash
# Copy to project for team sharing
cp ~/.claude/output-styles/security-auditor.md .claude/output-styles/

# Or create a styles repository
git clone company/claude-styles ~/.claude/output-styles
```

### Style Priority

1. Session-selected style (via `/output-style`)
2. User default (in `~/.claude/settings.json`)
3. Built-in default

### Setting Default Style

In `~/.claude/settings.json`:

```json
{
  "outputStyle": "explanatory"
}
```

## Tips and Best Practices

1. **Start with built-in**: Try `explanatory` or `learning` before creating custom styles

2. **Keep it focused**: Each style should have a clear purpose

3. **Use `keep-coding-instructions: true`**: Unless you specifically want a non-coding assistant

4. **Test iteratively**: Refine style instructions based on actual output

5. **Combine with CLAUDE.md**: Styles for communication, CLAUDE.md for project context

## Official Documentation

- [Output Styles Guide](https://code.claude.com/docs/en/output-styles)
