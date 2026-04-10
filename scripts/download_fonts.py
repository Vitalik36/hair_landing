"""One-off: rewrite fonts/google-fonts.css with local woff2 paths and download files."""
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_IN = ROOT / "fonts" / "google-fonts.css"
CSS_OUT = ROOT / "fonts" / "fonts.css"
FONT_DIR = ROOT / "fonts"

PATTERN = re.compile(r"url\((https://fonts\.gstatic\.com/[^)]+)\)")


def local_name(url: str) -> str:
    path = url.replace("https://fonts.gstatic.com/", "").replace("/", "_")
    return path


def main():
    text = CSS_IN.read_text(encoding="utf-8")
    urls = sorted(set(PATTERN.findall(text)))
    print(f"Unique font files: {len(urls)}")

    for url in urls:
        name = local_name(url)
        dest = FONT_DIR / name
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"  skip (exists): {name}")
            continue
        print(f"  fetch: {name}")
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.write_bytes(r.read())

    def repl(m):
        url = m.group(1)
        return f"url(./{local_name(url)})"

    out = PATTERN.sub(repl, text)
    CSS_OUT.write_text(out, encoding="utf-8")
    print(f"Wrote {CSS_OUT}")


if __name__ == "__main__":
    main()
