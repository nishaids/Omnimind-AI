"""
OMNIMIND AI — tools/pdf_exporter.py
Dark theme PDF with clean markdown stripping, colored sections, and cover page.
"""

import os
import re
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

# ── Color Palette (Dark Theme) ───────────────────────────────────────────────
BG_COLOR       = colors.HexColor("#0a0a0a")
C_ORANGE       = colors.HexColor("#ff8c00")
C_GOLD         = colors.HexColor("#ffcc00")
C_CYAN         = colors.HexColor("#00ddff")
C_WHITE        = colors.HexColor("#e8e8e8")
C_LIGHT_GRAY   = colors.HexColor("#aaaaaa")
C_DIM          = colors.HexColor("#666666")
C_ACCENT       = colors.HexColor("#ff8c00")
C_BULLET_GREEN = colors.HexColor("#00ff88")


def clean_markdown(text: str) -> str:
    """Strip markdown symbols: ##, **, *, and convert - bullets to bullet points."""
    if not text:
        return ""
    # Remove ## headers markers
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Remove bold markers **text** → text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove italic markers *text* → text
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Convert - bullets to • bullets
    text = re.sub(r'^[\-\*\+]\s+', '• ', text, flags=re.MULTILINE)
    return text


def _dark_bg(canvas, doc):
    """Draw dark background and orange accent footer on every page."""
    canvas.saveState()
    # Full page dark background
    canvas.setFillColor(BG_COLOR)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    # Orange accent line at bottom
    canvas.setStrokeColor(C_ORANGE)
    canvas.setLineWidth(2)
    canvas.line(20 * mm, 12 * mm, A4[0] - 20 * mm, 12 * mm)
    # Footer text
    canvas.setFillColor(C_DIM)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(
        A4[0] / 2, 8 * mm,
        f"OMNIMIND AI  |  Built by Nishanth R  |  Page {doc.page}"
    )
    canvas.restoreState()


def _make_styles():
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle", fontName="Helvetica-Bold", fontSize=32,
            textColor=C_ORANGE, alignment=TA_CENTER,
            spaceBefore=0, spaceAfter=0, leading=40,
        ),
        "cover_tagline": ParagraphStyle(
            "CoverTagline", fontName="Helvetica", fontSize=11,
            textColor=C_LIGHT_GRAY, alignment=TA_CENTER,
            spaceBefore=10, spaceAfter=0, leading=16,
        ),
        "cover_company": ParagraphStyle(
            "CoverCompany", fontName="Helvetica-Bold", fontSize=24,
            textColor=C_GOLD, alignment=TA_CENTER,
            spaceBefore=20, spaceAfter=0, leading=30,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta", fontName="Helvetica", fontSize=9,
            textColor=C_DIM, alignment=TA_CENTER,
            spaceBefore=8, spaceAfter=0, leading=14,
        ),

        # Section header — orange
        "sec_head": ParagraphStyle(
            "SecHead", fontName="Helvetica-Bold", fontSize=15,
            textColor=C_ORANGE, spaceBefore=22, spaceAfter=6, leading=20,
        ),
        # Subsection — gold
        "sub_head": ParagraphStyle(
            "SubHead", fontName="Helvetica-Bold", fontSize=11,
            textColor=C_GOLD, spaceBefore=12, spaceAfter=4, leading=15,
        ),
        # Key label — cyan
        "key_label": ParagraphStyle(
            "KeyLabel", fontName="Helvetica-Bold", fontSize=9,
            textColor=C_CYAN, spaceBefore=4, spaceAfter=1, leading=13,
        ),
        # Value text
        "value": ParagraphStyle(
            "Value", fontName="Helvetica", fontSize=9,
            textColor=C_WHITE, spaceBefore=0, spaceAfter=4,
            leading=14, leftIndent=12,
        ),
        # Bullet text
        "bullet": ParagraphStyle(
            "Bullet", fontName="Helvetica", fontSize=9,
            textColor=C_WHITE, spaceBefore=2, spaceAfter=2,
            leading=14, leftIndent=18,
        ),
        # Body text
        "body": ParagraphStyle(
            "Body", fontName="Helvetica", fontSize=9,
            textColor=C_LIGHT_GRAY, spaceBefore=2, spaceAfter=5,
            leading=14, alignment=TA_JUSTIFY,
        ),
    }


