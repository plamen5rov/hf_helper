from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from hf_helper.crew import HfHelper
from hf_helper.inputs import build_inputs, default_inputs

USAGE_OPTIONS = [
    "chat assistant",
    "coding assistant",
    "image generation",
    "audio generation",
    "multimodal research",
    "custom",
]


st.set_page_config(page_title="HF Helper Recommender", layout="wide")
st.session_state.setdefault("run_history", [])


def _kickoff(inputs: Dict[str, str]) -> Any:
    crew = HfHelper().crew()
    return crew.kickoff(inputs=inputs)


def _load_recommendations(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def _history_table(history: List[Dict[str, str]]) -> None:
    if not history:
        return
    st.subheader("Recent Runs")
    st.dataframe(history[-5:], use_container_width=True)


def main() -> None:
    defaults = default_inputs()
    artifact_path = Path("artifacts/recommendations.md")

    st.title("Hardware-Aware HuggingFace Recommender")
    st.write(
        "Provide your local hardware specs and we will return the best-fitting open-source "
        "LLMs from HuggingFace, complete with pros, cons, and deployment notes."
    )

    with st.form("hardware_form"):
        col1, col2 = st.columns(2)
        with col1:
            gpu = st.text_input("GPU", defaults["gpu"])
            ram = st.text_input("RAM", defaults["ram"])
            operating_system = st.text_input(
                "Operating System", defaults["operating_system"]
            )
        with col2:
            cpu = st.text_input("CPU", defaults["cpu"])
            storage = st.text_input("Storage", defaults["storage"])
            default_usage = defaults.get("usage", USAGE_OPTIONS[0])
            usage_index = (
                USAGE_OPTIONS.index(default_usage)
                if default_usage in USAGE_OPTIONS
                else 0
            )
            usage_choice = st.selectbox(
                "Primary Usage", USAGE_OPTIONS, index=usage_index
            )
            custom_usage = ""
            if usage_choice == "custom":
                custom_usage = st.text_input(
                    "Describe your usage", "retrieval-augmented agent"
                )

        submitted = st.form_submit_button("Recommend Models", use_container_width=True)

    if not submitted:
        st.info("Fill in your specs and click Recommend Models to run the crew.")
        return

    usage_value = custom_usage or usage_choice
    overrides = {
        "gpu": (gpu or "").strip(),
        "cpu": (cpu or "").strip(),
        "ram": (ram or "").strip(),
        "storage": (storage or "").strip(),
        "operating_system": (operating_system or "").strip(),
        "usage": (usage_value or "").strip() or defaults["usage"],
        "current_year": datetime.now().year,
    }

    try:
        inputs = build_inputs(overrides)
    except ValueError as exc:
        st.error(f"Input validation failed: {exc}")
        return

    with st.spinner("Running crew... this may take a minute"):
        try:
            result = _kickoff(inputs)
        except Exception as exc:
            st.error(f"Crew execution failed: {exc}")
            return

    st.success("Recommendation run complete")
    st.session_state.run_history.append(
        {
            "gpu": inputs["gpu"],
            "cpu": inputs["cpu"],
            "usage": inputs["usage"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )

    st.subheader("Crew Output")
    if isinstance(result, dict):
        st.json(result)
    else:
        st.write(result)

    rendered = _load_recommendations(artifact_path)
    if rendered:
        st.subheader("Top 5 Recommendations")
        st.markdown(rendered)
        st.download_button(
            "Download recommendations.md",
            data=rendered,
            file_name="recommendations.md",
            mime="text/markdown",
        )
    else:
        st.warning("recommendations.md not found yet. Check the logs for details.")

    _history_table(st.session_state.run_history)


if __name__ == "__main__":
    main()
