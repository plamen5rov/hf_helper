# AGENTS

Guide for autonomous contributors working in this repo. Treat it as the source of truth for tooling, commands, and coding conventions.

## Quick Facts
- Project name: `hf_helper`, a crewAI-based multi-agent workflow located under `src/hf_helper`.
- Python requirement: 3.10 <= version < 3.14. Install via `uv` for parity with maintainers.
- Dependencies live in `pyproject.toml`; only runtime dep today is `crewai[tools]==1.9.3`.
- Entry points are defined under `[project.scripts]` so `uv run hf_helper` maps to `hf_helper.main:run` (and similar for `train`, `replay`, `test`, `run_with_trigger`).
- No Cursor or Copilot instruction files exist right now, so this document is the standing policy for agents.

## Repository Layout (paths relative to repo root)
- `src/hf_helper/crew.py` — crew wiring plus agent/task factories via decorators.
- `src/hf_helper/main.py` — script-style helpers that wrap crew operations (run/train/replay/test/trigger).
- `src/hf_helper/config/agents.yaml` — agent personas keyed by `researcher` and `reporting_analyst`.
- `src/hf_helper/config/tasks.yaml` — task descriptions plus expected outputs and agent bindings.
- `src/hf_helper/tools/custom_tool.py` — template for extending crew tools using `BaseTool`.
- `artifacts/` — runtime output directory (e.g., `recommendations.md`) created automatically.
- `knowledge/` — supplemental context (currently `user_preference.txt`). Keep personally identifying info here if needed.
- `tests/` — placeholder package for automated tests (empty today; add modules here).
- `.env` — user-managed secrets (e.g., `OPENAI_API_KEY`). Never commit.

## Environment Setup
- Install uv globally once: `pip install uv`.
- Create a virtualenv managed by uv: `uv venv --python 3.11` (or desired minor version within range).
- Sync dependencies: `uv sync` (reads `pyproject.toml` and creates `.venv`).
- Activate env when using shells: `source .venv/bin/activate` or rely on `uv run <cmd>` to auto-spawn the environment.
- Add secrets to `.env`; at minimum set `OPENAI_API_KEY` for crewAI LLM calls.
- For local experimentation with alternative LLM providers, export their keys in the shell just-in-time instead of storing them in the repo.

## Build & Execution Commands
- **One-line app launch:** `uv run start_app --port 8501` boots the Streamlit UI and backend in one go (use `--no-browser` for headless servers).
- **Run crew with defaults:** `uv run crewai run` (loads configs, uses inputs embedded in tasks). Reports land in `artifacts/recommendations.md`.
- **Run via module entry point:** `uv run hf_helper` (alias for `hf_helper.main:run`).
- **Pass dynamic inputs:** `uv run crewai run --inputs-file path/to/inputs.json` or adjust `inputs` dict in `main.py` before running.
- **Train loop:** `uv run train 3 logs/training.jsonl` (arguments: iterations, output filename).
- **Replay a task:** `uv run replay <task_id>` (task ID taken from prior run artifacts).
- **Evaluate/test crew:** `uv run test 3 gpt-4o-mini` (iterations + eval LLM name).
- **Trigger mode:** `uv run run_with_trigger '{"topic": "LLM safety"}'` (stringified JSON payload as first arg) or `uv run run_with_trigger --payload-file path/to/payload.json`. Arg parsing now uses `argparse`, so named flags are available.
- **Packaging build:** `uv build` (produces wheel + sdist using hatchling; required before publishing to an index).
- Prefer `uv run python -m hf_helper.main` when you need to call specific helper functions for ad-hoc automation scripts.

## Linting & Formatting
- Repo does not ship a dedicated lint config; use `ruff` as the lightweight default.
- Install lint tool once: `uv tool install ruff` (or add `ruff` to `[project.optional-dependencies.dev]` if standardizing).
- **Full lint sweep:** `uv run ruff check src tests`.
- **Auto-fix safe issues:** `uv run ruff check src tests --fix` (review diff afterward).
- Formatting preference: rely on `ruff format` (Black-compatible) instead of maintaining a separate formatter.
- **Format command:** `uv run ruff format src tests`.
- When editing YAML, keep indentation at two spaces to align with crewAI documentation (see existing `config/*.yaml`).
- Document tooling gaps in PR descriptions if you introduce a new formatter or static analysis tool so the next agent can add it here.

