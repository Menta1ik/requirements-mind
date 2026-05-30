#!/usr/bin/env python3
import os
import sys
import argparse
import asyncio
from datetime import datetime

# Check that the required libraries are present
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: the 'playwright' library is not installed in the current Python environment.", file=sys.stderr)
    print("Please install it with: pip install playwright or uv pip install playwright", file=sys.stderr)
    sys.exit(1)

try:
    from markdownify import markdownify as md
except ImportError:
    print("Error: the 'markdownify' library is not installed in the current Python environment.", file=sys.stderr)
    print("Please install it with: pip install markdownify or uv pip install markdownify", file=sys.stderr)
    sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="Headless import of web pages from a running Chrome (CDP) into Requirements Mind.")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--port", type=int, default=9222, help="Chrome debugging port (default 9222)")
    parser.add_argument("--query", required=True, help="Search query to find the tab (by URL or title)")
    parser.add_argument("--filename", default="confluence_specs.md", help="Output file name (default confluence_specs.md)")

    args = parser.parse_args()

    project_dir = os.path.join("projects", args.project)
    if not os.path.exists(project_dir):
        print(f"Error: project directory {project_dir} not found. Initialize the project first.", file=sys.stderr)
        sys.exit(1)

    output_path = os.path.join(project_dir, "input", args.filename)

    print(f"Connecting to Google Chrome on port {args.port}...")

    try:
        async with async_playwright() as p:
            # Connect to the running Chrome over the CDP protocol
            try:
                browser = await p.chromium.connect_over_cdp(f"http://localhost:{args.port}")
            except Exception as e:
                print(f"Could not connect to Chrome on port {args.port}.", file=sys.stderr)
                print("Make sure Chrome is started with the flag --remote-debugging-port=9222", file=sys.stderr)
                print(f"Error details: {e}", file=sys.stderr)
                sys.exit(1)

            # Get all the open contexts and pages
            if not browser.contexts:
                print("Error: the browser has no active contexts.", file=sys.stderr)
                sys.exit(1)

            context = browser.contexts[0]
            pages = context.pages

            if not pages:
                print("Error: the browser has no open tabs.", file=sys.stderr)
                sys.exit(1)

            print(f"Scanning {len(pages)} open tabs...")
            target_page = None

            for page in pages:
                url = page.url
                title = await page.title()

                # Look for a match by tab URL or title
                if args.query.lower() in url.lower() or args.query.lower() in title.lower():
                    target_page = page
                    print(f"Found a matching tab: '{title}' ({url})")
                    break

            if not target_page:
                print(f"Error: no tab containing '{args.query}' was found.", file=sys.stderr)
                print("The open tabs in your browser:", file=sys.stderr)
                for page in pages:
                    print(f" - '{await page.title()}' ({page.url})", file=sys.stderr)
                sys.exit(1)

            print(f"Extracting the page content...")
            # Get the page's HTML
            html_content = await target_page.content()
            title = await target_page.title()

            # Convert the HTML to Markdown
            print("Converting the content to Markdown...")
            # Strip navigation, headers, footers, and scripts to keep only the text
            markdown_content = md(
                html_content,
                strip=['script', 'style', 'nav', 'header', 'footer', 'noscript'],
                heading_style="ATX"
            )

            # Add a header with the source
            final_markdown = (
                f"# {title}\n\n"
                f"> **Source:** [{target_page.url}]({target_page.url})\n"
                f"> **Import date:** {datetime.now().isoformat()}\n\n"
                f"---\n\n"
                f"{markdown_content}"
            )

            # Save into input/
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_markdown)

            print(f"Successfully imported {len(final_markdown)} characters into the file: {output_path}")

    except Exception as e:
        print(f"Unexpected error during the import process: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
