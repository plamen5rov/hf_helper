from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

HARDWARE_FIELDS = [
    "gpu",
    "cpu",
    "ram",
    "storage",
    "operating_system",
    "usage",
]


def default_inputs() -> Dict[str, str]:
    """Return a sample hardware profile for local runs."""
    return {
        "gpu": "NVIDIA RTX 4090 24GB",
        "cpu": "AMD Ryzen 9 7950X",
        "ram": "64GB DDR5",
        "storage": "2TB NVMe SSD",
        "operating_system": "Ubuntu 22.04",
        "usage": "coding assistant",
        "current_year": str(datetime.now().year),
    }


def merge_trigger_payload(payload: Dict[str, Any]) -> Dict[str, str]:
    """Overlay trigger payload values onto the default input template."""
    merged = default_inputs()
    merged["crewai_trigger_payload"] = payload

    for field in HARDWARE_FIELDS:
        if field in payload:
            merged[field] = str(payload[field])

    merged["current_year"] = str(datetime.now().year)
    return merged
