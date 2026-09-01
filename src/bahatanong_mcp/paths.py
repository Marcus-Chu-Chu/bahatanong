"""Path resolution for package data and BahaMap inputs."""
import os
from pathlib import Path

# Editable install: this file lives in src/bahatanong_mcp/, data/ sits beside it.
DATA_DIR = Path(__file__).resolve().parent / "data"

# BahaMap processed outputs (build-time input only; the served app never reads it).
# Default assumes the sibling checkout used on Marcus's machine.
BAHAMAP_PROCESSED = Path(
    os.environ.get(
        "BAHAMAP_PROCESSED",
        Path(__file__).resolve().parents[3] / "bahamap" / "data" / "processed",
    )
)
