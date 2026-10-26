"""Unit tests for tools/benchmark_skills.py using Python unittest."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.benchmark_skills import SkillBenchmarkAnalyzer


class TestSkillBenchmark(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create two sample skills
        skill1_dir = self.root / "skill-compact"
        skill1_dir.mkdir(parents=True)
        (skill1_dir / "SKILL.md").write_text(
            """---
name: skill-compact
description: Use when needing a compact skill for benchmarks
---

# Skill Compact

## Overview
Compact test skill.

## When to Use
Use when running benchmark tests.
""",
            encoding="utf-8",
        )

        skill2_dir = self.root / "skill-heavy"
        skill2_dir.mkdir(parents=True)
        (skill2_dir / "SKILL.md").write_text(
            """---
name: skill-heavy
description: This description does not have prefix and describes the entire process first step 1 then step 2 then step 3
---

# Heavy Skill
"""
            + ("Some very repetitive content line.\n" * 200),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_benchmark_metrics(self):
        analyzer = SkillBenchmarkAnalyzer(self.root)
        results = analyzer.analyze_all()

        self.assertEqual(len(results), 2)

        compact_res = next(r for r in results if r["name"] == "skill-compact")
        heavy_res = next(r for r in results if r["name"] == "skill-heavy")

        # Compact should have a higher SDO score than heavy
        self.assertGreater(compact_res["sdo_score"], heavy_res["sdo_score"])
        # Heavy should have more tokens than compact
        self.assertGreater(heavy_res["tokens_est"], compact_res["tokens_est"])

    def test_markdown_report_generation(self):
        analyzer = SkillBenchmarkAnalyzer(self.root)
        analyzer.analyze_all()
        md_report = analyzer.generate_markdown_report()

        self.assertIn("# Benchmark de Desempeño y Huella de Skills", md_report)
        self.assertIn("skill-compact", md_report)
        self.assertIn("skill-heavy", md_report)


if __name__ == "__main__":
    unittest.main()
