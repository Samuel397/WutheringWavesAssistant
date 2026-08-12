"""Compile the Qt translations and embedded GUI resources."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

try:
    import PySide6
except ImportError:  # pragma: no cover - handled by find_tool's error below
    PySide6 = None

from build_gui_translations import I18N_ROOT, ROOT, main as build_catalog_main


RESOURCE_ROOT = ROOT / "src" / "gui" / "resource"
RESOURCE_OUTPUT = ROOT / "src" / "gui" / "common" / "resource.py"


def find_tool(name: str) -> str:
    package_tool = None
    if PySide6 is not None:
        package_tool = str(Path(PySide6.__file__).resolve().parent / f"{name}.exe")
    candidates = (
        shutil.which(f"pyside6-{name}"),
        shutil.which(name),
        package_tool,
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise FileNotFoundError(
        f"Qt tool {name!r} was not found. Run this script with the project's PySide6 environment."
    )


def build() -> None:
    if build_catalog_main() != 0:
        raise SystemExit(1)
    lrelease = find_tool("lrelease")
    rcc = find_tool("rcc")
    subprocess.run(
        [lrelease, str(I18N_ROOT / "gallery.pt_BR.ts"), "-qm", str(I18N_ROOT / "gallery.pt_BR.qm")],
        check=True,
    )
    subprocess.run(
        [rcc, "-g", "python", str(RESOURCE_ROOT / "resource.qrc"), "-o", str(RESOURCE_OUTPUT)],
        check=True,
    )
    print(f"Wrote {RESOURCE_OUTPUT.relative_to(ROOT)}")


def check() -> int:
    catalog_args = sys.argv
    try:
        sys.argv = [catalog_args[0], "--check"]
        if build_catalog_main() != 0:
            return 1
    finally:
        sys.argv = catalog_args

    lrelease = find_tool("lrelease")
    rcc = find_tool("rcc")
    with tempfile.TemporaryDirectory(prefix="wwa-qt-") as directory:
        temp = Path(directory)
        qm = temp / "gallery.pt_BR.qm"
        resource = temp / "resource.py"
        subprocess.run([lrelease, str(I18N_ROOT / "gallery.pt_BR.ts"), "-qm", str(qm)], check=True)
        subprocess.run(
            [rcc, "-g", "python", str(RESOURCE_ROOT / "resource.qrc"), "-o", str(resource)], check=True
        )
        if qm.read_bytes() != (I18N_ROOT / "gallery.pt_BR.qm").read_bytes():
            print("src/gui/resource/i18n/gallery.pt_BR.qm is stale")
            return 1
        if resource.read_bytes() != RESOURCE_OUTPUT.read_bytes():
            print("src/gui/common/resource.py is stale")
            return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify that generated files are current")
    args = parser.parse_args()
    if args.check:
        return check()
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
