"""Unit tests for tools/agent_browser_runner.py using Python unittest."""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.agent_browser_runner import AgentBrowserRunner, AccessibilityNode


class TestAgentBrowserRunner(unittest.TestCase):
    def setUp(self):
        self.runner = AgentBrowserRunner(use_npx=True)

    def test_build_command_basic(self):
        cmd = self.runner.build_command(["open", "https://example.com"])
        self.assertIn("open", cmd)
        self.assertIn("https://example.com", cmd)

    def test_build_command_with_session(self):
        cmd = self.runner.build_command(["snapshot", "-i"], session="qa-session")
        self.assertIn("--session", cmd)
        self.assertIn("qa-session", cmd)
        self.assertIn("snapshot", cmd)

    def test_parse_snapshot_interactive_refs(self):
        sample_snapshot = """
- document:
  - heading "Welcome" [level=1]
  - link "Learn More" [@e1]
  - button "Submit Form" [@e2]
  - textbox "Username" [@e3]
"""
        nodes = self.runner.parse_snapshot_refs(sample_snapshot)
        self.assertEqual(len(nodes), 3)

        self.assertEqual(nodes[0].ref, "@e1")
        self.assertEqual(nodes[0].role, "link")
        self.assertEqual(nodes[0].name, "Learn More")

        self.assertEqual(nodes[1].ref, "@e2")
        self.assertEqual(nodes[1].role, "button")
        self.assertEqual(nodes[1].name, "Submit Form")

        self.assertEqual(nodes[2].ref, "@e3")
        self.assertEqual(nodes[2].role, "textbox")
        self.assertEqual(nodes[2].name, "Username")

    @patch("subprocess.run")
    def test_execute_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Page title: Example Domain\n",
            stderr="",
        )
        result = self.runner.execute(["get", "title"])
        self.assertTrue(result["success"])
        self.assertIn("Example Domain", result["output"])
        self.assertEqual(result["returncode"], 0)

    @patch("subprocess.run")
    def test_execute_failure(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: Element @e99 not found",
        )
        result = self.runner.execute(["click", "@e99"])
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])


if __name__ == "__main__":
    unittest.main()
