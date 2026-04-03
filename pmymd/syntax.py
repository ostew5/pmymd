"""Syntax highlighting support for code blocks in pmymd."""

from pygments import lex
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.token import Token

from reportlab.lib.colors import HexColor
from reportlab.platypus.flowables import Flowable

from pmymd.config import (
    FONT_MONO, FONT_BODY, ACCENT, MUTED, CODE_BG, RULE_COLOR
)

# ── Syntax token → colour map ────────────────────────────────────────────────
# Dark-ish theme on light CODE_BG (#F3F4F6)
_TOKEN_COLORS = {
    Token.Keyword:            "#C04000",  # accent
    Token.Keyword.Constant:   "#C04000",
    Token.Keyword.Declaration:"#C04000",
    Token.Keyword.Type:       "#9B2D00",
    Token.Name.Builtin:       "#7C3AED",
    Token.Name.Function:      "#1D4ED8",
    Token.Name.Class:         "#1D4ED8",
    Token.Name.Decorator:     "#6D28D9",
    Token.Literal.String:     "#15803D",
    Token.Literal.String.Doc: "#15803D",
    Token.Literal.Number:     "#B45309",
    Token.Comment:            "#9CA3AF",
    Token.Comment.Single:     "#9CA3AF",
    Token.Comment.Multiline:  "#9CA3AF",
    Token.Operator:           "#374151",
    Token.Punctuation:        "#374151",
    Token.Name.Namespace:     "#0F766E",
    Token.Name.Tag:           "#C04000",
    Token.Name.Attribute:     "#1D4ED8",
}


def _token_color(ttype):
    """Walk up the token hierarchy to find the best colour."""
    while ttype is not None:
        if ttype in _TOKEN_COLORS:
            return _TOKEN_COLORS[ttype]
        ttype = ttype.parent if hasattr(ttype, 'parent') else None
    return "#1F2937"  # default dark text


class SyntaxCodeBlock(Flowable):
    """
    A flowable that renders a syntax-highlighted code block with:
    - tight line spacing (no gaps)
    - rounded-corner background box
    - language label in bottom-right
    """
    PAD   = 7   # px padding inside box
    LANG_FONT_SIZE = 7
    CODE_FONT_SIZE = 8.5
    LINE_H = CODE_FONT_SIZE * 1.35

    def __init__(self, code, language=""):
        super().__init__()
        self.code     = code
        self.language = language.strip().lower()
        self._lines   = code.split("\n")
        self._tokens  = None  # lazily computed

    def _get_tokens(self):
        if self._tokens is not None:
            return self._tokens
        try:
            lexer = get_lexer_by_name(self.language) if self.language else TextLexer()
        except Exception:
            lexer = TextLexer()
        # tokenise line by line so we can address per-line
        self._tokens = []
        for line in self._lines:
            toks = list(lex(line, lexer))
            self._tokens.append(toks)
        return self._tokens

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        n_lines = len(self._lines)
        self._height = (n_lines * self.LINE_H
                        + 2 * self.PAD
                        + (self.LANG_FONT_SIZE + 4 if self.language else 0))
        return availWidth, self._height

    def draw(self):
        c = self.canv
        w = self.availWidth
        h = self._height

        # Background box
        c.saveState()
        c.setFillColor(CODE_BG)
        c.setStrokeColor(RULE_COLOR)
        c.setLineWidth(0.6)
        c.roundRect(0, 0, w, h, 4, fill=1, stroke=1)

        # Left accent bar
        c.setFillColor(ACCENT)
        c.roundRect(0, 0, 3, h, 2, fill=1, stroke=0)

        # Draw each line of tokens
        all_tokens = self._get_tokens()
        for line_idx, line_toks in enumerate(all_tokens):
            y = (h - self.PAD - self.CODE_FONT_SIZE
                 - line_idx * self.LINE_H)
            x = self.PAD + 6  # offset past accent bar

            c.setFont(FONT_MONO, self.CODE_FONT_SIZE)
            for ttype, value in line_toks:
                if not value:
                    continue
                col = _token_color(ttype)
                c.setFillColor(HexColor(col))
                # measure and draw each token value
                for char_chunk in value.split("\n"):
                    if char_chunk:
                        c.drawString(x, y, char_chunk)
                        x += c.stringWidth(char_chunk, FONT_MONO, self.CODE_FONT_SIZE)

        # Language label bottom-right
        if self.language:
            c.setFont(FONT_BODY, self.LANG_FONT_SIZE)
            c.setFillColor(MUTED)
            label = self.language
            lw = c.stringWidth(label, FONT_BODY, self.LANG_FONT_SIZE)
            c.drawString(w - lw - self.PAD, self.PAD - 1, label)

        c.restoreState()
