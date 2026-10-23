"""Read-only discovery for the current Python and local math/PDF tools."""
import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import sys
from pathlib import Path


def inspect():
    packages = {}
    for module, distribution in {
        "sympy": "sympy", "pypdf": "pypdf", "PIL": "Pillow",
        "matplotlib": "matplotlib", "markitdown": "markitdown",
    }.items():
        try:
            available = importlib.util.find_spec(module) is not None
            version = importlib.metadata.version(distribution) if available else None
        except (ImportError, ValueError, importlib.metadata.PackageNotFoundError):
            available, version = False, None
        packages[module] = {"available": available, "version": version}
    binaries = {name: shutil.which(name) for name in ("xelatex", "tectonic", "latexmk", "pdftoppm")}
    if not binaries["xelatex"] and os.environ.get("LOCALAPPDATA"):
        candidate = Path(os.environ["LOCALAPPDATA"]) / "Programs/MiKTeX/miktex/bin/x64/xelatex.exe"
        if candidate.is_file():
            binaries["xelatex"] = str(candidate)
    return {
        "python": sys.executable, "python_version": platform.python_version(),
        "platform": platform.system(), "packages": packages, "binaries": binaries,
        "note": "Discovery only; fonts, TeX packages, website access and visual review are not verified.",
    }


if __name__ == "__main__":
    print(json.dumps(inspect(), ensure_ascii=False, indent=2))
