"""Expose Tcl/Tk 9's embedded script archives to the build tools if present.

Some Windows Python distributions embed these files inside their Tcl/Tk DLLs
rather than shipping ordinary library folders. Extract only a local build copy.
"""
from pathlib import Path
import sys
import zipfile

destination = Path(__file__).resolve().parent / "toolchain" / "libraries"
for dll in (Path(sys.base_prefix) / "DLLs").glob("*tcl*.dll"):
    if zipfile.is_zipfile(dll):
        with zipfile.ZipFile(dll) as archive:
            for member in archive.infolist():
                target = (destination / member.filename).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise ValueError("Unexpected archive path")
            archive.extractall(destination)
