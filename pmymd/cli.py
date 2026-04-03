"""CLI entry point for pmymd."""

import sys
import os
import argparse

from pmymd.builder import build_pdf


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown to a landscape 2-column PDF with title page.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("input", help="Path to input .md file")
    parser.add_argument("-o", "--output", default=None,
                        help="Output PDF path (default: same name as input)")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = args.output
    else:
        base = os.path.splitext(input_path)[0]
        output_path = base + ".pdf"

    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    source_name = os.path.basename(input_path)

    print(f"Converting {input_path} → {output_path} …")
    build_pdf(md_text, output_path, source_name=source_name)
    print(f"Done! PDF saved to: {output_path}")


if __name__ == "__main__":
    main()
