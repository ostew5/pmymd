# pmymd — Print MY MarkDown

Converts Markdown to a landscape, two-column PDF with a title page and running headers.

## Features

- **Title page** — Everything before the first `---` separator is rendered as a styled title page.
- **Two-column layout** — Content after `---` flows in a two-column layout on landscape A4 pages.
- **Running headers** — The last H1 before any section is automatically displayed in the page header.
- **Syntax-highlighted code blocks** — Code fences are rendered with Pygments syntax highlighting.
- **Numbered headings** — H1/H2/H3 headings are automatically numbered (e.g. 1, 1.1, 1.1.1).
- **Rich inline formatting** — Bold, italic, inline code, and links are all supported.

## Installation

```bash
pip install .
```

Or install in editable mode for development:

```bash
pip install -e .
```

### Dependencies

- **reportlab** — PDF generation
- **pygments** — Syntax highlighting for code blocks

## Usage

```bash
# Basic usage — produces input.pdf from input.md
pmymd input.md

# Specify output path
pmymd input.md -o output.pdf
```

## Input Format

Your Markdown file should be structured as follows:

```markdown
# My Document Title
## Subtitle
Author Name
Date

---

# Section One

Content goes here...

## Subsection

More content, including code:

```python
def hello():
    print("Hello, world!")
```

# Section Two

Continued content...
```

- Everything **before** `---` becomes the title page.
- Everything **after** `---` is laid out in two columns with numbered headings and running headers.

## Project Structure

```
pmymd/
├── builder.py    # PDF document building and page templates
├── cli.py        # Command-line interface
├── config.py     # Color, font, and style constants
├── parser.py     # Markdown-to-flowables parsing logic
├── styles.py     # ReportLab stylesheet generation
└── syntax.py     # Pygments syntax-highlighted code blocks
```

## License

MIT
