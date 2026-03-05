import json
import os
from typing import Any, Dict, Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class HuggingFaceModelInfoInput(BaseModel):
    """Arguments for querying HuggingFace model metadata."""

    repo_id: str = Field(
        ..., description="Full HuggingFace repo id, e.g. meta-llama/Llama-3-8b"
    )
    include_card: bool = Field(
        default=False,
        description="Whether to attempt fetching the README/card Markdown as well",
    )


class HuggingFaceModelInfoTool(BaseTool):
    name: str = "huggingface_model_info"
    description: str = "Use this tool to fetch live metadata for a HuggingFace model (likes, downloads, tags, license, and optional model card)."
    args_schema: Type[BaseModel] = HuggingFaceModelInfoInput
    return_direct: bool = False
    _timeout: int = 15

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _fetch_json(self, url: str) -> Dict[str, Any]:
        response = requests.get(url, headers=self._headers(), timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def _fetch_card(self, repo_id: str) -> str | None:
        url = f"https://huggingface.co/{repo_id}/raw/main/README.md"
        response = requests.get(url, headers=self._headers(), timeout=self._timeout)
        if response.status_code == 200:
            return response.text
        return None

    def _run(self, repo_id: str, include_card: bool = False) -> str:
        model_url = f"https://huggingface.co/api/models/{repo_id}"

        try:
            result: Dict[str, Any] = self._fetch_json(model_url)
        except requests.HTTPError as exc:
            return json.dumps(
                {
                    "error": "huggingface_model_info_failed",
                    "status_code": exc.response.status_code if exc.response else None,
                    "detail": str(exc),
                }
            )
        except requests.RequestException as exc:  # pragma: no cover - network edge
            return json.dumps({"error": "network_failure", "detail": str(exc)})

        if include_card:
            card = self._fetch_card(repo_id)
            if card:
                result["model_card"] = card[:5000]

        return json.dumps(result)
