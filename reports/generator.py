"""
reports/generator.py
Issue #10 — Report Generator

Generates professional investment research memos in Markdown.
Optional PDF export via --pdf flag.

Design:
- Jinja2 templating for clean separation of logic and presentation
- Deterministic data formatting (no LLM for numbers/tables)
- Optional LLM-enhanced executive summary prose
- Graceful degradation when data is missing
- PDF generation attempts weasyprint; falls back gracefully if unavailable
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Path to the templates directory
TEMPLATE_DIR = Path(__file__).parent / "templates"
DEFAULT_TEMPLATE = "report.md.j2"


class ReportGenerator:
    """
    Professional investment memo generator for AIRS.

    Usage:
        generator = ReportGenerator()
        markdown = generator.generate(results)
        generator.save(markdown, "reports/AAPL_2026-08-04.md")
    """

    def __init__(self, template_name: str = DEFAULT_TEMPLATE, use_llm_summary: bool = False):
        self.template_name = template_name
        self.use_llm_summary = use_llm_summary
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Custom filter: {{ value | percent }} turns 0.29 into "29%"
        self.env.filters["percent"] = lambda x: f"{x * 100:.0f}%" if x is not None else "N/A"
        
    def generate(self, results: Dict[str, Any]) -> str:
        """
        Render a full investment memo from loop results.

        Args:
            results: The dict returned by EvidenceDrivenLoop._final_output()

        Returns:
            Markdown string
        """
        template = self.env.get_template(self.template_name)
        context = self._build_context(results)
        return template.render(**context)

    def _build_context(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize data from loop results for the template."""
        hyp = results.get("hypotheses") or {}
        dash = results.get("dashboard") or {}
        risk = results.get("risk") or {}

        return {
            "entity": results.get("entity", "Unknown"),
            "ticker": results.get("ticker", ""),
            "asset_type": results.get("asset_type", "unknown"),
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "iterations": results.get("iterations", 0),
            "halt_reason": self._format_halt_reason(results.get("halt_reason", "unknown")),
            "evidence_count": results.get("evidence_count", 0),
            "dashboard": dash,
            "directional_bias": hyp.get("directional_bias"),
            "uncertainty": hyp.get("uncertainty"),
            "bull": hyp.get("bull"),
            "bear": hyp.get("bear"),
            "base": hyp.get("base"),
            "risk": risk,
            "active_questions": results.get("active_questions", []),
            "unresolved_contradictions": results.get("unresolved_contradictions", []),
            "evidence_by_source": results.get("evidence_by_source", {}),
            "evidence_by_tier": results.get("evidence_by_tier", {}),
            "evidence_snapshot": results.get("evidence_snapshot", {}),
            "executive_summary": None,
        }

    def _format_halt_reason(self, reason: str) -> str:
        """Make halt reasons human-readable."""
        mapping = {
            "coherent_view": "A coherent directional view was formed with available evidence",
            "stable_thesis": "Thesis stabilized across iterations; deeper data did not change the story",
            "resolved": "Ambiguity resolved with deeper data",
            "unresolvable_tension": "Contradictions remain but cannot be resolved with available data",
            "max_iterations": "Circuit breaker: maximum iterations reached",
            "critic_error": "Halted due to critic evaluation error",
            "insufficient_clarity": "Could not form a coherent view; insufficient evidence",
            "seeking_clarity": "View forming but not yet sharp; requested deeper tier",
            "fallback": "Halted for safety due to unexpected state",
        }
        return mapping.get(reason, reason.replace("_", " ").title())
    def save(self, markdown: str, output_path: str) -> Path:
        """Save markdown to disk. Creates parent directories if needed."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        logger.info(f"Report saved to {path}")
        return path

    def to_pdf(self, markdown: str, output_path: str) -> Optional[Path]:
        """
        Convert markdown to PDF.

        Tries weasyprint first. If unavailable, logs a warning and returns None.
        Does NOT raise an exception.
        """
        try:
            import weasyprint
            from markdown import markdown

            html = markdown(markdown, extensions=["tables", "fenced_code"])
            styled_html = f"""
            <html>
            <head>
            <style>
                body {{ font-family: Georgia, serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
                h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
                h2 {{ border-bottom: 1px solid #ccc; padding-bottom: 6px; margin-top: 30px; }}
                h3 {{ color: #555; }}
                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background: #f5f5f5; font-weight: bold; }}
                code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
            </style>
            </head>
            <body>{html}</body>
            </html>
            """
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            weasyprint.HTML(string=styled_html).write_pdf(str(path))
            logger.info(f"PDF report saved to {path}")
            return path

        except ImportError:
            logger.warning(
                "PDF generation skipped: weasyprint not installed. "
                "Install with: pip install weasyprint markdown"
            )
            return None
        except Exception as e:
            logger.warning(f"PDF generation failed: {e}")
            return None
        
def generate_report(results: Dict[str, Any], output_dir: str = "reports/output", pdf: bool = False) -> Dict[str, Any]:
    """
    Convenience function: generate and save a report from loop results.

    Args:
        results: Loop output dict
        output_dir: Directory to save reports
        pdf: Whether to also generate PDF

    Returns:
        Dict with paths and the markdown content:
        {
            "markdown_path": Path,
            "pdf_path": Path or None,
            "markdown": str,
        }
    """
    entity = results.get("entity", "unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    generator = ReportGenerator()
    markdown = generator.generate(results)

    md_filename = f"{entity}_{timestamp}.md"
    md_path = generator.save(markdown, os.path.join(output_dir, md_filename))

    pdf_path = None
    if pdf:
        pdf_filename = f"{entity}_{timestamp}.pdf"
        pdf_path = generator.to_pdf(markdown, os.path.join(output_dir, pdf_filename))

    return {
        "markdown_path": md_path,
        "pdf_path": pdf_path,
        "markdown": markdown,
    }