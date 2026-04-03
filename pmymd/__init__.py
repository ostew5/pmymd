"""
pmymd - Print MY MarkDown converts Markdown to a PDF in my preferred format.

Features:
  - Everything before the first '---' becomes a title page
  - Content after '---' is laid out in 2 columns
  - The last H1 before any section is shown in the header
  - Landscape orientation

Usage:
  pmymd input.md                  # outputs input.pdf
  pmymd input.md -o output.pdf    # custom output path
  pmymd input.md --title-font-size 48
"""

__version__ = "0.1.0"
