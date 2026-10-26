---
name: electron-automator
description: Use when needing to automate, test, or interact with desktop Electron applications via Chrome DevTools Protocol connections
license: MIT
metadata:
  version: "1.0"
  author: "Skill Hub"
---

# Electron Desktop Automation

## Overview
Control and automate desktop applications built on Electron (such as VS Code, Discord, Slack, Obsidian, and Figma) using `agent-browser` connected over Chrome DevTools Protocol (CDP). Because Electron applications run on Chromium, they support full accessibility snapshots, element ref interaction, and screenshot annotations.

## When to Use
- Automating repetitive actions in desktop clients (e.g. VS Code, Slack, Obsidian).
- Running end-to-end user tests against Electron-based desktop installers.
- Capturing annotated screenshots and UI states of running desktop software.
- Extracting accessibility text and status indicators from desktop apps.

When NOT to use:
- Native non-Chromium apps (Win32, WPF, Cocoa, Qt native apps without embedded Chromium).
- Regular public websites (use `skills/web-dogfooding` or direct `agent-browser`).

## Quick Reference Commands

Launch application with remote debugging enabled:
```bash
# Helper launcher for common apps (VS Code, Discord, Slack, Obsidian)
python skills/electron-automator/scripts/launch_electron_cdp.py vscode --port 9223

# Or launch directly with native shell flags
"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe" --remote-debugging-port=9223
```

Connect and automate via `agent-browser`:
```bash
# Connect agent-browser to the CDP port
agent-browser connect 9223

# Inspect windows and internal webviews
agent-browser tab

# Capture interactive accessibility tree with refs
agent-browser snapshot -i

# Click or type into elements
agent-browser click @e4
agent-browser fill @e5 "Automated test text"

# Capture annotated screenshot of desktop app
agent-browser screenshot desktop_view.png --annotate
```

## Multi-Window & Webview Handling

Electron apps often embed multiple renderer processes and `<webview>` containers:
```bash
# List all active renderer targets
agent-browser tab

# Target switching by index or URL pattern
agent-browser tab 1
agent-browser tab --url "*settings*"
```

## Recommended Workflow

```
  [1. Quit existing instance] --> Ensure no background headless processes lock the user profile
              |
              v
  [2. Launch with --remote-debugging-port] --> Use launch_electron_cdp.py or direct binary
              |
              v
  [3. Connect agent-browser]  --> agent-browser connect <port>
              |
              v
  [4. Snapshot & Interact]   --> Discover elements with snapshot -i and interact via refs
```

## Common Mistakes & Troubleshooting

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `Connection refused` | App was launched without `--remote-debugging-port` | Fully quit app (check Task Manager / Activity Monitor) and relaunch with flag. |
| Elements missing in snapshot | Elements reside inside an embedded `<webview>` or secondary window | Run `agent-browser tab` to inspect all targets and switch with `agent-browser tab <N>`. |
| Cannot type in custom inputs | Custom canvas or non-standard DOM input elements | Use `agent-browser keyboard type "text"` to send real keyboard events at current focus. |
