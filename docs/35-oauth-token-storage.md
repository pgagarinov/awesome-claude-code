# Part 35: OAuth Token Storage

## Overview

When using Claude Code with a Max or Teams subscription, authentication is handled via OAuth. Claude Code stores OAuth tokens in the **macOS Keychain** (or the platform's native credential store), not as plaintext files on disk.

## Storage Location

### macOS Keychain Entries

Claude Code creates Keychain entries with the service name pattern:

```
Claude Code-credentials-<hash>
```

Where `<hash>` is the **first 8 characters of the SHA-256 hash** of the `CLAUDE_CONFIG_DIR` path.

For the default config directory (`~/.claude`), the entry is simply:

```
Claude Code-credentials
```

(no suffix).

### Hash Derivation

```bash
# Compute the keychain suffix for a given config directory
echo -n "$CLAUDE_CONFIG_DIR" | shasum -a 256 | head -c 8
```

For example, if `CLAUDE_CONFIG_DIR=/Users/you/.claude-myprofile`:

```bash
echo -n "/Users/you/.claude-myprofile" | shasum -a 256 | head -c 8
# outputs something like: a1b2c3d4
```

The corresponding Keychain entry would be `Claude Code-credentials-a1b2c3d4`.

### Multiple Config Directories

If you use multiple config directories (via `CLAUDE_CONFIG_DIR`), each gets its own Keychain entry with a unique hash suffix. This allows independent OAuth sessions per profile.

## Token Structure

Each Keychain entry stores a JSON object:

```json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1234567890
  }
}
```

| Field | Prefix | Purpose |
|---|---|---|
| `accessToken` | `sk-ant-oat01-` | Bearer token for API calls; short-lived |
| `refreshToken` | `sk-ant-ort01-` | Used to obtain new access tokens when they expire |

The same entry may also contain MCP OAuth data under a separate `mcpOAuth` key if MCP servers requiring authentication are configured.

## Getting `CLAUDE_CODE_OAUTH_TOKEN` from `CLAUDE_CONFIG_DIR` (macOS)

The `CLAUDE_CODE_OAUTH_TOKEN` environment variable can be set to authenticate Claude Code without interactive login. To extract it from the Keychain given a `CLAUDE_CONFIG_DIR`:

### One-liner

```bash
export CLAUDE_CODE_OAUTH_TOKEN=$(
  security find-generic-password \
    -s "Claude Code-credentials-$(echo -n "$CLAUDE_CONFIG_DIR" | shasum -a 256 | head -c 8)" \
    -w \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['claudeAiOauth']['accessToken'])"
)
```

### Step by step

```bash
# 1. Compute the Keychain suffix from CLAUDE_CONFIG_DIR
SUFFIX=$(echo -n "$CLAUDE_CONFIG_DIR" | shasum -a 256 | head -c 8)

# 2. Extract the full credentials JSON from macOS Keychain
CREDS_JSON=$(security find-generic-password -s "Claude Code-credentials-$SUFFIX" -w)

# 3. Parse out just the access token
export CLAUDE_CODE_OAUTH_TOKEN=$(
  echo "$CREDS_JSON" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['claudeAiOauth']['accessToken'])"
)

# 4. Verify
echo "$CLAUDE_CODE_OAUTH_TOKEN"
# Should print: sk-ant-oat01-...
```

### For the default config directory (`~/.claude`)

The default directory uses the unsuffixed Keychain entry:

```bash
export CLAUDE_CODE_OAUTH_TOKEN=$(
  security find-generic-password -s "Claude Code-credentials" -w \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['claudeAiOauth']['accessToken'])"
)
```

### Shell helper function

Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
claude-oauth-token() {
  local config_dir="${1:-$CLAUDE_CONFIG_DIR}"
  local suffix service_name
  if [ -z "$config_dir" ] || [ "$config_dir" = "$HOME/.claude" ]; then
    service_name="Claude Code-credentials"
  else
    suffix=$(echo -n "$config_dir" | shasum -a 256 | head -c 8)
    service_name="Claude Code-credentials-$suffix"
  fi
  security find-generic-password -s "$service_name" -w \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['claudeAiOauth']['accessToken'])"
}

# Usage:
#   claude-oauth-token                          # uses current CLAUDE_CONFIG_DIR
#   claude-oauth-token ~/.claude-myprofile      # explicit config dir
#   export CLAUDE_CODE_OAUTH_TOKEN=$(claude-oauth-token ~/.claude-myprofile)
```

## Extracting the Full Credentials JSON

### For a custom config directory

```bash
SUFFIX=$(echo -n "$CLAUDE_CONFIG_DIR" | shasum -a 256 | head -c 8)
security find-generic-password -s "Claude Code-credentials-$SUFFIX" -w
```

### For the default config directory

```bash
security find-generic-password -s "Claude Code-credentials" -w
```

## Account Metadata

Separately from the Keychain, account metadata (not the token itself) is stored in `$CLAUDE_CONFIG_DIR/.claude.json` under the `oauthAccount` key:

```json
{
  "oauthAccount": {
    "accountUuid": "...",
    "emailAddress": "...",
    "organizationUuid": "...",
    "billingType": "stripe_subscription",
    "displayName": "..."
  }
}
```

This is used for display purposes and usage tracking, not for authentication.

## Listing All Claude Code Keychain Entries

```bash
security dump-keychain 2>/dev/null | grep -A2 "Claude Code-credentials"
```

## Security Notes

- Tokens are stored in the OS credential store, protected by your login keychain password
- Access tokens are short-lived and automatically refreshed
- Treat extracted tokens as secrets — anyone with the access token can make API calls as your account
- On Linux, Claude Code uses `libsecret` (GNOME Keyring / KDE Wallet) instead of macOS Keychain
