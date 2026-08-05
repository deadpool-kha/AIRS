"""
utils/formatting.py
Unicode box-drawing + ANSI color helpers for AIRS CLI output.
No external dependencies.
"""

import re
import shutil

# ═══════════════════════════════════════════════════════════════════════════════
# ANSI ESCAPE CODES
# ═══════════════════════════════════════════════════════════════════════════════

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"

# ═══════════════════════════════════════════════════════════════════════════════
# CORE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def c(text: str, *codes: str) -> str:
    """Wrap text in ANSI color codes."""
    return "".join(codes) + str(text) + RESET


def _visible_len(text: str) -> int:
    """Visible character count (strips ANSI codes)."""
    return len(re.sub(r"\033\[[0-9;]*m", "", text))


def _pad(text: str, width: int) -> str:
    """Pad to width using visible length."""
    return text + " " * max(0, width - _visible_len(text))


def _term_width() -> int:
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 60


# ═══════════════════════════════════════════════════════════════════════════════
# BOXES & PANELS
# ═══════════════════════════════════════════════════════════════════════════════

def header(title: str = "AIRS", version: str = "v0.3.7", subtitle: str = "") -> str:
    """Top banner."""
    w = 46
    lines = [
        f"╔{'═' * w}╗",
        f"║  {c(title, BOLD, CYAN)}  {c(version, DIM)}".ljust(w + 13) + "║",
    ]
    if subtitle:
        lines.append(f"║  {subtitle}".ljust(w + 2) + "║")
    lines.append(f"╚{'═' * w}╝")
    return "\n".join(lines)


def box(title: str, lines: list, width: int = 46) -> str:
    """Draw a bordered panel."""
    title_plain = f"─ {title} "
    top = f"┌{title_plain}{'─' * max(0, width - len(title_plain) - 1)}┐"
    body = [f"│ {_pad(line, width - 2)}│" for line in lines]
    bottom = f"└{'─' * width}┘"
    return "\n".join([top] + body + [bottom])


def mini_box(lines: list, width: int = 46) -> str:
    """Simple box without title."""
    body = [f"│ {_pad(line, width - 2)}│" for line in lines]
    return "\n".join([f"┌{'─' * width}┐"] + body + [f"└{'─' * width}┘"])


# ═══════════════════════════════════════════════════════════════════════════════
# PROGRESS & STATUS
# ═══════════════════════════════════════════════════════════════════════════════

def progress_bar(pct: float, width: int = 20) -> str:
    """Unicode progress bar. pct is 0.0–1.0."""
    filled = int(round(width * pct))
    empty = width - filled
    bar = c("█" * filled, GREEN) + c("░" * empty, DIM)
    return bar


def status(icon: str, label: str, detail: str = "") -> str:
    """Compact phase status line."""
    if detail:
        return f"{icon} {c(label, BOLD)}  {c(detail, DIM)}"
    return f"{icon} {c(label, BOLD)}"


def badge(text: str, color: str = BLUE) -> str:
    """Small colored badge."""
    return c(f" {text} ", BOLD, color)


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD PANEL
# ═══════════════════════════════════════════════════════════════════════════════

def dashboard_panel(dq_pct: float, cov_pct: float, agreement: str, stability: str) -> str:
    """Render the 4-dimension Audit Dashboard."""
    # Color-code agreement
    agr_color = GREEN if agreement.lower() == "high" else YELLOW if agreement.lower() == "moderate" else RED
    stab_color = GREEN if stability.lower() == "stable" else YELLOW if stability.lower() == "mixed" else DIM

    lines = [
        f"{c('Data Quality', BOLD)}  {progress_bar(dq_pct)}  {c(f'{dq_pct:.0%}', GREEN if dq_pct > 0.7 else YELLOW)}",
        f"{c('Coverage', BOLD)}      {progress_bar(cov_pct)}  {c(f'{cov_pct:.0%}', GREEN if cov_pct > 0.7 else YELLOW)}",
        f"{c('Agreement', BOLD)}     {c(agreement.upper(), BOLD, agr_color)}  {c('(dimensions align)', DIM)}",
        f"{c('Stability', BOLD)}     {c(stability.upper(), BOLD, stab_color)}  {c('(iteration-over-iteration)', DIM)}",
    ]
    return box("Audit Dashboard", lines)


# ═══════════════════════════════════════════════════════════════════════════════
# BIAS & UNCERTAINTY
# ═══════════════════════════════════════════════════════════════════════════════

def bias_panel(net: str, bull: float, bear: float, score: float) -> str:
    """Directional bias block."""
    net_color = GREEN if net.lower() == "bullish" else RED if net.lower() == "bearish" else YELLOW
    return "\n".join([
        f"{c('Directional Bias:', BOLD)} {c(net.upper(), BOLD, net_color)}",
        f"  {c('Bullish:', BOLD)}  {bull:.2f}  {c('│', DIM)}  {c('Bearish:', BOLD)}  {bear:.2f}  {c('│', DIM)}  {c('Net:', BOLD)}  {score:+.2f}",
    ])


def uncertainty_panel(level: str, score: float, scarcity: float, conflict: float, coverage: float) -> str:
    """Uncertainty block."""
    lvl_color = GREEN if level.lower() == "low" else YELLOW if level.lower() == "moderate" else RED if level.lower() == "elevated" else MAGENTA
    return "\n".join([
        f"{c('Uncertainty:', BOLD)} {c(level, BOLD, lvl_color)} ({c(f'{score:.0%}', lvl_color)})",
        f"  {c('Scarcity', DIM)} {scarcity:.0%}  ·  {c('Conflict', DIM)} {conflict:.0%}  ·  {c('Coverage', DIM)} {coverage:.0%}",
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# QUESTIONS & CONTRADICTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def question_line(idx: int, q_text: str, why: str = "", resolvable: bool = False) -> str:
    """Single active question."""
    icon = c("→", CYAN) if resolvable else c("?", YELLOW)
    lines = [f"  {icon} {c(q_text, BOLD)}"]
    if why:
        lines.append(f"     {c(why, DIM)}")
    return "\n".join(lines)


def contradiction_line(name: str, description: str, severity: str = "medium") -> str:
    """Single contradiction."""
    sev_color = RED if severity.lower() == "high" else YELLOW
    return f"  {c('⚠', sev_color)}  [{c(severity.upper(), BOLD, sev_color)}] {c(name, BOLD)}\n     {c(description, DIM)}"


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE STATUS (for loop.py)
# ═══════════════════════════════════════════════════════════════════════════════

def phase_header(phase_num: int, title: str) -> str:
    return f"\n{c(f'PHASE {phase_num}:', BOLD, BLUE)} {c(title, BOLD)}"


def iteration_header(n: int, max_n: int) -> str:
    return f"\n{c(f'ITERATION {n}/{max_n}', BOLD, CYAN)}"


def halt_banner(reason: str, narrative: str = "", circuit: bool = False) -> str:
    """Halt announcement."""
    color = YELLOW if circuit else GREEN
    icon = "⛔" if circuit else "✓"
    lines = [
        "",
        f"{c(icon, color)}  {c('HALT', BOLD, color)}  —  {c(reason, BOLD)}",
    ]
    if narrative:
        lines.append(f"   {c(narrative, DIM)}")
    return "\n".join(lines)


def report_footer(md_path: str, pdf_path: str = None) -> str:
    """Final report location line."""
    pdf_msg = f"  {c('[PDF]', GREEN)} {pdf_path}" if pdf_path else ""
    return f"\n{c('Report:', BOLD)} {c(md_path, CYAN)}{pdf_msg}"
