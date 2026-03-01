"""Command-line interface for Tour Guide Copilot."""

import argparse
import sys
import webbrowser
from pathlib import Path

from .config import load_config
from .exceptions import CopilotError
from .generator import generate


def main():
    """Entry point for the CLI."""
    # Ensure UTF-8 output on Windows so emoji in print statements don't crash
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="copilot",
        description="Tour Guide Copilot — Turn a guide's knowledge into itineraries and plans.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate command
    gen_parser = subparsers.add_parser(
        "generate", help="Generate itinerary and plans from a guide document."
    )
    gen_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the guide's document (.md, .txt, or .pdf)",
    )
    gen_parser.add_argument(
        "--output", "-o",
        default="./output",
        help="Output directory (default: ./output)",
    )
    gen_parser.add_argument(
        "--format", "-f",
        choices=["html", "markdown", "json", "all"],
        default=None,
        help="Output format (overrides .env setting)",
    )
    gen_parser.add_argument(
        "--env",
        default=None,
        help="Path to .env file (default: .env in project root)",
    )

    # preview command
    prev_parser = subparsers.add_parser(
        "preview", help="Generate and open the result in a browser."
    )
    prev_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the guide's document",
    )
    prev_parser.add_argument(
        "--env",
        default=None,
        help="Path to .env file",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        config = load_config(args.env)

        if args.command == "generate":
            if args.format:
                config.output_format = args.format
            created = generate(args.input, args.output, config)
            print(f"\n🎉 Done! {len(created)} file(s) created.")

        elif args.command == "preview":
            config.output_format = "html"
            created = generate(args.input, "./output", config)
            html_files = [f for f in created if f.endswith(".html")]
            if html_files:
                path = Path(html_files[0]).resolve()
                print(f"\n🌐 Opening {path} in browser...")
                webbrowser.open(f"file://{path}")
            else:
                print("No HTML file generated.")

    except CopilotError as exc:
        print(f"\n❌ Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(130)


if __name__ == "__main__":
    main()
