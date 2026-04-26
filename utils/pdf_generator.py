"""
TourMind AI — Itinerary PDF Generator
Converts AI-generated itinerary markdown text into a
beautifully styled, travel-themed PDF using ReportLab.
"""

import io
import re
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable


# ── Brand colours ────────────────────────────────────────────
FOREST  = HexColor("#2D5016")
LEAF    = HexColor("#4A7C59")
SAGE    = HexColor("#7AAE8E")
MIST    = HexColor("#C8DDD4")
SAND    = HexColor("#E8D5A3")
DUNE    = HexColor("#C9A96E")
EARTH   = HexColor("#8B6E47")
CREAM   = HexColor("#FAF7F0")
LIGHT   = HexColor("#F0EDE4")
DARK    = HexColor("#2C2416")
SOFT    = HexColor("#8B7355")
OCEAN   = HexColor("#2E86AB")
SUNSET  = HexColor("#E8845A")
GOLDEN  = HexColor("#F4B942")


# ── Page setup ───────────────────────────────────────────────
PAGE_W, PAGE_H = A4
L_MARGIN = R_MARGIN = 2.2 * cm
T_MARGIN = 2.5 * cm
B_MARGIN = 2.2 * cm
CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN


# ── Styles ───────────────────────────────────────────────────
def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "tm_title",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=FOREST,
            alignment=TA_CENTER,
            spaceAfter=4,
            leading=28,
        ),
        "subtitle": ParagraphStyle(
            "tm_subtitle",
            fontName="Helvetica",
            fontSize=11,
            textColor=EARTH,
            alignment=TA_CENTER,
            spaceAfter=2,
            leading=16,
        ),
        "meta": ParagraphStyle(
            "tm_meta",
            fontName="Helvetica",
            fontSize=9,
            textColor=SOFT,
            alignment=TA_CENTER,
            spaceAfter=0,
            leading=13,
        ),
        "section": ParagraphStyle(
            "tm_section",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=white,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            leading=18,
            leftIndent=10,
        ),
        "day_title": ParagraphStyle(
            "tm_day",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=FOREST,
            alignment=TA_LEFT,
            spaceBefore=14,
            spaceAfter=4,
            leading=16,
        ),
        "slot_head": ParagraphStyle(
            "tm_slot",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=LEAF,
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=2,
            leading=14,
        ),
        "body": ParagraphStyle(
            "tm_body",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK,
            alignment=TA_JUSTIFY,
            spaceBefore=2,
            spaceAfter=3,
            leading=14,
            leftIndent=8,
        ),
        "bullet": ParagraphStyle(
            "tm_bullet",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK,
            alignment=TA_LEFT,
            spaceBefore=1,
            spaceAfter=1,
            leading=14,
            leftIndent=16,
            bulletIndent=6,
        ),
        "tip": ParagraphStyle(
            "tm_tip",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=EARTH,
            alignment=TA_LEFT,
            spaceBefore=2,
            spaceAfter=2,
            leading=13,
            leftIndent=12,
        ),
        "footer": ParagraphStyle(
            "tm_footer",
            fontName="Helvetica",
            fontSize=8,
            textColor=SOFT,
            alignment=TA_CENTER,
            leading=11,
        ),
        "table_header": ParagraphStyle(
            "tm_th",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=white,
            alignment=TA_CENTER,
            leading=12,
        ),
        "table_cell": ParagraphStyle(
            "tm_tc",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK,
            alignment=TA_LEFT,
            leading=12,
        ),
    }
    return styles


