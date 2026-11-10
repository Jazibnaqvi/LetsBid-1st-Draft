import json
from typing import Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.core.config import settings

_GEMINI_SCHEMA_SKIP_KEYS = frozenset({"$defs", "$schema", "default", "title", "description"})


def _resolve_schema_node(node: Any, defs: dict[str, Any]) -> Any:
    if not isinstance(node, dict):
        return node

    if "$ref" in node:
        ref = node["$ref"]
        if ref.startswith("#/$defs/"):
            def_name = ref.rsplit("/", 1)[-1]
            if def_name in defs:
                return _resolve_schema_node(defs[def_name], defs)
        return node

    if "anyOf" in node and isinstance(node["anyOf"], list):
        non_null = [
            item
            for item in node["anyOf"]
            if item != {"type": "null"} and item.get("type") != "null"
        ]
        if len(non_null) == 1:
            return _resolve_schema_node(non_null[0], defs)

    resolved: dict[str, Any] = {}
    for key, value in node.items():
        if key in _GEMINI_SCHEMA_SKIP_KEYS:
            continue
        if key == "properties" and isinstance(value, dict):
            resolved[key] = {
                prop: _resolve_schema_node(prop_schema, defs) for prop, prop_schema in value.items()
            }
        elif key in ("items", "additionalProperties") and isinstance(value, dict):
            resolved[key] = _resolve_schema_node(value, defs)
        elif key in ("anyOf", "allOf", "oneOf") and isinstance(value, list):
            resolved[key] = [_resolve_schema_node(item, defs) for item in value]
        elif isinstance(value, dict):
            resolved[key] = _resolve_schema_node(value, defs)
        elif isinstance(value, list):
            resolved[key] = [
                _resolve_schema_node(item, defs) if isinstance(item, dict) else item for item in value
            ]
        else:
            resolved[key] = value
    return resolved


def sanitize_schema_for_gemini(schema: dict[str, Any]) -> dict[str, Any]:
    """Flatten Pydantic JSON Schema ($defs/$ref) for Gemini response_schema."""
    defs = schema.get("$defs", {})
    root = {key: value for key, value in schema.items() if key not in ("$defs", "$schema")}
    return _resolve_schema_node(root, defs)


class GeminiClientError(Exception):
    pass


class GeminiClient:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise GeminiClientError("GEMINI_API_KEY is not configured.")
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(settings.gemini_model)

    def generate_structured_json(self, prompt: str, response_schema: dict[str, Any]) -> dict[str, Any]:
        gemini_schema = sanitize_schema_for_gemini(response_schema)
        config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=gemini_schema,
        )
        try:
            response = self._model.generate_content(prompt, generation_config=config)
        except Exception as exc:
            raise GeminiClientError(f"Gemini request failed: {exc}") from exc

        raw_text = getattr(response, "text", None)
        if not raw_text:
            raise GeminiClientError("Gemini returned an empty response.")

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise GeminiClientError("Gemini returned invalid JSON.") from exc


def get_gemini_client() -> GeminiClient:
    return GeminiClient()


