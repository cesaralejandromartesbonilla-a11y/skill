#!/usr/bin/env python3
"""launch_electron_cdp.py - Helper to launch Electron apps with CDP remote debugging

Finds installed instances of common Electron apps (VS Code, Discord, Slack, Obsidian)
and launches them with `--remote-debugging-port=<port>` enabled.
"""

import argparse
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Known Electron app executable locations on Windows
KNOWN_WINDOWS_APPS = {
    "vscode": [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
    "discord": [
        os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Discord\app-*\Discord.exe"),
    ],
    "slack": [
        os.path.expandvars(r"%LOCALAPPDATA%\slack\slack.exe"),
    ],
    "obsidian": [
        os.path.expandvars(r"%LOCALAPPDATA%\Obsidian\Obsidian.exe"),
    ],
    "postman": [
        os.path.expandvars(r"%LOCALAPPDATA%\Postman\Postman.exe"),
    ],
}


def find_executable(app_name: str) -> str | None:
    """Locates the executable path for the requested Electron app."""
    # Check PATH first
    in_path = shutil.which(app_name)
    if in_path:
        return in_path

    if sys.platform == "win32":
        candidates = KNOWN_WINDOWS_APPS.get(app_name.lower(), [])
        for candidate in candidates:
            if "*" in candidate:
                parts = candidate.split("*")
                base = Path(parts[0])
                if base.parent.is_dir():
                    matches = list(base.parent.glob(base.name + "*" + parts[1]))
                    if matches:
                        return str(matches[0])
            elif Path(candidate).is_file():
                return candidate

    return None


def launch_with_cdp(app_name: str, port: int = 9222) -> bool:
    """Launches the app with remote debugging port flag."""
    exe = find_executable(app_name)
    if not exe:
        print(f"[ERROR] Could not find executable for app '{app_name}'.")
        print("Please provide the full path to the executable manually.")
        return False

    cmd = [exe, f"--remote-debugging-port={port}"]
    print(f"[LAUNCH] Starting {app_name} with CDP on port {port}...")
    print(f"         Command: {' '.join(cmd)}")

    try:
        # Launch detached process
        if sys.platform == "win32":
            subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            subprocess.Popen(cmd, start_new_session=True)

        print(f"[SUCCESS] {app_name} launched. Ready to connect via:")
        print(f"          npx agent-browser connect {port}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to launch: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch Electron desktop apps with CDP remote debugging"
    )
    parser.add_argument(
        "app",
        choices=["vscode", "discord", "slack", "obsidian", "postman"],
        help="Target Electron application to launch",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9222,
        help="CDP debugging port (default: 9222)",
    )

    args = parser.parse_args()
    success = launch_with_cdp(args.app, port=args.port)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
