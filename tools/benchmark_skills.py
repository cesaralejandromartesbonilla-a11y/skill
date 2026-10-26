#!/usr/bin/env python3
"""benchmark_skills.py - Skill Performance, Footprint, and SDO Benchmarking Suite

Analyzes agent skills to calculate:
1. Context footprint (lines, character count, estimated tokens).
2. SDO (Skill Discovery Optimization) score (clarity of triggers, absence of spoilers).
3. Structural quality score (adherence to templates and standard sections).
4. Asset bundling (scripts, references, templates).
5. Ponytail efficiency verdict (YAGNI/anti-bloat analysis).
"""

import argparse
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from tools.validate_skill import SkillValidator, WORKFLOW_SPOILER_PATTERNS, NAME_REGEX
except ImportError:
    from validate_skill import SkillValidator, WORKFLOW_SPOILER_PATTERNS, NAME_REGEX


class SkillBenchmarkAnalyzer:
    """Evaluates skills and aggregates benchmark analytics across directories."""

    def __init__(self, target_path: str | Path):
        self.target_path = Path(target_path).resolve()
        self.results: List[Dict[str, Any]] = []

    def analyze_all(self, rank_by: str = "tokens") -> List[Dict[str, Any]]:
        """Finds all skills under target_path, evaluates each, and ranks them."""
        self.results.clear()

        if self.target_path.is_file():
            candidates = [self.target_path]
        else:
            candidates = list(self.target_path.glob("**/SKILL.md"))
            if not candidates and (self.target_path / "SKILL.md").exists():
                candidates = [self.target_path / "SKILL.md"]

        for candidate in sorted(candidates):
            entry = self._analyze_single_skill(candidate)
            self.results.append(entry)

        # Sort results
        if rank_by == "tokens":
            self.results.sort(key=lambda x: x["tokens_est"], reverse=True)
        elif rank_by == "sdo":
            self.results.sort(key=lambda x: x["sdo_score"], reverse=True)
        elif rank_by == "name":
            self.results.sort(key=lambda x: x["name"])

        return self.results

    def _analyze_single_skill(self, skill_file: Path) -> Dict[str, Any]:
        """Analyzes a single SKILL.md file and its surrounding assets."""
        validator = SkillValidator(skill_file)
        validation_report = validator.validate()

        content = ""
        try:
            content = skill_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass

        skill_dir = skill_file.parent
        total_chars = len(content)
        lines = len(content.splitlines())
        tokens_est = round(total_chars / 4)

        # Analyze SDO (Skill Discovery Optimization) score [0 - 100]
        sdo_score = 100
        desc = validation_report["metadata"].get("description", "")
        if not desc:
            sdo_score -= 50
        else:
            if not desc.strip().lower().startswith("use when"):
                sdo_score -= 25
            if len(desc.strip()) > 500:
                sdo_score -= 15
            for pattern in WORKFLOW_SPOILER_PATTERNS:
                if re.search(pattern, desc, re.I):
                    sdo_score -= 30
                    break

        name = validation_report["metadata"].get("name", "")
        if not name or not NAME_REGEX.match(name):
            sdo_score -= 20

        sdo_score = max(0, sdo_score)

        # Analyze Structural Quality score [0 - 100]
        struct_score = 0
        body = validator.body
        if any(line.startswith("# ") for line in body.splitlines()):
            struct_score += 25
        if re.search(r"^##\s+(?:Overview|Resumen)", body, re.M | re.I):
            struct_score += 25
        if re.search(r"^##\s+(?:When to Use|Cuándo Usar)", body, re.M | re.I):
            struct_score += 25
        if "```" in body or "|" in body:
            struct_score += 25

        # Check auxiliary assets
        scripts_count = len(list((skill_dir / "scripts").glob("*"))) if (skill_dir / "scripts").is_dir() else 0
        references_count = len(list((skill_dir / "references").glob("*"))) if (skill_dir / "references").is_dir() else 0
        examples_count = len(list((skill_dir / "examples").glob("*"))) if (skill_dir / "examples").is_dir() else 0
        total_aux_files = scripts_count + references_count + examples_count

        # Ponytail Verdict
        if tokens_est > 3500 and references_count == 0:
            verdict = "Heavy (Recommend externalizing references)"
        elif tokens_est <= 1600 and sdo_score >= 80 and struct_score >= 75:
            verdict = "Lean & Optimal"
        elif sdo_score < 60:
            verdict = "Low Discovery Clarity (Fix description)"
        else:
            verdict = "Balanced"

        rel_path = skill_file.relative_to(Path.cwd()) if skill_file.is_relative_to(Path.cwd()) else skill_file

        return {
            "name": validation_report["name"],
            "path": str(rel_path),
            "tokens_est": tokens_est,
            "total_chars": total_chars,
            "lines": lines,
            "sdo_score": sdo_score,
            "struct_score": struct_score,
            "aux_files": total_aux_files,
            "scripts_count": scripts_count,
            "references_count": references_count,
            "verdict": verdict,
            "valid": validation_report["valid"],
            "warnings_count": len(validation_report["warnings"]),
        }

    def generate_markdown_report(self) -> str:
        """Constructs an exhaustive Markdown benchmark report."""
        if not self.results:
            self.analyze_all()

        total_skills = len(self.results)
        total_tokens = sum(r["tokens_est"] for r in self.results)
        avg_tokens = round(total_tokens / total_skills) if total_skills else 0
        avg_sdo = round(sum(r["sdo_score"] for r in self.results) / total_skills, 1) if total_skills else 0
        avg_struct = round(sum(r["struct_score"] for r in self.results) / total_skills, 1) if total_skills else 0
        lean_count = sum(1 for r in self.results if "Optimal" in r["verdict"])

        md = []
        md.append("# Benchmark de Desempeño y Huella de Skills")
        md.append(f"> **Directorio Auditado:** `{self.target_path}`  ")
        md.append(f"> **Total de Skills Analizadas:** {total_skills}  ")
        md.append(f"> **Huella Total Estimada en Contexto:** ~{total_tokens:,} tokens (~{round(total_tokens*4/1024, 1)} KB)\n")

        md.append("## 1. Resumen Ejecutivo (KPIs)")
        md.append("")
        md.append("| Métrica | Valor Global | Estado / Meta |")
        md.append("| :--- | :---: | :--- |")
        md.append(f"| **Skills Evaluadas** | **{total_skills}** | Catálogo Activo |")
        md.append(f"| **Tokens Totales (Payload)** | **~{total_tokens:,}** | Consumo pasivo si cargadas simultáneamente |")
        md.append(f"| **Promedio por Skill** | **~{avg_tokens:,} tokens** | Target recomendado: < 2,000 tokens |")
        md.append(f"| **Score SDO Promedio** | **{avg_sdo} / 100** | Claridad de descubrimiento de Anthropic/Superpowers |")
        md.append(f"| **Calidad Estructural Promedio** | **{avg_struct} / 100** | Adherencia a plantilla de secciones estándar |")
        md.append(f"| **Skills Óptimas (Lean)** | **{lean_count} / {total_skills}** ({round(lean_count*100/total_skills if total_skills else 0)}%) | Principio Ponytail (YAGNI) cumplido |")
        md.append("")

        md.append("## 2. Matriz Comparativa Detallada")
        md.append("")
        md.append("| Skill | Tokens Est. | Líneas | SDO Score | Estructura | Archivos Aux. | Veredicto Ponytail |")
        md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :--- |")

        for r in self.results:
            md.append(
                f"| `{r['name']}` | **~{r['tokens_est']:,}** | {r['lines']} | {r['sdo_score']}/100 | {r['struct_score']}/100 | {r['aux_files']} | {r['verdict']} |"
            )

        md.append("")
        md.append("## 3. Recomendaciones y Oportunidades de Optimización")
        md.append("")
        md.append("1. **Skills con Alto Consumo (>3,500 tokens):** Considerar extraer especificaciones extensas o tablas de referencia pesadas hacia carpetas `references/` para permitir *progressive disclosure* y mantener el archivo principal ligero.")
        md.append("2. **Optimización de Descripciones (SDO):** Asegurar que toda skill inicie con `'Use when...'` y que no contenga spoilers de procedimiento en el frontmatter YAML, garantizando que el agente lea el cuerpo completo cuando deba invocarla.")
        md.append("3. **Determinismo por Scripts:** Las skills complejas deben delegar lógica de cálculo o conversión a ejecutables en `scripts/` (ej. `tools/blender_universal_bridge.py`, `sync_roadmaps.py`) para evitar alucinaciones en el razonamiento del LLM.")

        return "\n".join(md) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Skill Performance, Footprint, and SDO Benchmarking Suite"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="skills",
        help="Path to scan for skills (default: 'skills')",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "table"],
        default="table",
        help="Output format (default: 'table')",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Path to save report file (e.g. research/benchmarks/skills_footprint_report.md)",
    )
    parser.add_argument(
        "--rank-by",
        choices=["tokens", "sdo", "name"],
        default="tokens",
        help="Sort ranking by metric (default: 'tokens')",
    )

    args = parser.parse_args()
    analyzer = SkillBenchmarkAnalyzer(args.path)
    results = analyzer.analyze_all(rank_by=args.rank_by)

    if args.format == "json":
        output_str = json.dumps(results, indent=2, ensure_ascii=False)
    elif args.format == "markdown":
        output_str = analyzer.generate_markdown_report()
    else:
        # Table console display
        lines = []
        lines.append("=" * 80)
        lines.append(f"SKILL PERFORMANCE & FOOTPRINT BENCHMARK ({args.path})")
        lines.append("=" * 80)
        lines.append(f"{'Skill Name':<28} {'Tokens Est':<12} {'Lines':<8} {'SDO':<8} {'Struct':<8} {'Verdict'}")
        lines.append("-" * 80)
        for r in results:
            lines.append(
                f"{r['name']:<28} ~{r['tokens_est']:<11} {r['lines']:<8} {r['sdo_score']:<8} {r['struct_score']:<8} {r['verdict']}"
            )
        lines.append("=" * 80)
        lines.append(f"Total skills: {len(results)} | Total tokens: ~{sum(r['tokens_est'] for r in results):,}")
        output_str = "\n".join(lines)

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # If saving to .md always write markdown
        if out_path.suffix.lower() == ".md" and args.format != "markdown":
            output_str = analyzer.generate_markdown_report()
        elif out_path.suffix.lower() == ".json" and args.format != "json":
            output_str = json.dumps(results, indent=2, ensure_ascii=False)

        out_path.write_text(output_str, encoding="utf-8")
        print(f"Benchmark report saved to: {out_path}")
    else:
        print(output_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