# ── Header/Footer canvas ─────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # ── Top bar ──
    canvas.setFillColor(FOREST)
    canvas.rect(0, h - 1.2*cm, w, 1.2*cm, fill=1, stroke=0)
    canvas.setFillColor(GOLDEN)
    canvas.rect(0, h - 1.25*cm, w, 0.18*cm, fill=1, stroke=0)

    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(white)
    canvas.drawString(L_MARGIN, h - 0.85*cm, "🌿 TourMind AI")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(w - R_MARGIN, h - 0.85*cm, "Smart Itinerary Planner")

    # ── Bottom bar ──
    canvas.setFillColor(MIST)
    canvas.rect(0, 0, w, 1.1*cm, fill=1, stroke=0)
    canvas.setFillColor(LEAF)
    canvas.rect(0, 1.08*cm, w, 0.12*cm, fill=1, stroke=0)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK)
    from datetime import timezone as _tz, timedelta as _td
    _ist = _tz(_td(hours=5, minutes=30))
    canvas.drawString(L_MARGIN, 0.42*cm,
                      f"Generated by TourMind AI  •  {datetime.now(_ist).strftime('%d %b %Y')}")
    canvas.drawRightString(w - R_MARGIN, 0.42*cm,
                           f"Page {doc.page}")

    canvas.restoreState()


# ── Coloured section banner ───────────────────────────────────
class SectionBanner(Flowable):
    """A full-width coloured banner for section headings."""
    def __init__(self, text, bg=None, fg=white, width=None, height=0.7*cm):
        super().__init__()
        self.text   = text
        self.bg     = bg or LEAF
        self.fg     = fg
        self.width  = width or CONTENT_W
        self.height = height

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
        c.setFillColor(self.fg)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(10, self.height * 0.28, self.text)


