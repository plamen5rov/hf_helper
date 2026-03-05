from hf_helper.inputs import (
    HardwareInputs,
    build_inputs,
    default_inputs,
    merge_trigger_payload,
)


def test_default_inputs_are_normalized() -> None:
    defaults = default_inputs()
    assert defaults["ram"].endswith("GB")
    assert defaults["storage"].endswith("TB")
    assert defaults["current_year"].isdigit()


def test_merge_trigger_payload_overrides_fields() -> None:
    payload = {"gpu": "NVIDIA RTX 3080 10GB", "ram": "32GB", "usage": "chat"}
    merged = merge_trigger_payload(payload)

    assert merged["gpu"] == payload["gpu"]
    assert merged["ram"].startswith("32")
    assert merged["usage"] == "chat"


def test_build_inputs_validates_numeric_fields() -> None:
    overrides = {"ram": "16384 MB", "storage": "2048 GB"}
    inputs = build_inputs(overrides)

    assert inputs["ram"].startswith("16")
    assert inputs["storage"].startswith("2")


def test_hardware_inputs_rejects_bad_year() -> None:
    try:
        HardwareInputs(
            gpu="GPU",
            cpu="CPU",
            ram="1 GB",
            storage="1 TB",
            operating_system="Ubuntu",
            usage="chat",
            current_year=2010,
        )
    except ValueError:
        return

    raise AssertionError("HardwareInputs should reject years before 2020")
