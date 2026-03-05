from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from hf_helper.crew import HfHelper
from hf_helper.inputs import default_inputs

USAGE_OPTIONS = [
    "chat assistant",
    "coding assistant",
    "image generation",
    "audio generation",
    "multimodal research",
    "custom",
]


st.set_page_config(page_title="HF Helper Recommender", layout="wide")


def _kickoff(inputs: Dict[str, str]) -> Any:
    crew = HfHelper().crew()
    return crew.kickoff(inputs=inputs)


def _load_recommendations() -> str | None:
    path = Path("recommendations.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def main() -> None:
    defaults = default_inputs()

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

        submitted = st.form_submit_button("Recommend Models")

    if not submitted:
        st.info("Fill in your specs and click Recommend Models to run the crew.")
        return

    usage_value = custom_usage or usage_choice
    inputs = {
        "gpu": gpu.strip(),
        "cpu": cpu.strip(),
        "ram": ram.strip(),
        "storage": storage.strip(),
        "operating_system": operating_system.strip(),
        "usage": usage_value.strip() or defaults["usage"],
        "current_year": str(datetime.now().year),
    }

    with st.spinner("Running crew... this may take a minute"):
        try:
            result = _kickoff(inputs)
        except Exception as exc:
            st.error(f"Crew execution failed: {exc}")
            return

    st.success("Recommendation run complete")

    st.subheader("Crew Output")
    if isinstance(result, dict):
        st.json(result)
    else:
        st.write(result)

    rendered = _load_recommendations()
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


if __name__ == "__main__":
    main()