# ── Main generator ────────────────────────────────────────────
def generate_itinerary_pdf(
    itinerary_text: str,
    destination: str,
    num_days: int,
    trip_type: str,
    preferences: list,
) -> bytes:
    """
    Convert AI itinerary text to a styled PDF.
    Returns PDF as bytes — pass directly to st.download_button.
    """
    buf    = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        topMargin=T_MARGIN + 0.6*cm,
        bottomMargin=B_MARGIN + 0.8*cm,
        title=f"TourMind — {destination} {num_days}-Day Itinerary",
        author="TourMind AI",
        subject="Travel Itinerary",
    )

    story = []

    # ── COVER HEADER ─────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))

    # Destination title
    story.append(Paragraph(
        f"✈️  {destination.title()}",
        styles["title"]
    ))
    story.append(Paragraph(
        f"{num_days}-Day {trip_type} Itinerary",
        styles["subtitle"]
    ))
    story.append(Spacer(1, 0.15*cm))

    prefs_str = "  •  ".join(preferences) if preferences else "General Sightseeing"
    story.append(Paragraph(
        f"Preferences:  {prefs_str}",
        styles["meta"]
    ))
    from datetime import timezone as _tz, timedelta as _td
    _ist = _tz(_td(hours=5, minutes=30))
    story.append(Paragraph(
        f"Generated on  {datetime.now(_ist).strftime('%d %B %Y  at  %I:%M %p')}",
        styles["meta"]
    ))

    # Decorative divider
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=DUNE, spaceAfter=0.4*cm
    ))

    # ── PARSE + RENDER ITINERARY ──────────────────────────────
    lines = itinerary_text.strip().splitlines()

    def clean(t):
        """Strip markdown bold/italic/headers."""
        t = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", t)
        t = re.sub(r"#{1,6}\s*",           "",      t)
        t = re.sub(r"^---+$",              "",      t)
        return t.strip()

    # Slot emoji map
    SLOT_EMOJIS = {
        "morning":   "🌅",
        "afternoon": "☀️",
        "evening":   "🌆",
        "night":     "🌙",
        "travel":    "🚗",
        "tip":       "💡",
        "pack":      "🎒",
        "budget":    "💰",
        "note":      "📝",
    }

    in_table    = False
    table_rows  = []
    table_cols  = 0

    def flush_table():
        nonlocal in_table, table_rows, table_cols
        if not table_rows:
            return
        # Build ReportLab table
        col_w = CONTENT_W / max(table_cols, 1)
        col_widths = [col_w] * table_cols

        rl_data = []
        for ri, row in enumerate(table_rows):
            cells = [Paragraph(c, styles["table_header"] if ri == 0 else styles["table_cell"])
                     for c in row]
            rl_data.append(cells)

        tbl = Table(rl_data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0),  LEAF),
            ("TEXTCOLOR",   (0,0), (-1,0),  white),
            ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("BACKGROUND",  (0,1), (-1,-1), CREAM),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [CREAM, LIGHT]),
            ("GRID",        (0,0), (-1,-1), 0.5, SAGE),
            ("ALIGN",       (0,0), (-1,-1), "LEFT"),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING",  (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("ROUNDEDCORNERS", [4]),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.2*cm))
        in_table   = False
        table_rows = []
        table_cols = 0

    for raw_line in lines:
        line = raw_line.strip()

        # ── Markdown table ───────────────────────────────────
        if line.startswith("|"):
            # Skip separator row
            if re.match(r"^\|[-| :]+\|$", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not in_table:
                in_table   = True
                table_cols = len(cells)
            table_rows.append(cells)
            continue
        else:
            if in_table:
                flush_table()

        if not line:
            story.append(Spacer(1, 0.15*cm))
            continue

        # ── Day heading ──────────────────────────────────────
        if re.match(r"^(Day\s+\d+|###?\s*Day\s+\d+)", line, re.I):
            text = clean(line)
            story.append(Spacer(1, 0.1*cm))
            story.append(SectionBanner(f"📅  {text}", bg=FOREST))
            story.append(Spacer(1, 0.1*cm))
            continue

        # ── Slot heading (Morning / Afternoon / Evening …) ───
        slot_match = re.match(
            r"^[*#\-]*\s*(Morning|Afternoon|Evening|Night|Travel Tips?|Tip|Pack|Budget|Note)[*#\s:]*(.*)$",
            line, re.I
        )
        if slot_match:
            slot_key  = slot_match.group(1).lower().split()[0]
            emoji     = SLOT_EMOJIS.get(slot_key, "📌")
            slot_text = clean(slot_match.group(1))
            extra     = clean(slot_match.group(2))
            full      = f"{emoji}  {slot_text}" + (f" — {extra}" if extra else "")
            story.append(Paragraph(full, styles["slot_head"]))
            continue

        # ── Section headings (## / ### not Day) ─────────────
        if re.match(r"^#{1,3}\s+", line):
            text = clean(line)
            story.append(SectionBanner(f"  {text}", bg=LEAF))
            story.append(Spacer(1, 0.1*cm))
            continue

        # ── Bullet points ────────────────────────────────────
        if re.match(r"^[-*•]\s+", line):
            text = clean(re.sub(r"^[-*•]\s+", "", line))
            story.append(Paragraph(f"•  {text}", styles["bullet"]))
            continue

        # ── Numbered list ────────────────────────────────────
        if re.match(r"^\d+\.\s+", line):
            text = clean(re.sub(r"^\d+\.\s+", "", line))
            num  = re.match(r"^(\d+)\.", line).group(1)
            story.append(Paragraph(f"{num}.  {text}", styles["bullet"]))
            continue

        # ── Tips / italic lines ──────────────────────────────
        if line.startswith("_") or line.startswith("*_"):
            story.append(Paragraph(clean(line), styles["tip"]))
            continue

        # ── Divider ──────────────────────────────────────────
        if re.match(r"^-{3,}$", line):
            story.append(HRFlowable(width="100%", thickness=0.5, color=MIST, spaceAfter=0.1*cm))
            continue

        # ── Regular body text ────────────────────────────────
        story.append(Paragraph(clean(line), styles["body"]))

    # Flush any remaining table
    if in_table:
        flush_table()

    # ── FOOTER NOTE ──────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=SAND))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "This itinerary was generated by TourMind AI and is meant as a guide. "
        "Always verify opening hours, prices, and transport options before travel. "
        "Have a wonderful trip! 🌿",
        styles["footer"]
    ))

    # ── BUILD ─────────────────────────────────────────────────
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buf.getvalue()