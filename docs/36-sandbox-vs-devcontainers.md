# Claude Code Sandboxing: Native Sandbox vs Dev Containers

## The Problem

Claude Code operates on a permission-based model by default — it asks for approval before running commands or modifying files. This creates two competing problems:

- **Approval fatigue:** Repeatedly clicking "approve" leads to reduced attention and paradoxically less security, as users stop scrutinizing what they're approving.
- **Reduced productivity:** Constant interruptions slow down development workflows and limit Claude Code's ability to work autonomously.

The blunt alternative, `--dangerously-skip-permissions`, removes all safety guardrails entirely. Sandboxing offers a middle path: define boundaries upfront, then let Claude work freely within them. Anthropic's internal usage found that sandboxing reduces permission prompts by approximately 84%.

---

## Option 1: Native Sandboxing (Built-in `/sandbox`)

### How It Works

Native sandboxing uses OS-level security primitives — **Seatbelt** on macOS and **bubblewrap** on Linux/WSL2 — to enforce restrictions directly on the host machine. These primitives operate at the kernel level, meaning all child processes spawned by Claude Code's commands inherit the same security boundaries.

Enable it by typing `/sandbox` in a Claude Code session and selecting a sandbox mode.

### Two Layers of Isolation

Effective sandboxing requires both filesystem and network isolation working together:

**Filesystem isolation** restricts which directories Claude Code can read from and write to. By default, writes are limited to the current working directory and its subdirectories. Reads are unrestricted by default but can be hardened with deny rules in `settings.json`.

**Network isolation** restricts which domains processes can connect to. Internet access is routed through a proxy server running outside the sandbox that enforces domain restrictions. Without network isolation, a compromised agent could exfiltrate sensitive files like SSH keys. Without filesystem isolation, a compromised agent could escape the sandbox and gain network access.

### Sandbox Modes

- **Auto-allow mode:** Bash commands that stay within sandbox boundaries run automatically without requiring permission. Commands that cannot be sandboxed (e.g., those needing network access to non-allowed hosts) fall back to the regular permission flow.

### Strengths

- Zero setup on macOS (works out of the box)
- Minimal performance overhead (no virtualization layer)
- Granular control over allowed directories and network hosts
- Stays within your normal development environment
- Low friction — enable with `/sandbox` and keep working

### Limitations

- Reads are unrestricted by default (agent can read `~/.ssh`, `~/.aws`, etc.) — requires manual deny rules to harden
- Network filtering doesn't inspect traffic content, only restricts domains
- Broad domain allowlists (e.g., `github.com`) may enable data exfiltration
- Domain fronting can potentially bypass network filtering
- The `allowUnixSockets` configuration can inadvertently grant access to system services that bypass the sandbox
- Process-level isolation only — not a hard VM boundary

### Best For

Interactive pair-programming sessions where you're watching Claude's output and want minimal friction with solid default protections.

---

## Option 2: Dev Containers (Docker-based)

### How It Works

Dev containers run Claude Code inside a Docker container, providing a fully isolated development environment separated from the host system. Anthropic provides a reference devcontainer setup with a `devcontainer.json`, `Dockerfile`, and `init-firewall.sh` that establishes network security rules.

The container's enhanced security measures allow running `claude --dangerously-skip-permissions` to bypass permission prompts for unattended operation. The agent literally cannot see the host filesystem beyond what is explicitly mounted.

### What Gets Isolated

- **Filesystem:** Host files are inaccessible; only mounted directories are visible
- **Processes:** Fully isolated from host processes
- **Package installations:** Stay within the container
- **Network:** Configurable via firewall rules (full outbound by default — must be restricted manually)

### Strengths

- Hard filesystem boundary — even if Claude goes off the rails, it's trapped inside the container
- Full process isolation from the host
- Disposable environments that can be torn down and rebuilt
- Consistent across team members (new developers get a fully configured environment in minutes)
- Well-suited for CI/CD pipelines and autonomous workflows
- Compatible with VS Code Dev Containers extension for seamless IDE integration
- Session persistence through Docker volumes (command history, configurations survive container restarts)