## Testing Workflow
- Testing stack is `pytest`. Add `pytest` to your environment (`uv add --dev pytest` or `uv pip install pytest`) — metadata already exposes `pytest` under the `dev` optional dependency for convenience.
- Sample unit tests live in `tests/test_inputs.py` and cover the `HardwareInputs` validators; follow that pattern for future utilities.
- **Run complete suite:** `uv run pytest` (default discovery under `tests/`).
- **Focused file:** `uv run pytest tests/test_agent_logic.py`.
- **Single test function:** `uv run pytest tests/test_agent_logic.py -k test_handles_empty_prompt` (preferred way to satisfy "single test" requirement).
- **Looping stress test:** `uv run pytest tests -k critical --maxfail=1 --durations=10` when investigating flakiness.
- Populate fixtures that boot the crew through `HfHelper().crew()` instead of mocking internals; the scaffolding is lightweight and stable.
- Maintain parity between CLI helper functions (`run`, `train`, etc.) and tests—if you add new keyword-only args, update both tests and the `main.py` wrappers.
- Stick to deterministic mocks for external APIs (LLM calls) using pytest monkeypatching so agents can re-run tests offline.

## Coding Standards — Imports
- Import order: standard library, third-party (crewai, pydantic, etc.), local modules (hf_helper.*). Separate groups with a blank line.
- Avoid wildcard imports; prefer explicit symbols (`from crewai import Agent, Crew` as seen in `crew.py`).
- Use relative imports only within subpackages when staying inside `hf_helper` (e.g., `.config`), but prefer absolute paths for clarity in tests.
- Keep typing imports (`List`, `Type`) alongside other stdlib imports; rely on `from __future__ import annotations` only if you hit circular type references.

## Coding Standards — Formatting & Structure
- Follow Black/PEP-8 defaults: 4-space indents, 88-char soft limit (90 acceptable when string literals demand it).
- Use trailing commas in multi-line literals to keep diffs minimal.
- Multi-line dictionaries in YAML should maintain one key per line with folded scalars (see `agents.yaml`).
- Prefer f-strings for string interpolation (`f"An error occurred: {e}"`) and keep messages human-readable.
- Reserve inline comments for clarifying non-obvious behavior; keep them short and aligned with the code they annotate.

## Coding Standards — Typing & Data Contracts
- Public functions and methods must carry type hints for all parameters and return values; default to `-> None` when no value is returned.
- Use `TypedDict`/`Protocol` when passing structured dictionaries across modules instead of relying on `dict[str, Any]`.
- For Pydantic models (see `MyCustomToolInput`), document each field with `Field(..., description="...")` so downstream agents have schema insight.
- Prefer enums or `Literal` annotations when valid values are finite (e.g., process modes, agent role types).
- Capture external payloads (trigger JSON) in dedicated dataclasses or Pydantic models before handing them to crews.

## Coding Standards — Naming
- Functions: snake_case verbs that explain intent (`run_with_trigger`, `research_task`).
- Classes: PascalCase nouns (`MyCustomTool`).
- Configuration keys: lowercase snake_case (already established in YAML files).
- Module-level constants: UPPER_SNAKE (add `DEFAULT_TOPIC = "AI LLMs"` if you find yourself reusing values).
- Avoid abbreviations unless the term is ubiquitous (LLM, API, ID). Expand everything else for clarity.

## Coding Standards — Error Handling & Logging
- Wrap crew executions in try/except blocks that re-raise context-rich exceptions, as shown in `main.py`. Maintain that pattern for new entry points.
- Prefer raising domain-specific exceptions (e.g., `CrewConfigurationError`) when validation fails before execution.
- Validate CLI arguments early (length/type checks) and emit actionable error messages.
- When introducing logging, configure a module-level logger via `logging.getLogger(__name__)` and keep log lines structured (`logger.info("Kickoff started", extra={...})`).
- Never swallow exceptions silently; at minimum re-raise with additional context.

