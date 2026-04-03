"""Font and color configuration for pmymd."""

import sys

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

_FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"


def _register_fonts():
    """Register Instrument Sans (body/headings) and JetBrains Mono (code)."""
    try:
        pdfmetrics.registerFont(TTFont("InstrumentSans",            f"{_FONT_DIR}/InstrumentSans-Regular.ttf"))
        pdfmetrics.registerFont(TTFont("InstrumentSans-Bold",       f"{_FONT_DIR}/InstrumentSans-Bold.ttf"))
        pdfmetrics.registerFont(TTFont("InstrumentSans-Italic",     f"{_FONT_DIR}/InstrumentSans-Italic.ttf"))
        pdfmetrics.registerFont(TTFont("InstrumentSans-BoldItalic", f"{_FONT_DIR}/InstrumentSans-BoldItalic.ttf"))
        pdfmetrics.registerFontFamily(
            "InstrumentSans",
            normal="InstrumentSans",
            bold="InstrumentSans-Bold",
            italic="InstrumentSans-Italic",
            boldItalic="InstrumentSans-BoldItalic")
        pdfmetrics.registerFont(TTFont("JetBrainsMono",      f"{_FONT_DIR}/JetBrainsMono-Regular.ttf"))
        pdfmetrics.registerFont(TTFont("JetBrainsMono-Bold", f"{_FONT_DIR}/JetBrainsMono-Bold.ttf"))
        pdfmetrics.registerFontFamily(
            "JetBrainsMono",
            normal="JetBrainsMono",
            bold="JetBrainsMono-Bold")
        return True
    except Exception as e:
        print(f"Warning: could not load custom fonts ({e}), falling back to Helvetica/Courier", file=sys.stderr)
        return False


_FONTS_LOADED = _register_fonts()

# Convenience aliases — swap fonts here without touching the rest of the code
FONT_BODY       = "InstrumentSans"            if _FONTS_LOADED else "Helvetica"
FONT_BOLD       = "InstrumentSans-Bold"       if _FONTS_LOADED else "Helvetica-Bold"
FONT_ITALIC     = "InstrumentSans-Italic"     if _FONTS_LOADED else "Helvetica-Oblique"
FONT_BOLDITALIC = "InstrumentSans-BoldItalic" if _FONTS_LOADED else "Helvetica-BoldOblique"
FONT_MEDIUM     = "InstrumentSans-Bold"       if _FONTS_LOADED else "Helvetica-Bold"
FONT_MONO       = "JetBrainsMono"             if _FONTS_LOADED else "Courier"
FONT_MONO_BOLD  = "JetBrainsMono-Bold"        if _FONTS_LOADED else "Courier-Bold"

# ── Palette ──────────────────────────────────────────────────────────────────
ACCENT       = HexColor("#C04000")
ACCENT_LIGHT = HexColor("#FDEEE5")
TEXT         = HexColor("#1A1A2E")
MUTED        = HexColor("#6B7280")
CODE_BG      = HexColor("#F3F4F6")
RULE_COLOR   = HexColor("#E5E7EB")