### Limitations

- More setup friction than native sandboxing (requires Docker, devcontainer config)
- Network is not sandboxed by default — requires explicit firewall configuration
- Performance overhead from filesystem sharing between host and container
- Does not prevent exfiltration of anything accessible inside the container, including Claude Code credentials
- Requires trusted repositories — a malicious project inside the container still has full access within it

### Best For

Autonomous/unattended workflows, CI/CD pipelines, security audits, untrusted code review, and multi-client project isolation.

---

## The Docker Root Problem

A critical consideration for dev container security: Docker containers run processes as root by default.

### Why This Matters

If a container process runs as root and a container escape vulnerability is exploited, the attacker lands on the host as root. Docker's isolation relies on Linux namespaces and cgroups, which have had breakout vulnerabilities historically. Root inside the container makes those exploits significantly more dangerous.

Even without a kernel exploit, root inside a container can modify system files, install packages system-wide, and change permissions — expanding the blast radius of any bug or malicious action.

### Mitigations

**Run container processes as a non-root user.** Well-designed Claude Code devcontainer setups already do this. Anthropic's reference devcontainer uses a non-root `vscode` user (`containerUser: "vscode"`). The container process should always run as an unprivileged user, even if sudo is available inside the container.

**Use rootless Docker or Podman.** Rootless mode runs the entire Docker daemon as a non-root user on the host. Podman is natively rootless and is supported by several Claude Code sandbox projects. This eliminates the class of attacks where Docker daemon access equals host root access.

**Never mount the Docker socket.** Mounting `/var/run/docker.sock` into a container gives the container process full control over the Docker daemon, which effectively means root access to the host. This is a complete sandbox escape.

**Use `--userns-remap`.** This maps container root (UID 0) to an unprivileged UID on the host, so even a container escape as root lands as a non-privileged user.

**Consider microVM-based solutions.** Docker's newer Sandboxes feature uses microVM-based isolation, adding a hard security boundary. Even a container escape leaves you inside a lightweight VM, not on the host. This is the strongest isolation model available within the Docker ecosystem.

---

## Comparison Summary

| Dimension | Native Sandbox | Dev Container |
|---|---|---|
| **Isolation level** | Process-level (OS primitives) | Container-level (Docker) |
| **Filesystem** | Restrict writes; reads configurable via deny rules | Hard boundary — only mounted dirs visible |
| **Network** | Domain allowlist via proxy | Full outbound by default (must configure firewall) |
| **Process isolation** | Inherited by child processes only | Full isolation from host |
| **Setup** | `/sandbox` command | Docker + devcontainer configuration |
| **Performance** | Native | Near-native; filesystem sharing adds overhead |
| **Permission model** | Auto-allow within boundaries | Typically `--dangerously-skip-permissions` |
| **Disposability** | N/A (runs on host) | Containers can be torn down and rebuilt |
| **Team consistency** | Per-developer configuration | Shared, reproducible environment |
| **Root risk** | N/A (runs as your user) | Must configure non-root user; consider rootless Docker |
| **Best for** | Interactive pair-programming | Autonomous workflows, CI/CD, untrusted code |

---

## Choosing Your Approach

**Use native sandboxing** if Claude Code is your pair programmer, you're actively watching its output, and you want minimal friction with solid default protections. This covers the vast majority of interactive development work.

**Use dev containers** if you're running Claude Code autonomously, working with untrusted repositories, need full isolation for security audits, or want consistent environments across a team. Harden by running as a non-root user, configuring network firewall rules, and considering rootless Docker or Podman.

**Use microVMs or full VMs** if you need the strongest isolation guarantees — for instance, running Claude Code against untrusted code where a container escape would be catastrophic. The VM boundary is the real security boundary; everything else provides defense-in-depth.

The key insight: these approaches are not mutually exclusive. You can run native sandboxing inside a dev container for layered defense, or graduate from native sandboxing to containers as your autonomy needs increase.

---

*Last updated: February 2026. Based on Anthropic's official documentation, the Anthropic engineering blog, and community implementations including Trail of Bits' devcontainer configurations.*