## Configuration & Secrets
- Keep agent/task definitions declarative in `config/`. Update YAML instead of hardcoding values inside Python; the HuggingFace model scout now expects the `huggingface_model_info` tool to be available per `agents.yaml`.
- Use placeholders (`{topic}`, `{current_year}`) consistently; document any new placeholders at the top of the YAML file you touch.
- Secrets belong in `.env` and are loaded by crewAI automatically. Never bake tokens into code or sample configs committed to git.
- If you add provider-specific settings (e.g., Anthropic keys), gate them behind environment checks and document them here.

## Knowledge & Data Files
- Store reusable textual context under `knowledge/` and reference it via crewAI knowledge sources when appropriate.
- Keep knowledge files small, plain text or markdown, and scoped to a single subject to avoid cross-contamination.
- Capture provenance inside the file (source, date) so future agents can decide when to refresh it.
- Large or binary assets should live outside the repo; link to external storage instead.

## Collaboration & Process
- Before editing, run `git status` to understand existing changes; never reset user work.
- Prefer small, focused PRs; describe both the change and why it matters (align with this guide's terminology).
- Update this `AGENTS.md` whenever you introduce a new command, dependency, or workflow expectation.
- When adding tests or tools, include at least one usage example in this document so autonomous agents can act without guesswork.
- If you discover repo-specific caveats (e.g., long-running crew tasks), record mitigations here for future operators.

## Crew Configuration Tips
- Treat `src/hf_helper/config/agents.yaml` and `tasks.yaml` as the single source of truth; prefer YAML updates over inline Python tweaks.
- Use descriptive roles/goals/backstories so crewAI prompt templates stay coherent as tasks evolve.
- Keep placeholders (`{topic}`, `{current_year}`) synchronized between YAML and the `inputs` dict in `main.py`.
- Document any new required inputs as module-level constants and propagate them to CLI helpers plus tests.
- When experimenting with `Process.hierarchical`, annotate rationale and revert path inside PR notes.
- Save sample outputs (e.g., `report.md`) when they demonstrate a new behavior, but clean up large artifacts before committing.

## Tool Development Checklist
- Extend `BaseTool` subclasses inside `src/hf_helper/tools/`; keep each tool self-contained with clear descriptions.
- Define `args_schema` using Pydantic models that include per-field docstrings via `Field(..., description=...)`.
- Keep tool side effects idempotent; if you must mutate external state, add retry/backoff guards and document expectations.
- Add minimal usage tests under `tests/` to lock API contracts before wiring new tools into agents.
- Record any external dependencies (APIs, CLI utilities) near the tool implementation and mirror them in `AGENTS.md`.
- Prefer returning structured dictionaries over raw strings when downstream tasks need to branch on tool output.

## Performance & Resource Use
- Enable `verbose=False` for non-debug runs if you script repeated executions to cut down on console noise.
- Cache expensive HTTP responses or file reads inside tools to avoid rate limits when crews iterate over similar prompts.
- Keep generated artifacts (reports, logs) under version control only if they serve as fixtures; otherwise add them to `.gitignore`.
- When benchmarking, record command timings (e.g., `time uv run crewai run`) so future agents understand baseline performance.
- If you hit API throttling, encode wait strategies in code rather than manual pauses, and document the limits here.
- For long-lived runs, prefer `uv run` over activating the venv manually so dependency resolution stays deterministic.

## Git & Review Expectations
- Work on topic branches; reserve `main` for stable states unless explicitly testing a hotfix.
- Commit messages should summarize "why" rather than "what" (e.g., `explain: clarify trigger payload validation`).
- Never amend or force-push shared commits without owner approval; coordinate via PR comments if history surgery is required.
- Include reproduction steps (commands, inputs) in PR descriptions whenever you touch runtime behavior.
- Run lint + targeted tests before opening a PR; paste command outputs or summaries so reviewers can trust the state.
- Tag reviewers on sections they own (agents, tools, configs) and highlight any backward-incompatible changes.

End of guide — keep this close to ~150 lines by pruning outdated info when adding new sections.
