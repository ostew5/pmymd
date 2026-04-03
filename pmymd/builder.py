"""PDF document building and page templates for pmymd."""

import re

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, PageBreak, KeepTogether, NextPageTemplate
)
from reportlab.platypus.flowables import Flowable

from pmymd.config import (
    FONT_BODY, FONT_BOLD, FONT_ITALIC, FONT_BOLDITALIC,
    FONT_MONO, FONT_MONO_BOLD, ACCENT, ACCENT_LIGHT, TEXT, MUTED,
    RULE_COLOR, CODE_BG
)
from pmymd.styles import make_styles
from pmymd.parser import parse_markdown
from pmymd.syntax import SyntaxCodeBlock

PAGE_W, PAGE_H = landscape(A4)
MARGIN        = 18 * mm
HEADER_H      = 12 * mm
FOOTER_H      = 8  * mm
GUTTER        = 8  * mm


# ── Page templates ────────────────────────────────────────────────────────────
class DocWithHeader(BaseDocTemplate):
    """Custom document template with header support."""
    def __init__(self, filename, header_title_ref, **kw):
        super().__init__(filename, **kw)
        self.header_title_ref = header_title_ref  # list([str|None])

    def handle_pageBegin(self):
        super().handle_pageBegin()

    def afterPage(self):
        pass


def draw_title_page_bg(canvas, doc):
    """Title page: accent top bar + subtle bottom strip, white background."""
    canvas.saveState()
    # Top accent bar (same height as body header)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)
    # Bottom accent strip
    canvas.setFillColor(ACCENT_LIGHT)
    canvas.rect(0, 0, PAGE_W, FOOTER_H, fill=1, stroke=0)
    # Thin rule above bottom strip
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(1.5)
    canvas.line(MARGIN, FOOTER_H, PAGE_W - MARGIN, FOOTER_H)
    canvas.restoreState()


def make_body_page_fns(header_title_ref):
    """Create header/footer drawing functions for body pages."""

    def draw_header_footer(canvas, doc):
        from reportlab.lib.colors import white

        canvas.saveState()
        # Header bar
        canvas.setFillColor(ACCENT)
        canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)

        title = header_title_ref[0] or ""
        canvas.setFont(FONT_BOLD, 9)
        canvas.setFillColor(white)
        canvas.drawString(MARGIN, PAGE_H - HEADER_H + 4 * mm, title)

        # Page number (right side of header)
        page_str = f"Page {doc.page}"
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - HEADER_H + 4 * mm, page_str)

        # Footer rule
        canvas.setStrokeColor(RULE_COLOR)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, FOOTER_H, PAGE_W - MARGIN, FOOTER_H)

        # Footer text
        canvas.setFont(FONT_BODY, 7.5)
        canvas.setFillColor(MUTED)
        src = getattr(doc, '_source_name', '')
        canvas.drawString(MARGIN, 3 * mm, src)

        canvas.restoreState()

    return draw_header_footer


# ── Main builder ──────────────────────────────────────────────────────────────
def build_pdf(md_text, output_path, source_name=""):
    """Build a PDF from markdown text and save to output_path."""
    styles = make_styles()

    # Split on first '---' separator
    parts = re.split(r'^\s*---\s*$', md_text, maxsplit=1, flags=re.MULTILINE)
    title_md = parts[0].strip()
    body_md  = parts[1].strip() if len(parts) > 1 else ""

    # Parse body first to find last H1 for header tracking
    body_flowables, last_h1_in_body = parse_markdown(body_md, styles, number_headings=True)

    # Header title ref: we start with None, but we track H1s at build time
    # by scanning title md too
    title_h1_match = re.findall(r'^#\s+(.+)', title_md, re.MULTILINE)
    initial_header = title_h1_match[-1].strip() if title_h1_match else None

    # We'll keep a mutable ref updated as flowables are built
    header_title_ref = [initial_header]

    # ── Frames ──
    usable_top    = PAGE_H - MARGIN - HEADER_H
    usable_bottom = MARGIN + FOOTER_H
    usable_h      = usable_top - usable_bottom

    col_w = (PAGE_W - 2 * MARGIN - GUTTER) / 2

    # Both title and body pages use the same 2-column frame geometry
    def make_col_frames(left_id, right_id):
        lf = Frame(
            MARGIN, usable_bottom, col_w, usable_h,
            id=left_id, leftPadding=4, rightPadding=4,
            topPadding=4, bottomPadding=4)
        rf = Frame(
            MARGIN + col_w + GUTTER, usable_bottom, col_w, usable_h,
            id=right_id, leftPadding=4, rightPadding=4,
            topPadding=4, bottomPadding=4)
        return lf, rf

    draw_body = make_body_page_fns(header_title_ref)

    title_template = PageTemplate(
        id="TitlePage",
        frames=list(make_col_frames("title_left", "title_right")),
        onPage=draw_title_page_bg)

    body_template = PageTemplate(
        id="BodyPage",
        frames=list(make_col_frames("left", "right")),
        onPage=draw_body)

    doc = DocWithHeader(
        output_path,
        header_title_ref,
        pagesize=landscape(A4),
        leftMargin=0, rightMargin=0,
        topMargin=0, bottomMargin=0)
    doc._source_name = source_name
    doc.addPageTemplates([title_template, body_template])

    # ── Title page content ──
    story = []

    title_flowables, _ = parse_markdown(title_md, {
        **styles,
        "H1":   styles["TitleMain"],
        "H2":   styles["TitleSub"],
        "H3":   styles["TitleSub"],
        "Body": styles["TitleMeta"],
    })
    story.extend(title_flowables)

    # Switch to body template
    story.append(NextPageTemplate("BodyPage"))
    story.append(PageBreak())

    # ── Walk body flowables, updating header ref when we hit H1 ──
    # We need to intercept H1s at render time. Easiest: wrap in a custom flowable.

    class H1Tracker(Flowable):
        def __init__(self, title, ref):
            super().__init__()
            self.title = title
            self.ref   = ref
            self.width = 0
            self.height = 0
        def draw(self):
            self.ref[0] = self.title
        def wrap(self, aw, ah):
            return 0, 0

    # Re-parse body keeping H1 tracker injections
    enriched = []
    h1_pattern = re.compile(r'^#\s+(.*)', re.MULTILINE)
    # interleave tracker flowables with body_flowables by re-parsing
    body_lines = body_md.splitlines()
    line_flowables, _ = parse_markdown(body_md, styles, number_headings=True)

    # Simpler approach: scan body_md for H1s and insert trackers
    # Map flowable index → h1 title via second pass
    h1_titles = [m.group(1).strip() for m in h1_pattern.finditer(body_md)]
    h1_idx = 0
    for fl in line_flowables:
        # detect if this paragraph matches an H1 style
        if (hasattr(fl, 'style') and
                getattr(fl.style, 'name', '') == 'H1' and
                h1_idx < len(h1_titles)):
            enriched.append(H1Tracker(h1_titles[h1_idx], header_title_ref))
            h1_idx += 1
        enriched.append(fl)

    story.extend(enriched)

    doc.build(story)
    return output_path
