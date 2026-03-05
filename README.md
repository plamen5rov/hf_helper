# HfHelper Crew

Welcome to the HfHelper Crew project, powered by [crewAI](https://crewai.com). This codebase now focuses on recommending the best open-source HuggingFace LLMs for a user's hardware profile. A hardware-focused crew gathers specs, scouts models, and judges the top 5 recommendations that fit GPU/CPU/RAM/storage constraints. See `docs/objective.md` for the canonical objective.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/hf_helper/config/agents.yaml` to define your agents
- Modify `src/hf_helper/config/tasks.yaml` to define your tasks
- Modify `src/hf_helper/crew.py` to add your own logic, tools and specific args
- Modify `src/hf_helper/main.py` to add custom inputs for your agents and tasks

## Required Inputs

Provide the following fields (either via CLI helpers or a future frontend):

- GPU (e.g., `NVIDIA RTX 4090 24GB`)
- CPU (e.g., `AMD Ryzen 9 7950X`)
- RAM (e.g., `64GB DDR5`)
- Storage (e.g., `2TB NVMe SSD` plus free space)
- Operating system (e.g., `Ubuntu 22.04`)
- Usage type (chat, coding, image generation, etc.)

Each helper in `main.py` seeds realistic defaults via `default_inputs()` so you can run locally without a UI yet.

## Crew Workflow

1. **Hardware Agent** (`gather_hardware_task`) normalizes the supplied specs and highlights constraints.
2. **HuggingFace Specialist** (`scout_models_task`) returns a shortlist of 10 compatible models with quantization/compatibility notes.
3. **Judge** (`judge_task`) selects the best 5, summarizing pros, cons, and deployment caveats. The final task writes `recommendations.md` in the project root.

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the hf-helper Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example now creates `recommendations.md` containing the judged top 5 HuggingFace models tailored to the sample hardware inputs.

## Streamlit UI (beta)

Launch the optional frontend with:

```bash
uv run streamlit run streamlit_app.py
```

Enter your specs in the form and the app will trigger the crew, render the Markdown recommendations inline, and expose a download button once the file is generated.

## Frontend Direction

See `docs/frontend_proposal.md` for the rationale behind picking Streamlit first and how it compares to Gradio and React.

## Understanding Your Crew

The hf-helper Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the HfHelper Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
