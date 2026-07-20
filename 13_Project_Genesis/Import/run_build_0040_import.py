from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BUILD_NUMBER = "0040"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Build 0040 transactional import")
    parser.add_argument("zip_path")
    parser.add_argument("repository_path")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--asset-register", default="Documentation/Master_Asset_Register.csv")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    importer = Path(__file__).with_name("transactional_build_import.py")
    report = args.report
    command = [
        sys.executable,
        "-B",
        str(importer),
        args.zip_path,
        args.repository_path,
        "--asset-register",
        args.asset_register,
        "--report",
        report,
    ]
    if args.apply:
        command.append("--apply")
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
