#!/usr/bin/env python3
"""agent_browser_runner.py - Python Automation Wrapper for agent-browser CLI

Wraps vercel-labs/agent-browser to enable ultra-lightweight web and desktop
automation using accessibility trees, ref IDs (@e1, @e2), annotated screenshots,
and CDP connections with minimal token footprint (<10% vs raw DOM HTML).
"""

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class AccessibilityNode:
    """Represents an interactive element extracted from an accessibility snapshot."""

    ref: str
    role: str
    name: str
    extra: Dict[str, Any] = field(default_factory=dict)


class AgentBrowserRunner:
    """High-level programmatic wrapper for the agent-browser CLI."""

    def __init__(
        self,
        binary_path: Optional[str] = None,
        use_npx: bool = True,
        default_session: Optional[str] = None,
        timeout: int = 30,
    ):
        self.use_npx = use_npx
        self.default_session = default_session
        self.timeout = timeout

        if binary_path:
            self.base_cmd = [binary_path]
        else:
            # Check if agent-browser is available globally
            global_bin = shutil.which("agent-browser")
            if global_bin:
                self.base_cmd = [global_bin]
            elif shutil.which("npx"):
                self.base_cmd = ["npx", "-y", "agent-browser"]
            else:
                self.base_cmd = ["agent-browser"]

    def build_command(self, args: List[str], session: Optional[str] = None) -> List[str]:
        """Constructs the command argument list including optional session flag."""
        cmd = list(self.base_cmd)
        active_session = session or self.default_session
        if active_session:
            cmd.extend(["--session", active_session])
        cmd.extend(args)
        return cmd

    def execute(
        self,
        args: List[str],
        session: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Executes an agent-browser command synchronously and captures structured results."""
        cmd = self.build_command(args, session=session)
        actual_timeout = timeout or self.timeout

        try:
            # Use shell=True on Windows if executing npx cmd
            use_shell = sys.platform == "win32" and ("npx" in cmd[0] or cmd[0] == "npx")
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=actual_timeout,
                shell=use_shell,
                encoding="utf-8",
                errors="replace",
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()

            # Filter out npx download banners if present
            filtered_stdout = "\n".join(
                line for line in stdout.splitlines() if not line.startswith("npm notice")
            ).strip()

            return {
                "success": proc.returncode == 0,
                "returncode": proc.returncode,
                "output": filtered_stdout,
                "error": stderr,
                "command": cmd,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "output": "",
                "error": f"Command timed out after {actual_timeout}s: {' '.join(cmd)}",
                "command": cmd,
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "output": "",
                "error": str(e),
                "command": cmd,
            }

    def parse_snapshot_refs(self, snapshot_text: str) -> List[AccessibilityNode]:
        """Parses elements containing ref identifiers [@eN] from an accessibility snapshot."""
        nodes: List[AccessibilityNode] = []
        # Matches patterns like: - button "Submit" [@e2] or - link "Home" [@e1]
        pattern = re.compile(r"-\s+([a-zA-Z0-9_\-]+)\s+\"([^\"]*)\"\s+\[(@e\d+)\]")

        for line in snapshot_text.splitlines():
            line_str = line.strip()
            match = pattern.search(line_str)
            if match:
                role = match.group(1)
                name = match.group(2)
                ref = match.group(3)
                nodes.append(AccessibilityNode(ref=ref, role=role, name=name))
            else:
                # Alternative format fallback: role [@eN] or [name] [@eN]
                fallback_match = re.search(r"(\w+)\s+.*\[(@e\d+)\]", line_str)
                if fallback_match:
                    role = fallback_match.group(1)
                    ref = fallback_match.group(2)
                    nodes.append(AccessibilityNode(ref=ref, role=role, name=""))

        return nodes

    def open_url(self, url: str, session: Optional[str] = None) -> Dict[str, Any]:
        """Navigates the browser to the specified URL."""
        res = self.execute(["open", url], session=session)
        if res["success"]:
            # Wait for network idle
            self.execute(["wait", "--load", "networkidle"], session=session, timeout=15)
        return res

    def snapshot(self, interactive_only: bool = True, session: Optional[str] = None) -> Dict[str, Any]:
        """Captures an accessibility snapshot. Returns text and parsed refs."""
        args = ["snapshot", "-i"] if interactive_only else ["snapshot"]
        res = self.execute(args, session=session)
        if res["success"]:
            nodes = self.parse_snapshot_refs(res["output"])
            res["nodes"] = [
                {"ref": n.ref, "role": n.role, "name": n.name} for n in nodes
            ]
        return res

    def click(self, target_ref_or_selector: str, session: Optional[str] = None) -> Dict[str, Any]:
        """Clicks an element by ref (e.g. '@e2') or selector."""
        return self.execute(["click", target_ref_or_selector], session=session)

    def fill(self, target_ref: str, text: str, session: Optional[str] = None) -> Dict[str, Any]:
        """Clears and fills an input element with text."""
        return self.execute(["fill", target_ref, text], session=session)

    def screenshot(
        self,
        output_path: str | Path,
        annotate: bool = False,
        full_page: bool = False,
        session: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Captures a screenshot, optionally annotating element refs for vision models."""
        args = ["screenshot"]
        if annotate:
            args.append("--annotate")
        if full_page:
            args.append("--full")
        args.append(str(output_path))
        return self.execute(args, session=session)

    def get_errors(self, session: Optional[str] = None) -> Dict[str, Any]:
        """Fetches page and runtime error logs."""
        return self.execute(["errors"], session=session)

    def get_console(self, session: Optional[str] = None) -> Dict[str, Any]:
        """Fetches browser console log output."""
        return self.execute(["console"], session=session)

    def eval_js(self, expression: str, session: Optional[str] = None) -> Dict[str, Any]:
        """Evaluates JavaScript in the active page context."""
        return self.execute(["eval", expression], session=session)

    def connect_cdp(self, port_or_url: str | int, session: Optional[str] = None) -> Dict[str, Any]:
        """Connects to a running Electron or Chromium instance via CDP."""
        return self.execute(["connect", str(port_or_url)], session=session)

    def close(self, session: Optional[str] = None, all_sessions: bool = False) -> Dict[str, Any]:
        """Closes the active browser session or all sessions."""
        args = ["close"]
        if all_sessions:
            args.append("--all")
        return self.execute(args, session=session)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="agent-browser CLI Runner & Automation Wrapper"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # check command
    subparsers.add_parser("check", help="Check agent-browser availability and version")

    # open command
    open_p = subparsers.add_parser("open", help="Open a URL")
    open_p.add_argument("url", help="Target URL to open")
    open_p.add_argument("--session", default=None, help="Session name")

    # snapshot command
    snap_p = subparsers.add_parser("snapshot", help="Capture accessibility snapshot")
    snap_p.add_argument("-a", "--all", action="store_true", help="Include all nodes, not just interactive")
    snap_p.add_argument("--session", default=None, help="Session name")
    snap_p.add_argument("--json", action="store_true", help="Output parsed refs in JSON")

    # click command
    click_p = subparsers.add_parser("click", help="Click an element by ref")
    click_p.add_argument("ref", help="Element ref e.g. @e1")
    click_p.add_argument("--session", default=None, help="Session name")

    # screenshot command
    ss_p = subparsers.add_parser("screenshot", help="Capture screenshot")
    ss_p.add_argument("output", help="Output path for image")
    ss_p.add_argument("--annotate", action="store_true", help="Annotate with ref badges")
    ss_p.add_argument("--session", default=None, help="Session name")

    # close command
    close_p = subparsers.add_parser("close", help="Close browser session")
    close_p.add_argument("--all", action="store_true", help="Close all sessions")
    close_p.add_argument("--session", default=None, help="Session name")

    args = parser.parse_args()

    runner = AgentBrowserRunner()

    if args.command == "check" or not args.command:
        res = runner.execute(["--version"])
        if res["success"]:
            print(f"[OK] agent-browser available: {res['output']}")
            return 0
        else:
            print(f"[ERROR] agent-browser check failed: {res['error']}")
            return 1

    if args.command == "open":
        print(f"Navigating to {args.url}...")
        res = runner.open_url(args.url, session=args.session)
        if res["success"]:
            print("[OK] Navigation complete.")
            return 0
        else:
            print(f"[ERROR] Navigation failed: {res['error']}")
            return 1

    if args.command == "snapshot":
        res = runner.snapshot(interactive_only=not args.all, session=args.session)
        if res["success"]:
            if args.json:
                print(json.dumps(res.get("nodes", []), indent=2, ensure_ascii=False))
            else:
                print(res["output"])
            return 0
        else:
            print(f"[ERROR] Snapshot failed: {res['error']}")
            return 1

    if args.command == "click":
        res = runner.click(args.ref, session=args.session)
        if res["success"]:
            print(f"[OK] Clicked {args.ref}")
            return 0
        else:
            print(f"[ERROR] Click failed: {res['error']}")
            return 1

    if args.command == "screenshot":
        res = runner.screenshot(args.output, annotate=args.annotate, session=args.session)
        if res["success"]:
            print(f"[OK] Screenshot saved to: {args.output}")
            return 0
        else:
            print(f"[ERROR] Screenshot failed: {res['error']}")
            return 1

    if args.command == "close":
        res = runner.close(session=args.session, all_sessions=args.all)
        print("[OK] Browser closed.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
