"""Unified launcher for the Streamlit frontend + backend crew."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import List


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _build_command(
    port: int | None, no_browser: bool, address: str | None, passthrough: List[str]
) -> List[str]:
    script_path = _project_root() / "streamlit_app.py"
    cmd = ["streamlit", "run", str(script_path)]
    if port:
        cmd += ["--server.port", str(port)]
    if no_browser:
        cmd += ["--server.headless", "true"]
    if address:
        cmd += ["--server.address", address]
    if passthrough:
        cmd.extend(passthrough)
    return cmd


def start() -> None:
    parser = argparse.ArgumentParser(
        description="Start the HF Helper Streamlit frontend (backend runs inline)."
    )
    parser.add_argument("--port", type=int, default=None, help="Streamlit server port")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Run headless (skip automatically opening a browser)",
    )
    parser.add_argument(
        "--address",
        type=str,
        default=None,
        help="Network interface to bind (defaults to Streamlit's default)",
    )
    args, passthrough = parser.parse_known_args()
    cmd = _build_command(args.port, args.no_browser, args.address, passthrough)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - delegated
        raise SystemExit(exc.returncode) from exc


if __name__ == "__main__":  # pragma: no cover
    start()
