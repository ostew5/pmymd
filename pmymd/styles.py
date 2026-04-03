"""Styles definitions for pmymd PDF generation."""

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor

from pmymd.config import (
    FONT_BODY, FONT_BOLD, FONT_ITALIC, FONT_BOLDITALIC,
    FONT_MONO, ACCENT, TEXT, MUTED, CODE_BG
)


def make_styles():
    """Create and return a dictionary of ParagraphStyles for document elements."""
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        # Title page — left-aligned, same colours as body
        "TitleMain": ps("TitleMain",
            fontName=FONT_BOLD, fontSize=36,
            textColor=ACCENT, alignment=TA_LEFT,
            spaceAfter=6, leading=44),
        "TitleSub": ps("TitleSub",
            fontName=FONT_BODY, fontSize=16,
            textColor=TEXT, alignment=TA_LEFT,
            spaceAfter=5, leading=22),
        "TitleMeta": ps("TitleMeta",
            fontName=FONT_BODY, fontSize=11,
            textColor=MUTED, alignment=TA_LEFT,
            leading=16),

        # Body
        "H1": ps("H1",
            fontName=FONT_BOLD, fontSize=17,
            textColor=ACCENT, spaceBefore=14, spaceAfter=4,
            leading=22, borderPadding=(0, 0, 4, 0)),
        "H2": ps("H2",
            fontName=FONT_BOLD, fontSize=13,
            textColor=TEXT, spaceBefore=10, spaceAfter=3, leading=18),
        "H3": ps("H3",
            fontName=FONT_BOLDITALIC, fontSize=11,
            textColor=MUTED, spaceBefore=8, spaceAfter=2, leading=15),
        "Body": ps("Body",
            fontName=FONT_BODY, fontSize=10,
            textColor=TEXT, spaceAfter=6, leading=15,
            alignment=TA_JUSTIFY),
        "BulletItem": ps("BulletItem",
            fontName=FONT_BODY, fontSize=10,
            textColor=TEXT, spaceAfter=3, leading=14,
            leftIndent=14, firstLineIndent=0),
        "Code": ps("Code",
            fontName=FONT_MONO, fontSize=9,
            textColor=HexColor("#1F2937"),
            backColor=CODE_BG, spaceAfter=6,
            leading=13, leftIndent=8, rightIndent=8,
            borderPadding=6),
        "BlockQuote": ps("BlockQuote",
            fontName=FONT_ITALIC, fontSize=10,
            textColor=MUTED, leftIndent=14,
            borderPadding=(0, 0, 0, 8),
            spaceAfter=6, leading=14),
    }
