"""Markdown parsing logic for pmymd."""

import re

from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.platypus.flowables import HRFlowable

from pmymd.config import FONT_MONO, ACCENT, ACCENT_LIGHT, RULE_COLOR
from pmymd.syntax import SyntaxCodeBlock


def parse_markdown(md_text, styles, number_headings=False):
    """
    Convert markdown text to a list of ReportLab flowables.
    Also returns the last H1 text found (for header use).
    If number_headings=True, H1/H2/H3 are prefixed 1 / 1.1 / 1.1.1.
    """
    flowables = []
    last_h1 = [None]  # mutable so nested fn can write
    # counters for H1, H2, H3
    counters = [0, 0, 0]

    def heading_number(level):
        """Increment counter at `level` (1-indexed), reset deeper ones, return label."""
        idx = level - 1
        counters[idx] += 1
        for j in range(idx + 1, 3):
            counters[j] = 0
        parts = [str(counters[k]) for k in range(idx + 1)]
        return ".".join(parts)

    def escape_xml(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def inline(text):
        """Convert inline markdown (bold, italic, code, links) to ReportLab XML."""
        # inline code
        text = re.sub(r'`([^`]+)`',
                      lambda m: f'<font name="{FONT_MONO}" size="9" color="#1F2937">'
                                f'{escape_xml(m.group(1))}</font>', text)
        # bold+italic
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
        # bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        # links  [text](url)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)',
                      lambda m: f'<u><font color="{ACCENT.hexval()}">'
                                f'{m.group(1)}</font></u>', text)
        return text

    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip()  # e.g. "python", "yaml", ""
            raw_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                raw_lines.append(lines[i])
                i += 1
            code_text = "\n".join(raw_lines) if raw_lines else ""
            flowables.append(SyntaxCodeBlock(code_text, language=lang))
            i += 1
            continue

        # ATX headings
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            raw_text = m.group(2).strip()
            if number_headings and level <= 3:
                num = heading_number(level)
                display = f"{num}  {raw_text}"
            else:
                display = raw_text
            text = inline(escape_xml(display))
            if level == 1:
                last_h1[0] = raw_text
                flowables.append(Paragraph(text, styles["H1"]))
                flowables.append(HRFlowable(
                    width="100%", thickness=1.2,
                    color=ACCENT_LIGHT, spaceAfter=4))
            elif level == 2:
                flowables.append(Paragraph(text, styles["H2"]))
            else:
                flowables.append(Paragraph(text, styles["H3"]))
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}\s*$', line):
            flowables.append(HRFlowable(
                width="100%", thickness=0.7, color=RULE_COLOR,
                spaceBefore=4, spaceAfter=4))
            i += 1
            continue

        # Blockquote
        if line.startswith(">"):
            text = inline(escape_xml(line.lstrip("> ").strip()))
            flowables.append(Paragraph(f'<i>{text}</i>', styles["BlockQuote"]))
            i += 1
            continue

        # Unordered list
        m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m:
            indent = len(m.group(1)) // 2
            text = inline(escape_xml(m.group(2)))
            bullet = "•" if indent == 0 else "◦"
            para = Paragraph(f'{bullet}  {text}', styles["BulletItem"])
            para.style = ParagraphStyle(
                "BulletIndented",
                parent=styles["BulletItem"],
                leftIndent=14 + indent * 14)
            flowables.append(para)
            i += 1
            continue

        # Ordered list
        m = re.match(r'^(\s*)\d+[.)]\s+(.*)', line)
        if m:
            text = inline(escape_xml(m.group(2)))
            flowables.append(Paragraph(f'&#8226;  {text}', styles["BulletItem"]))
            i += 1
            continue

        # Blank line
        if not line.strip():
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Normal paragraph (collect wrapped lines)
        para_lines = [line]
        i += 1
        while (i < len(lines)
               and lines[i].strip()
               and not re.match(r'^#{1,6}\s', lines[i])
               and not lines[i].strip().startswith("```")
               and not lines[i].startswith(">")
               and not re.match(r'^[-*+]\s', lines[i])
               and not re.match(r'^\d+[.)]\s', lines[i])
               and not re.match(r'^[-*_]{3,}\s*$', lines[i])):
            para_lines.append(lines[i])
            i += 1
        text = inline(escape_xml(" ".join(para_lines)))
        flowables.append(Paragraph(text, styles["Body"]))

    return flowables, last_h1[0]
