"""Check the local report dependencies before building and in the bundle."""
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class ReportLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.local_paths = set()

    def handle_starttag(self, tag, attributes):
        for name, value in attributes:
            if name in ("src", "href") and value:
                url = urlsplit(value)
                if not url.scheme and not url.netloc and url.path:
                    self.local_paths.add(unquote(url.path))


root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
report_dir = root / "outputs" / "seasons"
parser = ReportLinks()
parser.feed((report_dir / "report.html").read_text(encoding="utf-8"))
required = parser.local_paths | {"daily_weather_with_seasons.csv", "report.html"}
for name in sorted(required):
    if not (report_dir / name).is_file():
        raise FileNotFoundError(f"Missing runtime asset: {report_dir / name}")
print(f"Verified {len(required)} report/data files under {report_dir}")

if len(sys.argv) == 1:
    import PyInstaller
    import pandas
    import matplotlib
    import tkinter
    window = tkinter.Tk()
    window.withdraw()
    print(f"Build dependencies available; Tcl/Tk {window.tk.call('info', 'patchlevel')}")
    window.destroy()
