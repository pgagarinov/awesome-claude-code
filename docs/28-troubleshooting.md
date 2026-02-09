# Part 28: Troubleshooting

## Installation Issues

### Windows Installation (WSL)

**OS/platform detection issues:**
```bash
# Set OS before installation
npm config set os linux

# Install with force flags (do NOT use sudo)
npm install -g @anthropic-ai/claude-code --force --no-os-check
```

**Node not found errors:**
```bash
# Check if using Windows or Linux Node
which npm    # Should show /usr/... not /mnt/c/...
which node   # Should show /usr/... not /mnt/c/...

# If pointing to Windows paths, install Node via nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

**nvm version conflicts:**

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

**"Claude Code on Windows requires git-bash" error:**

Install [Git for Windows](https://git-scm.com/downloads/win), then set path explicitly:
```powershell
$env:CLAUDE_CODE_GIT_BASH_PATH="C:\Program Files\Git\bin\bash.exe"
```

### Linux and macOS Installation

**Recommended: Native Installation**
```bash
# Install stable version
curl -fsSL https://claude.ai/install.sh | bash

# Install latest version
curl -fsSL https://claude.ai/install.sh | bash -s latest

# Install specific version
curl -fsSL https://claude.ai/install.sh | bash -s 1.0.58
```

Installs to `~/.local/bin/claude`. Ensure this is in your PATH.

**"command not found" after installation:**
```bash
# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

---

## Authentication Issues

### Repeated Login Prompts

```bash
# Logout and re-authenticate
/logout

# Close Claude Code, then restart
claude
```

### Persistent Authentication Failures

```bash
# Remove auth file and re-authenticate
rm -rf ~/.config/claude-code/auth.json
claude
```

---

## Permission Issues

### Repeated Permission Prompts

Use `/permissions` to configure auto-approval for trusted operations:

```bash
> /permissions
```

Or configure in `.claude/settings.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm test:*)",
      "Read(~/.zshrc)"
    ]
  }
}
```

See [Part 24: Permission Settings](24-permissions.md) for comprehensive configuration.

---

## Configuration File Locations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION FILE LOCATIONS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER LEVEL                                                                 │
│  ~/.claude/settings.json        User settings (permissions, model)          │
│  ~/.claude/CLAUDE.md            Personal memory for all projects           │
│  ~/.claude/settings.json        User settings (MCP servers, preferences)   │
│                                                                             │
│  PROJECT LEVEL                                                              │
│  .claude/settings.json          Project settings (shared via git)          │
│  .claude/settings.local.json    Local project settings (not committed)     │
│  .mcp.json                      Project MCP servers (shared via git)       │
│  CLAUDE.md                      Project memory (shared via git)            │
│  CLAUDE.local.md                Local project memory (not committed)       │
│                                                                             │
│  ENTERPRISE (managed)                                                       │
│  macOS: /Library/Application Support/ClaudeCode/                           │
│  Linux: /etc/claude-code/                                                  │
│  Windows: C:\Program Files\ClaudeCode\                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Resetting Configuration

```bash
# Reset all user settings and state
rm -rf ~/.claude/

# Reset project-specific settings
rm -rf .claude/
rm .mcp.json
```

---

## Performance Issues

### High CPU or Memory Usage

1. Use `/compact` regularly to reduce context size
2. Close and restart Claude Code between major tasks
3. Add large build directories to `.gitignore`

### Slow or Incomplete Search Results

**Install system ripgrep for better performance:**

```bash
# macOS
brew install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep

# Windows
winget install BurntSushi.ripgrep.MSVC

# Alpine Linux
apk add ripgrep

# Arch Linux
pacman -S ripgrep
```

Set environment variable to use system ripgrep:
```bash
export USE_BUILTIN_RIPGREP=0
```

### WSL Performance Issues

WSL disk read performance on `/mnt/c/` is slower. Solutions:

1. **Move project to Linux filesystem**: Use `/home/` instead of `/mnt/c/`
2. **Submit specific searches**: "Search for JWT validation in auth-service"
3. **Use native Windows**: Better file system performance

### Command Hangs or Freezes

1. Press `Ctrl+C` to cancel current operation
2. If unresponsive, close terminal and restart

---

## Terminal Scrolling Issues

### Problem

Terminal scrolls uncontrollably during Claude Code sessions, sometimes jumping to the top of output or scrolling rapidly on its own.

**Affected terminals:**
- VS Code integrated terminal
- Cursor IDE terminal
- iTerm2
- Windows terminals

**Reference**: [GitHub Issue #3648](https://github.com/anthropics/claude-code/issues/3648)

### iTerm2 Workaround

iTerm2 handles the scrolling issue better - resets to bottom instead of top.

**Recommended setting:**
1. Open iTerm2 > Settings (or press `Cmd + ,`)
2. Go to **Profiles** > **Terminal**
3. Under "Scrollback Lines", check **Unlimited**

### General Tips

- Start fresh sessions periodically (`claude` instead of `claude -c`)
- Use `/compact` to reduce context when sessions get long
- Type slowly when entering `/` slash commands

---

## IDE Integration Issues

### JetBrains IDE Not Detected (WSL2)

WSL2 NAT networking or Windows Firewall may block IDE detection.

**Option 1: Configure Windows Firewall**

Find WSL2 IP:
```bash
wsl hostname -I
# Example: 172.21.123.456
```

Open PowerShell as Administrator:
```powershell
New-NetFirewallRule -DisplayName "Allow WSL2 Internal Traffic" `
  -Direction Inbound -Protocol TCP -Action Allow `
  -RemoteAddress 172.21.0.0/16 -LocalAddress 172.21.0.0/16
```

**Option 2: Switch to mirrored networking**

Add to `.wslconfig` in Windows user directory:
```
[wsl2]
networkingMode=mirrored
```

Restart WSL: `wsl --shutdown`

### Escape Key Not Working in JetBrains Terminals

1. Go to Settings > Tools > Terminal
2. Either:
   - Uncheck "Move focus to the editor with Escape", or
   - Click "Configure terminal keybindings" and delete "Switch focus to Editor"

---

## Markdown Formatting Issues

### Missing Language Tags in Code Blocks

Ask Claude: "Add appropriate language tags to all code blocks in this markdown file"

Or use post-processing hooks (see [Part 13: Hooks](13-hooks.md)).

### Inconsistent Formatting

Document preferences in your `CLAUDE.md`:
```markdown
## Code Style
- Use 2-space indentation
- Always include language tags on code blocks
- Use fenced code blocks (```) not indented blocks
```

---

## Diagnostic Commands

### Check Installation Health

```bash
# Run diagnostic check
/doctor
```

### Report Bugs

```bash
# Report issue directly to Anthropic
/bug
```

### Check Session Status

```bash
# View context usage, session info
/status

# View context token breakdown
/context
```

---

## Getting More Help

1. Use `/doctor` to diagnose installation issues
2. Use `/bug` to report issues to Anthropic
3. Check [GitHub Issues](https://github.com/anthropics/claude-code/issues) for known problems
4. Ask Claude directly - it has built-in documentation access
5. See [Official Troubleshooting Guide](https://code.claude.com/docs/en/troubleshooting)
