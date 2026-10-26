---
name: web-dogfooding
description: Use when systematically exploring and testing a web application to discover visual defects, broken links, UX friction, console errors, or regressions
license: MIT
metadata:
  version: "1.0"
  author: "Skill Hub"
---

# Web Dogfooding (Exploratory Web Testing)

## Overview
Automated exploratory testing for web applications using `agent-browser`. Instead of parsing massive raw HTML DOMs that waste context tokens, this skill navigates live websites through compact accessibility trees (`@e1`, `@e2`), annotated screenshots, and error telemetry to detect real-world issues.

## When to Use
- Auditing web apps before a release or pull request merge.
- Verifying staging deployments for broken links, responsive layout glitches, or console errors.
- Performing autonomous user-journey dogfooding on complex multi-page platforms.
- Capturing annotated evidence (screenshots and video) for bugs reported to engineering teams.

When NOT to use:
- Unit or integration testing of backend APIs (use standard test suites).
- Scraping high-volume static data (use specialized HTTP scrapers).

## Quick Reference Commands

Using the workspace runner:
```bash
# Verify browser readiness
python tools/agent_browser_runner.py check

# Open URL and inspect interactive accessibility tree
python tools/agent_browser_runner.py open https://example.com --session qa
python tools/agent_browser_runner.py snapshot --session qa

# Click an element by its accessibility ref
python tools/agent_browser_runner.py click @e2 --session qa

# Capture labeled screenshot for multimodal models
python tools/agent_browser_runner.py screenshot dogfood-output/step1.png --annotate --session qa

# Terminate session
python tools/agent_browser_runner.py close --session qa
```

Direct binary usage (via `npx agent-browser`):
```bash
agent-browser --session qa open https://myapp.com
agent-browser --session qa snapshot -i
agent-browser --session qa errors
agent-browser --session qa console
agent-browser --session qa close
```

## Exploration & Bug Hunting Strategy

```
  [1. Orient]      --> Open target URL, capture initial annotated screenshot & snapshot
        |
        v
  [2. Traverse]    --> Visit top-level navigation, forms, modale triggers, and buttons
        |
        v
  [3. Inspect]     --> Check console errors, broken HTTP requests, and visual overflows
        |
        v
  [4. Evidence]    --> Capture annotated screenshot for every discovered defect
        |
        v
  [5. Report]      --> Compile findings into dogfood_report_template.md
```

### 1. Orient
Navigate to the root URL and establish a named session to preserve cookies and state:
```bash
python tools/agent_browser_runner.py open <TARGET_URL> --session qa
```

### 2. Traverse
Systematically visit major sections:
- Forms and input validation (empty submissions, edge-case characters).
- Interactive navigation menus, tabs, and dropdowns.
- Responsiveness and layout balance across desktop/mobile viewport settings.

### 3. Inspect
Continuously inspect runtime logs:
```bash
npx agent-browser --session qa errors
npx agent-browser --session qa console
```

### 4. Evidence Standards
Every reported bug must be backed by reproducible proof:
- For static/visual defects: Annotated screenshot highlighting the element.
- For interactive errors: Repro steps referencing element IDs `@eN` and console logs.
- Use the standard report template in [templates/dogfood_report_template.md](templates/dogfood_report_template.md).

## Common Mistakes & Best Practices

| Anti-Pattern | Best Practice |
| :--- | :--- |
| Inspecting raw DOM HTML ($10,000+$ tokens) | Use `snapshot -i` (compact accessibility tree, $<500$ tokens) |
| Reporting vague bugs without screenshots | Always save annotated screenshots (`screenshot --annotate`) |
| Forgetting to close daemon sessions | Run `close` or `python tools/agent_browser_runner.py close` at the end |
| Testing as a bot with machine-speed bursts | Include small waits (`wait --load networkidle`) for React renders |
