# Part 5: Keyboard Shortcuts

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              KEYBOARD SHORTCUTS                                      │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Legend:  ⌃ = Control    ⌘ = Command (Mac)    ⌥ = Option/Alt    ⇧ = Shift           │
│                                                                                      │
│  ESSENTIAL                           Linux/Windows         macOS                     │
│  ──────────────────────────────────────────────────────────────────────────────────  │
│  Cancel / Interrupt Claude           Ctrl + C              ⌃C                        │
│  Exit Claude Code                    Ctrl + D              ⌃D                        │
│  Clear screen                        Ctrl + L              ⌃L  or  ⌘K               │
│  Suspend (resume with `fg`)          Ctrl + Z              ⌃Z                        │
│                                                                                      │
│  NAVIGATION                          Linux/Windows         macOS                     │
│  ──────────────────────────────────────────────────────────────────────────────────  │
│  Navigate prompt history             ↑ / ↓                 ↑ / ↓                     │
│  Search prompt history               Ctrl + R              ⌃R                        │
│  Autocomplete paths/commands         Tab                   Tab                       │
│  Move to previous word               Ctrl + ←              ⌥←                        │
│  Move to next word                   Ctrl + →              ⌥→                        │
│                                                                                      │
│  EDITING                             Linux/Windows         macOS                     │
│  ──────────────────────────────────────────────────────────────────────────────────  │
│  Move to beginning of line           Ctrl + A              ⌃A  or  ⌘←               │
│  Move to end of line                 Ctrl + E              ⌃E  or  ⌘→               │
│  Delete word before cursor           Ctrl + W              ⌃W  or  ⌥⌫               │
│  Delete entire line                  Ctrl + U              ⌃U                        │
│  Delete word after cursor            Ctrl + Del            ⌥D  or  ⌥⌦               │
│  Undo                                Ctrl + _              ⌃_                        │
│  Yank (paste deleted text)           Ctrl + Y              ⌃Y                        │
│  Yank-pop (cycle kill ring)          Alt + Y               ⌥Y                        │
│  Open external editor                Ctrl + G              ⌃G                        │
│                                                                                      │
│  MULTI-LINE INPUT                    Linux/Windows         macOS                     │
│  ──────────────────────────────────────────────────────────────────────────────────  │
│  New line (continue input)           Shift + Enter         ⇧↵                        │
│  Submit prompt                       Enter                 ↵                         │
│  Stash prompt                        Ctrl + S              ⌃S                        │
│                                                                                      │
│  SESSION & MODE                      Linux/Windows         macOS                     │
│  ──────────────────────────────────────────────────────────────────────────────────  │
│  View transcript                     Ctrl + O              ⌃O                        │
│  Toggle thinking mode                Alt + T               ⌥T                        │
│  Switch model inline                 Alt + P               ⌥P                        │
│  Toggle permission mode              Shift + Tab           ⇧Tab                      │
│  Enter plan mode                     Shift + Tab (in plan) ⇧Tab                      │
│  Toggle fast mode                    /fast                 /fast                      │
│                                                                                      │
│  BACKGROUND TASKS                    Linux/Windows         macOS                     │
│  ──────────────────────────────────────────────────────────────────────────────────  │
│  Background running task             Ctrl + B              ⌃B                        │
│  Paste image from clipboard          Alt + V               ⌥V  or  ⌘V (iTerm2)      │
│                                                                                      │
│  PERMISSIONS                         All Platforms                                   │
│  ──────────────────────────────────────────────────────────────────────────────────  │
│  Accept permission request           y                                               │
│  Deny permission request             n                                               │
│  Accept all similar this session     a                                               │
│                                                                                      │
│  CLIPBOARD (Terminal)                Linux/Windows         macOS                     │
│  ──────────────────────────────────────────────────────────────────────────────────  │
│  Copy                                Ctrl + Shift + C      ⌘C                        │
│  Paste                               Ctrl + Shift + V      ⌘V                        │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

**Customizable keybindings:** Run `/keybindings` to customise keyboard shortcuts per context, create chord sequences, and personalise your workflow. See the [keybindings documentation](https://code.claude.com/docs/en/keybindings).

**Note for macOS users:** Most terminal emulators (Terminal.app, iTerm2, Warp) support both
the Ctrl-based shortcuts (standard Unix) and the Cmd-based shortcuts. The Ctrl shortcuts
work universally across all platforms.
