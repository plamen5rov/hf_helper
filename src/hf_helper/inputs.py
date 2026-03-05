"""Input helpers for hf_helper."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Mapping

from pydantic import BaseModel, Field, ValidationError, field_validator


HARDWARE_FIELDS = (
    "gpu",
    "cpu",
    "ram",
    "storage",
    "operating_system",
    "usage",
)


_MEMORY_PATTERN = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>tb|gb|mb|bytes)?", re.IGNORECASE
)


def _normalize_capacity(value: Any, target_unit: str) -> str:
    """Normalize textual capacity descriptions into standard units."""

    if isinstance(value, (int, float)):
        numeric = float(value)
        unit = target_unit
    else:
        match = _MEMORY_PATTERN.search(str(value))
        if not match:
            raise ValueError(f"Unable to parse capacity from '{value}'")
        numeric = float(match.group("value"))
        unit = (match.group("unit") or target_unit).upper()

    unit = unit.replace("BYTES", target_unit)
    if unit == "MB":
        numeric /= 1024
        unit = "GB"
    if unit == "GB" and target_unit == "TB":
        numeric /= 1024
    if unit == "TB" and target_unit == "GB":
        numeric *= 1024

    rounded = round(numeric, 2)
    if rounded.is_integer():
        rounded = int(rounded)
    return f"{rounded} {target_unit}"


class HardwareInputs(BaseModel):
    """Validated hardware inputs shared across entry points."""

    gpu: str = Field(..., description="GPU model with memory annotation")
    cpu: str = Field(..., description="CPU model")
    ram: str = Field(..., description="Normalized RAM string in GB")
    storage: str = Field(..., description="Normalized storage string in TB")
    operating_system: str = Field(..., description="Operating system name")
    usage: str = Field(..., description="Primary workload description")
    current_year: int = Field(..., description="Calendar year for prompts")
    crewai_trigger_payload: Dict[str, Any] | None = Field(
        default=None, description="Raw payload forwarded from triggers"
    )

    @field_validator("gpu", "cpu", "operating_system", "usage", mode="before")
    def _require_text(cls, value: Any) -> str:  # noqa: D401
        if not isinstance(value, str):
            value = str(value)
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value must be a non-empty string")
        return cleaned

    @field_validator("ram", mode="before")
    def _normalize_ram(cls, value: Any) -> str:
        return _normalize_capacity(value, "GB")

    @field_validator("storage", mode="before")
    def _normalize_storage(cls, value: Any) -> str:
        return _normalize_capacity(value, "TB")

    @field_validator("current_year", mode="before")
    def _current_year(cls, value: Any) -> int:
        year = int(value) if value is not None else datetime.now().year
        if year < 2020:
            raise ValueError("current_year must reflect the modern era")
        return year

    @classmethod
    def example(cls) -> "HardwareInputs":
        return cls(
            gpu="NVIDIA RTX 4090 24GB",
            cpu="AMD Ryzen 9 7950X",
            ram="64 GB",
            storage="2 TB",
            operating_system="Ubuntu 22.04",
            usage="coding assistant",
            current_year=datetime.now().year,
        )

    def to_inputs(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["current_year"] = str(data["current_year"])
        if data["crewai_trigger_payload"] is None:
            data.pop("crewai_trigger_payload")
        return data


def default_inputs() -> Dict[str, Any]:
    """Return validated defaults for local runs."""

    return HardwareInputs.example().to_inputs()


def merge_trigger_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Overlay trigger payload values onto the default input template."""

    base: Dict[str, Any] = HardwareInputs.example().model_dump()
    merged: Dict[str, Any] = {
        **base,
        **{k: payload.get(k, base.get(k)) for k in HARDWARE_FIELDS},
    }
    merged["crewai_trigger_payload"] = dict(payload)
    merged["current_year"] = datetime.now().year

    try:
        model = HardwareInputs(**merged)
    except ValidationError as exc:
        raise ValueError(f"Invalid trigger payload: {exc}") from exc

    return model.to_inputs()


def build_inputs(overrides: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    """Convenience helper for callers that want to override defaults."""

    if not overrides:
        return default_inputs()

    payload: Dict[str, Any] = {**default_inputs(), **overrides}
    payload.setdefault("current_year", datetime.now().year)

    try:
        model = HardwareInputs(**payload)
    except ValidationError as exc:
        raise ValueError(f"Invalid overrides: {exc}") from exc

    return model.to_inputs()
