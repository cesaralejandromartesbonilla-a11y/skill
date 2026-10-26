#!/usr/bin/env python3
"""validate_skill.py - Automated Validator and Quality Gates for Agent Skills (SKILL.md)

Verifies compliance with Anthropic and Superpowers standards:
1. Frontmatter YAML presence, syntax, and size limit (<= 1024 chars).
2. Name format (alphanumeric, hyphens).
3. Description follows "Use when..." and avoids workflow spoilers/leaks.
4. Core structural sections (H1 title, Overview, When to Use).
5. Internal relative links and referenced script paths exist.
"""

import argparse
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


# Heuristic patterns for workflow spoilers in skill descriptions
WORKFLOW_SPOILER_PATTERNS = [
    r"\b(?:first|then|next|finally)\b.*\b(?:then|next|finally)\b",
    r"write\s+test.*(?:fail|pass|refactor)",
    r"dispatch(?:es)?\s+subagent",
    r"code\s+review\s+between\s+tasks",
    r"step\s+\d+",
    r"->|→|==>",
    r"\bexecute\s+all\s+tasks\b",
]

NAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+$")


class SkillValidator:
    """Validates an individual SKILL.md file or skill directory against quality gates."""

    def __init__(self, target_path: Path):
        self.target_path = Path(target_path).resolve()
        if self.target_path.is_dir():
            self.skill_file = self.target_path / "SKILL.md"
        else:
            self.skill_file = self.target_path

        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.body: str = ""

    def validate(self) -> Dict[str, Any]:
        """Runs all validation gates and returns a detailed report."""
        self.errors.clear()
        self.warnings.clear()
        self.stats.clear()
        self.metadata.clear()
        self.body = ""

        if not self.skill_file.exists():
            self.errors.append(f"Skill file does not exist: {self.skill_file}")
            return self._build_report()

        try:
            content = self.skill_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = self.skill_file.read_text(encoding="latin-1")
                self.warnings.append("File encoded in non-UTF-8 charset; UTF-8 is required.")
            except Exception as e:
                self.errors.append(f"Failed to read file: {e}")
                return self._build_report()

        self.stats["total_chars"] = len(content)
        self.stats["total_lines"] = len(content.splitlines())
        self.stats["estimated_tokens"] = round(len(content) / 4)

        # 1. Frontmatter Validation
        self._validate_frontmatter(content)

        # 2. Markdown Structure Validation
        if self.body:
            self._validate_body_structure(self.body)

        # 3. Reference and Link Validation
        if self.body:
            self._validate_references(self.body)

        return self._build_report()

    def _validate_frontmatter(self, content: str) -> None:
        """Parses and audits the YAML frontmatter block."""
        match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$", content, re.DOTALL)
        if not match:
            self.errors.append("Missing YAML frontmatter delimited by '---' at the start of file.")
            self.body = content
            return

        raw_frontmatter = match.group(1)
        self.body = match.group(2)

        raw_fm_len = len(raw_frontmatter)
        self.stats["frontmatter_chars"] = raw_fm_len

        # Rule: Max 1024 characters total in frontmatter
        if raw_fm_len > 1024:
            self.errors.append(
                f"Frontmatter exceeds maximum size limit: {raw_fm_len} chars (maximum allowed: 1024 chars)."
            )

        # Parse YAML
        parsed = None
        if yaml:
            try:
                parsed = yaml.safe_load(raw_frontmatter)
            except Exception as e:
                self.errors.append(f"YAML frontmatter parsing error: {e}")
        else:
            # Fallback simple parser
            parsed = {}
            for line in raw_frontmatter.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    parsed[k.strip()] = v.strip().strip("\"'")

        if not isinstance(parsed, dict):
            self.errors.append("Frontmatter is not a valid YAML dictionary mapping.")
            return

        self.metadata = parsed

        # Audit 'name' field
        name = parsed.get("name")
        if not name:
            self.errors.append("Missing required frontmatter field: 'name'.")
        elif not isinstance(name, str):
            self.errors.append(f"'name' must be a string, got {type(name).__name__}.")
        else:
            if not NAME_REGEX.match(name):
                self.errors.append(
                    f"Invalid skill name '{name}'. Names must only contain letters, numbers, and hyphens (no spaces or special chars)."
                )

        # Audit 'description' field
        desc = parsed.get("description")
        if not desc:
            self.errors.append("Missing required frontmatter field: 'description'.")
        elif not isinstance(desc, str):
            self.errors.append(f"'description' must be a string, got {type(desc).__name__}.")
        else:
            self._validate_description(desc)

    def _validate_description(self, desc: str) -> None:
        """Audits the 'description' field for triggers and absence of spoilers."""
        desc_stripped = desc.strip()
        self.stats["description_chars"] = len(desc_stripped)

        # Rule: Starts with "Use when..."
        if not desc_stripped.lower().startswith("use when"):
            self.warnings.append(
                "Description should start with 'Use when...' to define clear triggering conditions."
            )

        # Rule: Recommended size <= 500 characters
        if len(desc_stripped) > 500:
            self.warnings.append(
                f"Description is {len(desc_stripped)} characters; recommended under 500 characters for optimal discovery."
            )

        # Rule: No workflow spoilers
        for pattern in WORKFLOW_SPOILER_PATTERNS:
            if re.search(pattern, desc_stripped, re.IGNORECASE):
                self.warnings.append(
                    f"Possible workflow spoiler in description: '{pattern}'. Descriptions should state WHEN to use, not summarize internal steps."
                )
                break

    def _validate_body_structure(self, body: str) -> None:
        """Checks for standard heading hierarchy and core sections."""
        lines = [line.strip() for line in body.splitlines()]

        # Check for H1 header
        has_h1 = any(line.startswith("# ") for line in lines)
        if not has_h1:
            self.warnings.append("Missing main title (# Header 1).")

        # Check for Overview or When to Use
        has_overview = any(re.match(r"^##\s+(?:Overview|Resumen)", line, re.I) for line in lines)
        has_when = any(re.match(r"^##\s+(?:When to Use|Cuándo Usar)", line, re.I) for line in lines)

        if not (has_overview or has_when):
            self.warnings.append("Missing standard section: '## Overview' or '## When to Use'.")

    def _validate_references(self, body: str) -> None:
        """Audits relative markdown links to ensure target files exist."""
        skill_dir = self.skill_file.parent

        # Regex for markdown links [text](path)
        link_matches = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)
        for text, target in link_matches:
            target_clean = target.split("#")[0].strip()
            if not target_clean:
                continue

            # Skip web URLs or special schemes
            if target_clean.startswith(("http://", "https://", "file://", "conversation://", "mailto:")):
                continue

            ref_path = (skill_dir / target_clean).resolve()
            if not ref_path.exists():
                self.warnings.append(f"Broken relative file reference: '[{text}]({target})' target not found.")

    def _build_report(self) -> Dict[str, Any]:
        """Constructs the structured audit result."""
        valid = len(self.errors) == 0
        return {
            "path": str(self.skill_file),
            "name": self.metadata.get("name", self.skill_file.parent.name),
            "valid": valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
            "metadata": self.metadata,
        }


