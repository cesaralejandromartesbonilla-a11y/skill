"""Unit tests for tools/validate_skill.py using Python unittest."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.validate_skill import SkillValidator, validate_skill_file


class TestSkillValidator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.skill_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_skill(self, filename="SKILL.md", content=""):
        file_path = self.skill_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_valid_skill(self):
        content = """---
name: sample-skill
description: Use when needing to validate sample skill behavior in unit tests
---

# Sample Skill

## Overview
A lightweight sample skill for testing.

## When to Use
Use when verifying validation rules in automated test suites.
"""
        skill_path = self._create_skill(content=content)
        validator = SkillValidator(skill_path)
        report = validator.validate()

        self.assertTrue(report["valid"], f"Expected valid skill, got errors: {report['errors']}")
        self.assertEqual(len(report["errors"]), 0)
        self.assertEqual(report["name"], "sample-skill")

    def test_missing_frontmatter(self):
        content = """# No Frontmatter Skill

Just some markdown text without YAML frontmatter.
"""
        skill_path = self._create_skill(content=content)
        validator = SkillValidator(skill_path)
        report = validator.validate()

        self.assertFalse(report["valid"])
        self.assertTrue(any("frontmatter" in err.lower() for err in report["errors"]))

    def test_invalid_name(self):
        content = """---
name: Invalid Name (with parens & spaces!)
description: Use when testing invalid names
---
# Content
"""
        skill_path = self._create_skill(content=content)
        validator = SkillValidator(skill_path)
        report = validator.validate()

        self.assertFalse(report["valid"])
        self.assertTrue(any("name" in err.lower() for err in report["errors"]))

    def test_description_missing_use_when(self):
        content = """---
name: good-name
description: This description does not start with the mandatory prefix.
---
# Content
"""
        skill_path = self._create_skill(content=content)
        validator = SkillValidator(skill_path)
        report = validator.validate()

        # Should generate a warning or error about 'Use when'
        all_issues = report["errors"] + report["warnings"]
        self.assertTrue(any("use when" in issue.lower() for issue in all_issues))

    def test_workflow_spoiler_detection(self):
        content = """---
name: workflow-spoiler
description: Use when doing TDD - write test first, watch it fail, write minimal code, refactor
---
# Content
"""
        skill_path = self._create_skill(content=content)
        validator = SkillValidator(skill_path)
        report = validator.validate()

        # Should flag workflow spoiler
        self.assertTrue(any("spoiler" in w.lower() or "workflow" in w.lower() for w in report["warnings"]))

    def test_frontmatter_length_limit(self):
        huge_desc = "Use when " + ("a" * 1100)
        content = f"""---
name: huge-skill
description: {huge_desc}
---
# Content
"""
        skill_path = self._create_skill(content=content)
        validator = SkillValidator(skill_path)
        report = validator.validate()

        self.assertFalse(report["valid"])
        self.assertTrue(any("1024" in err or "length" in err.lower() or "character" in err.lower() for err in report["errors"]))

    def test_missing_required_headers(self):
        content = """---
name: missing-headers
description: Use when testing missing headers
---
Only raw text without H1 header or Overview.
"""
        skill_path = self._create_skill(content=content)
        validator = SkillValidator(skill_path)
        report = validator.validate()

        all_issues = report["errors"] + report["warnings"]
        self.assertTrue(any("header" in issue.lower() or "overview" in issue.lower() for issue in all_issues))


if __name__ == "__main__":
    unittest.main()
