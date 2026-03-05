#!/usr/bin/env python
import argparse
import json
import logging
import sys
import warnings
from pathlib import Path
from typing import Any, Dict

from hf_helper.crew import HfHelper
from hf_helper.inputs import build_inputs, default_inputs, merge_trigger_payload


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
logger = logging.getLogger(__name__)


def _kickoff(inputs: Dict[str, Any]) -> Any:
    """Kick off the crew with shared logging."""

    snapshot = {k: inputs.get(k) for k in ("gpu", "cpu", "usage") if k in inputs}
    logger.info("hf_helper kickoff", extra={"inputs": snapshot})
    return HfHelper().crew().kickoff(inputs=inputs)


def _parse_train_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="hf_helper.train")
    parser.add_argument("iterations", type=int, help="Number of training iterations")
    parser.add_argument(
        "output_file",
        type=str,
        help="Destination file for training transcripts",
    )
    return parser.parse_args(argv)


def _parse_test_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="hf_helper.test")
    parser.add_argument("iterations", type=int, help="Number of evaluation runs")
    parser.add_argument("llm", type=str, help="LLM name to score outputs")
    return parser.parse_args(argv)


def _parse_replay_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="hf_helper.replay")
    parser.add_argument("task_id", type=str, help="Crew task identifier to replay")
    return parser.parse_args(argv)


def _parse_trigger_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="hf_helper.run_with_trigger")
    parser.add_argument(
        "payload",
        nargs="?",
        help="Inline JSON payload (fallback if no other flags are set)",
    )
    parser.add_argument(
        "--payload-file",
        type=Path,
        help="Path to a JSON file containing the trigger payload",
    )
    parser.add_argument(
        "--payload-json",
        help="Explicit JSON string overriding positional payload",
    )
    return parser.parse_args(argv)


def _load_payload(namespace: argparse.Namespace) -> Dict[str, Any]:
    raw: str | None = namespace.payload_json or namespace.payload
    if namespace.payload_file:
        try:
            raw = namespace.payload_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise Exception(f"Unable to read payload file: {exc}") from exc

    if not raw:
        raise Exception(
            "No trigger payload provided. Supply inline JSON, --payload-json, or --payload-file."
        )

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Exception(f"Invalid JSON payload provided: {exc}") from exc


def run() -> None:
    """Run the crew using default inputs."""

    try:
        _kickoff(default_inputs())
    except Exception as exc:  # pragma: no cover - defensive logging
        raise Exception(f"An error occurred while running the crew: {exc}") from exc


def train() -> None:
    """Train the crew for a given number of iterations."""

    args = _parse_train_args(sys.argv[1:])
    try:
        HfHelper().crew().train(
            n_iterations=args.iterations,
            filename=args.output_file,
            inputs=default_inputs(),
        )
    except Exception as exc:
        raise Exception(f"An error occurred while training the crew: {exc}") from exc


def replay() -> None:
    """Replay the crew execution from a specific task."""

    args = _parse_replay_args(sys.argv[1:])
    try:
        HfHelper().crew().replay(task_id=args.task_id)
    except Exception as exc:
        raise Exception(f"An error occurred while replaying the crew: {exc}") from exc


def test() -> None:
    """Test the crew execution and returns the results."""

    args = _parse_test_args(sys.argv[1:])
    try:
        HfHelper().crew().test(
            n_iterations=args.iterations,
            eval_llm=args.llm,
            inputs=default_inputs(),
        )
    except Exception as exc:
        raise Exception(f"An error occurred while testing the crew: {exc}") from exc


def run_with_trigger() -> Any:
    """Run the crew with trigger payload."""

    namespace = _parse_trigger_args(sys.argv[1:])
    trigger_payload = _load_payload(namespace)
    inputs = merge_trigger_payload(trigger_payload)

    try:
        return _kickoff(inputs)
    except Exception as exc:
        raise Exception(
            f"An error occurred while running the crew with trigger: {exc}"
        ) from exc
