# Frontend Platform Proposal

## Requirements Snapshot
- Collect GPU/CPU/RAM/storage/OS/usage inputs with validation and helpful defaults.
- Call the crew backend (initially via CLI/HTTP) and display streaming or batched results.
- Present the final top-5 models with pros/cons plus hardware fit notes.
- Keep UX approachable for technical but time-constrained users; enable quick iteration as agents evolve.

## Option Comparison

| Platform   | Strengths | Gaps |
|------------|-----------|------|
| Streamlit  | Python-native, fast form building, built-in state/session handling, easy deployment on HF Spaces or Streamlit Cloud. Tight integration with the existing uv/venv workflow, making it trivial to call crew runs or cached recommendations. | Less control over pixel-perfect theming compared to React, but acceptable for our data-heavy UI. |
| Gradio     | Excellent for quick model demos and media components; native support for HuggingFace Spaces hosting. | Form layouts less flexible for mixed text + explanation content, styling is opinionated, and custom navigation (wizard-style spec intake + results) is harder. |
| React SPA  | Full design freedom, large ecosystem for charts/components, easy to integrate with future APIs. | Requires separate frontend stack/tooling, duplicating effort for state management and API clients before the backend stabilizes. Higher barrier for non-frontend contributors. |

## Recommendation

Streamlit is the best near-term fit. We stay inside the Python ecosystem, meaning hardware validation helpers and crew calls can live in the same codebase. Streamlit's form primitives (`st.form`, `st.selectbox`, `st.text_input`) cover all required inputs, while layout APIs (`st.columns`, `st.expander`) make it easy to present the top-5 recommendations with pros/cons and compatibility badges. Deployment on HuggingFace Spaces keeps everything co-located with the models we reference.

The initial implementation ships as `streamlit_app.py`; iterate on that file as new inputs or visualizations are required.

Once requirements stabilize or the UI needs richer branding, we can export a simple REST endpoint and switch the frontend to React without rewriting business logic, but Streamlit minimizes time-to-value right now.