def _render_section(s, title, content):
    """Build one section: heading + parsed content lines."""
    elems = []
    content = clean_markdown(str(content))

    elems.append(Spacer(1, 8))
    elems.append(Paragraph(title.upper(), s["sec_head"]))
    elems.append(HRFlowable(
        width="100%", thickness=1.5,
        color=C_ORANGE, spaceAfter=8
    ))

    lines = content.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            elems.append(Spacer(1, 3))
            continue

        # ALL CAPS short line → subsection header
        if stripped.isupper() and 4 < len(stripped) < 60:
            elems.append(Spacer(1, 5))
            elems.append(Paragraph(stripped, s["sub_head"]))
            continue

        # Numbered heading: "1. Title Text" or "1) Title Text"
        num_match = re.match(r'^(\d+)[\.)\s]+(.+)$', stripped)
        if num_match and len(num_match.group(2)) < 80:
            rest = num_match.group(2).strip()
            # Check if it's a key:value like "1. Key: Value"
            if ":" in rest:
                colon = rest.index(":")
                key = rest[:colon].strip()
                val = rest[colon + 1:].strip()
                if len(key.split()) <= 6 and val:
                    elems.append(Paragraph(
                        f"{num_match.group(1)}. {key}:", s["key_label"]
                    ))
                    elems.append(Paragraph(val, s["value"]))
                    continue
            # Just a numbered heading
            elems.append(Paragraph(
                f"{num_match.group(1)}.  {rest}", s["sub_head"]
            ))
            continue

        # Bullet point (• or -)
        if stripped.startswith("•") or (stripped[0] in ("-", "+") and len(stripped) > 1 and stripped[1] == " "):
            text = stripped.lstrip("•-+ ").strip()
            elems.append(Paragraph(f"•  {text}", s["bullet"]))
            continue

        # Key: Value pair
        if ":" in stripped:
            colon = stripped.index(":")
            key = stripped[:colon].strip()
            val = stripped[colon + 1:].strip()
            key_words = key.split()
            if 1 <= len(key_words) <= 6 and len(key) < 50 and val:
                elems.append(Paragraph(f"{key}:", s["key_label"]))
                elems.append(Paragraph(val, s["value"]))
                continue

        # Plain body text
        elems.append(Paragraph(stripped, s["body"]))

    elems.append(Spacer(1, 12))
    return elems


def export_pdf(
    company: str,
    research: str,
    stock: str,
    news: str,
    report: str,
    output_dir: str = "output",
) -> dict:
    if not REPORTLAB_OK:
        return {
            "success": False, "path": None,
            "message": "reportlab not installed. Run: pip install reportlab"
        }

    os.makedirs(output_dir, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{company.replace(' ', '_')}_OMNIMIND_{ts}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=22 * mm, rightMargin=22 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
        title=f"OMNIMIND AI - {company} Report",
        author="OMNIMIND AI",
    )

    s     = _make_styles()
    story = []
    now   = datetime.now().strftime("%d %B %Y, %I:%M %p")

    # ── COVER PAGE ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 60))
    story.append(Paragraph("OMNIMIND AI", s["cover_title"]))
    story.append(Paragraph("Autonomous Business Intelligence Report", s["cover_tagline"]))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=C_ORANGE, spaceAfter=0
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph(company.upper(), s["cover_company"]))
    story.append(Spacer(1, 14))
    story.append(Paragraph(f"Scan Date: {now}", s["cover_meta"]))
    story.append(Paragraph("Built by Nishanth R", s["cover_meta"]))
    story.append(Paragraph("Powered by 4 AI Agents", s["cover_meta"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(
        width="55%", thickness=0.6,
        color=C_DIM, spaceAfter=24
    ))
    story.append(PageBreak())

    # ── FOUR SECTIONS ─────────────────────────────────────────────────────────
    story += _render_section(s, "Executive Report",    report)
    story += _render_section(s, "Research",            research)
    story += _render_section(s, "Stock Analysis",      stock)
    story += _render_section(s, "News Intelligence",   news)

    # ── FINAL FOOTER ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 18))
    story.append(HRFlowable(width="100%", thickness=1, color=C_ORANGE))

    try:
        doc.build(story, onFirstPage=_dark_bg, onLaterPages=_dark_bg)
        return {"success": True, "path": filepath, "message": f"PDF saved: {filename}"}
    except Exception as e:
        return {"success": False, "path": None, "message": f"PDF generation failed: {str(e)}"}