def validate_skill_file(path: str | Path) -> Dict[str, Any]:
    """Convenience functional interface for validating a single skill file."""
    validator = SkillValidator(Path(path))
    return validator.validate()


def scan_and_validate(target_path: Path, strict: bool = False) -> Tuple[List[Dict[str, Any]], bool]:
    """Scans a file or directory recursively for skills and validates each."""
    reports: List[Dict[str, Any]] = []
    overall_valid = True

    target_path = target_path.resolve()
    if target_path.is_file():
        candidates = [target_path]
    else:
        # Search for SKILL.md files
        candidates = list(target_path.glob("**/SKILL.md"))
        if not candidates and (target_path / "SKILL.md").exists():
            candidates = [target_path / "SKILL.md"]

    if not candidates:
        print(f"Warning: No SKILL.md found in {target_path}")
        return [], True

    for candidate in sorted(candidates):
        validator = SkillValidator(candidate)
        report = validator.validate()
        if strict and report["warnings"]:
            report["valid"] = False
        if not report["valid"]:
            overall_valid = False
        reports.append(report)

    return reports, overall_valid


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated Validator and Quality Gates for Agent Skills (SKILL.md)"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="skills",
        help="Path to a SKILL.md file or directory containing skills (default: 'skills')",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output validation results as structured JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (fail validation if any warning exists)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed statistics and metadata",
    )

    args = parser.parse_args()
    target = Path(args.path)

    reports, overall_valid = scan_and_validate(target, strict=args.strict)

    if args.json:
        payload = {
            "overall_valid": overall_valid,
            "total_skills_audited": len(reports),
            "reports": reports,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if overall_valid else 1

    # Human-readable console output
    print("=" * 68)
    print(f"SKILL QUALITY GATES AUDITOR - Scanned: {target}")
    print("=" * 68)

    for r in reports:
        status_symbol = "[OK]  " if r["valid"] else "[FAIL]"
        print(f"\n{status_symbol} {r['name']} ({Path(r['path']).relative_to(Path.cwd()) if Path(r['path']).is_relative_to(Path.cwd()) else r['path']})")

        if args.verbose and r.get("stats"):
            stats = r["stats"]
            print(f"       Chars: {stats.get('total_chars', 0)} | Tokens est: {stats.get('estimated_tokens', 0)} | Desc chars: {stats.get('description_chars', 0)}")

        if r["errors"]:
            for err in r["errors"]:
                print(f"       [ERROR]   {err}")
        if r["warnings"]:
            for warn in r["warnings"]:
                print(f"       [WARNING] {warn}")

    print("\n" + "-" * 68)
    passed_count = sum(1 for r in reports if r["valid"])
    total_count = len(reports)
    print(f"Summary: {passed_count}/{total_count} skills passed quality gates.")
    print("=" * 68)

    return 0 if overall_valid else 1


if __name__ == "__main__":
    sys.exit(main())
