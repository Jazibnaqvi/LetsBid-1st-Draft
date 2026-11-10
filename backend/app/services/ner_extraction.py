from typing import Any

from pydantic import ValidationError

from app.core.config import settings
from app.schemas.documents import DocumentIngestionResponse, TextSegment
from app.schemas.ner import (
    BudgetFigure,
    ComplianceClause,
    EvaluationCriterion,
    EvaluationWeight,
    MandatoryRequirement,
    NerEntities,
    NerExtractionMetadata,
    NerExtractionResponse,
    QuestionAnswerSection,
    SubmissionDeadline,
)
from app.services.gemini_client import GeminiClient, GeminiClientError, get_gemini_client

ENTITY_FIELD_MODELS: dict[str, type] = {
    "mandatory_requirements": MandatoryRequirement,
    "evaluation_criteria": EvaluationCriterion,
    "submission_deadlines": SubmissionDeadline,
    "question_answer_sections": QuestionAnswerSection,
    "budget_figures": BudgetFigure,
    "evaluation_weights": EvaluationWeight,
    "compliance_clauses": ComplianceClause,
}

NER_SYSTEM_INSTRUCTION = """You are a Named Entity Recognition (NER) system for bid, RFP, and proposal documents.

Your task is ENTITY EXTRACTION ONLY. Do NOT summarize the document, rewrite content, or produce generic analysis.

Extract ONLY these entity types:
1. mandatory_requirements — binding obligations bidders must satisfy
2. evaluation_criteria — factors used to score or rank proposals
3. submission_deadlines — dates/times for submissions or related milestones
4. question_answer_sections — explicit Q&A pairs or FAQ blocks
5. budget_figures — monetary amounts, ceilings, or funding limits
6. evaluation_weights — percentage or weighted scoring allocations
7. compliance_clauses — legal, regulatory, certification, or contractual compliance terms

Required fields for EVERY entity:
- text: short normalized summary of the entity (required)
- source_quote: verbatim excerpt from the input (required)
- page: integer page number from segment markers, or null
- section: section/heading from segment markers, or null

Additional required fields:
- submission_deadlines: date_text (deadline exactly as written in the document)
- question_answer_sections: question (required), answer (optional if not stated)

Rules:
- NEVER return an entity without both text and source_quote.
- Use page and section when segment markers provide them; otherwise null.
- If an entity type is absent, return an empty list for that field.
- Do not invent entities not supported by the source text.
- Prefer precision over recall; omit uncertain extractions.
"""


def _coerce_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value).strip() or None


def _normalize_page(value: Any) -> int | None:
    if value is None or value == "unknown":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_section(value: Any) -> str | None:
    if not value or value == "unknown":
        return None
    return str(value).strip()


def _normalize_base_entity(item: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    source_quote = _coerce_str(item.get("source_quote"))
    if not source_quote:
        return None

    text = _coerce_str(item.get("text")) or source_quote
    return {
        **item,
        "text": text,
        "source_quote": source_quote,
        "page": _normalize_page(item.get("page")),
        "section": _normalize_section(item.get("section")),
    }


def _normalize_deadline(item: dict[str, Any]) -> dict[str, Any] | None:
    normalized = _normalize_base_entity(item)
    if not normalized:
        return None
    normalized["date_text"] = _coerce_str(item.get("date_text")) or normalized["text"]
    return normalized


def _normalize_question_answer(item: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    source_quote = _coerce_str(item.get("source_quote"))
    if not source_quote:
        return None

    return {
        "question": _coerce_str(item.get("question")) or source_quote,
        "answer": _coerce_str(item.get("answer")),
        "source_quote": source_quote,
        "page": _normalize_page(item.get("page")),
        "section": _normalize_section(item.get("section")),
    }


def _normalize_ner_response(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {field: [] for field in ENTITY_FIELD_MODELS}

    normalized: dict[str, Any] = {}
    for field_name in ENTITY_FIELD_MODELS:
        items = raw.get(field_name, [])
        if not isinstance(items, list):
            items = []

        cleaned: list[dict[str, Any]] = []
        for item in items:
            if field_name == "submission_deadlines":
                entry = _normalize_deadline(item)
            elif field_name == "question_answer_sections":
                entry = _normalize_question_answer(item)
            else:
                entry = _normalize_base_entity(item)
            if entry:
                cleaned.append(entry)

        normalized[field_name] = cleaned

    return normalized


def _parse_entities_lenient(raw: dict[str, Any]) -> NerEntities:
    normalized = _normalize_ner_response(raw)
    parsed: dict[str, list] = {}

    for field_name, model_class in ENTITY_FIELD_MODELS.items():
        entities: list = []
        for item in normalized.get(field_name, []):
            try:
                entities.append(model_class.model_validate(item))
            except ValidationError:
                continue
        parsed[field_name] = entities

    return NerEntities(**parsed)


def _format_segments_for_ner(segments: list[TextSegment]) -> str:
    blocks: list[str] = []
    for segment in segments:
        page = segment.page if segment.page is not None else "unknown"
        section = segment.section if segment.section else "unknown"
        blocks.append(
            f"[SEGMENT index={segment.index} page={page} section={section}]\n{segment.text}"
        )
    return "\n\n".join(blocks)


def _prepare_ner_input(
    text: str | None = None,
    ingestion: DocumentIngestionResponse | None = None,
) -> tuple[str, int, bool]:
    if ingestion is not None:
        source_text = _format_segments_for_ner(ingestion.segments)
        char_count = len(source_text)
    elif text is not None:
        source_text = text.strip()
        char_count = len(source_text)
    else:
        raise ValueError("Either text or ingestion output is required for NER.")

    if char_count == 0:
        raise ValueError("Input text is empty.")

    truncated = False
    max_chars = settings.ner_max_input_chars
    if char_count > max_chars:
        source_text = source_text[:max_chars]
        truncated = True

    return source_text, char_count, truncated


def _build_prompt(source_text: str) -> str:
    return (
        f"{NER_SYSTEM_INSTRUCTION}\n\n"
        "Extract entities from the following document content:\n\n"
        f"{source_text}"
    )


def _entity_counts(entities: NerEntities) -> dict[str, int]:
    return {
        "mandatory_requirements": len(entities.mandatory_requirements),
        "evaluation_criteria": len(entities.evaluation_criteria),
        "submission_deadlines": len(entities.submission_deadlines),
        "question_answer_sections": len(entities.question_answer_sections),
        "budget_figures": len(entities.budget_figures),
        "evaluation_weights": len(entities.evaluation_weights),
        "compliance_clauses": len(entities.compliance_clauses),
    }


def extract_entities(
    *,
    text: str | None = None,
    ingestion: DocumentIngestionResponse | None = None,
    client: GeminiClient | None = None,
) -> NerExtractionResponse:
    source_text, input_char_count, truncated = _prepare_ner_input(text=text, ingestion=ingestion)
    gemini = client or get_gemini_client()
    prompt = _build_prompt(source_text)

    try:
        raw = gemini.generate_structured_json(prompt, NerEntities.model_json_schema())
        entities = _parse_entities_lenient(raw)
    except GeminiClientError:
        raise
    except Exception as exc:
        raise GeminiClientError(f"NER extraction failed: {exc}") from exc

    return NerExtractionResponse(
        task="ner",
        metadata=NerExtractionMetadata(
            model=settings.gemini_model,
            input_char_count=input_char_count,
            truncated=truncated,
            entity_counts=_entity_counts(entities),
        ),
        entities=entities,
    )
