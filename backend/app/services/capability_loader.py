import csv
import io
import re
from pathlib import Path

from app.core.config import settings
from app.schemas.capability import CapabilityRecord

# PS1 export headers -> canonical field names
_COLUMN_ALIASES: dict[str, str] = {
    "cap id": "capability_id",
    "capability_id": "capability_id",
    "domain": "domain",
    "title": "title",
    "project summary": "description",
    "description": "description",
    "certification": "certifications",
    "certifications": "certifications",
    "year completed": "project_year",
    "project_year": "project_year",
    "contract value": "contract_value",
    "min_contract_value": "min_contract_value",
    "max_contract_value": "max_contract_value",
    "duration (months)": "duration_months",
    "client type": "client_types",
    "client_types": "client_types",
    "bid_outcome": "bid_outcome",
    "evidence_text": "evidence_text",
    "proof_document": "proof_document",
}

_HEADER_MARKERS = ("cap id", "capability_id")


def _parse_list_field(value: str) -> list[str]:
    if not value:
        return []
    cleaned = value.strip()
    if cleaned.upper() in {"N/A", "NA", "NONE", "-"}:
        return []
    return [item.strip() for item in cleaned.split(";") if item.strip()]


def _parse_pkr_value(value: str) -> float:
    """Parse values like 'PKR 15M' into numeric PKR amounts."""
    if not value:
        return 0.0
    text = value.strip().upper().replace(",", "")
    text = re.sub(r"^PKR\s*", "", text)
    match = re.match(r"([\d.]+)\s*([KMB])?", text)
    if not match:
        try:
            return float(text)
        except ValueError:
            return 0.0
    amount = float(match.group(1))
    suffix = match.group(2)
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    if suffix:
        amount *= multipliers.get(suffix, 1)
    return amount


def _normalize_key(key: str | None) -> str | None:
    if key is None:
        return None
    return _COLUMN_ALIASES.get(key.strip().lstrip("\ufeff").lower())


def _find_header_line_index(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        lower = line.lower()
        if any(marker in lower for marker in _HEADER_MARKERS):
            return index
    return 0


def _normalize_row(row: dict[str, str | None]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in row.items():
        canonical = _normalize_key(key)
        if canonical and value is not None:
            normalized[canonical] = value.strip()
    return normalized


def _row_to_record(row: dict[str, str]) -> CapabilityRecord | None:
    capability_id = row.get("capability_id", "").strip()
    if not capability_id or capability_id.lower().startswith("ps1"):
        return None

    domain = row.get("domain", "").strip()
    description = row.get("description", "").strip()
    title = row.get("title", "").strip() or domain

    certifications = _parse_list_field(row.get("certifications", ""))
    client_types = _parse_list_field(row.get("client_types", ""))

    if row.get("min_contract_value"):
        min_value = float(row["min_contract_value"])
    elif row.get("contract_value"):
        min_value = _parse_pkr_value(row["contract_value"])
    else:
        min_value = 0.0

    if row.get("max_contract_value"):
        max_value = float(row["max_contract_value"])
    elif row.get("contract_value"):
        max_value = _parse_pkr_value(row["contract_value"])
    else:
        max_value = min_value

    year_raw = row.get("project_year", "").strip()
    project_year = int(year_raw) if year_raw.isdigit() else 0

    evidence_parts = [description] if description else []
    duration = row.get("duration_months", "").strip()
    contract_display = row.get("contract_value", "").strip()
    if duration:
        evidence_parts.append(f"Duration: {duration} months")
    if contract_display:
        evidence_parts.append(f"Contract value: {contract_display}")

    return CapabilityRecord(
        capability_id=capability_id,
        title=title,
        description=description,
        domain=domain,
        certifications=certifications,
        client_types=client_types,
        min_contract_value=min_value,
        max_contract_value=max_value,
        project_year=project_year,
        bid_outcome=row.get("bid_outcome", "").strip(),
        evidence_text=row.get("evidence_text", "").strip() or " | ".join(evidence_parts),
        proof_document=row.get("proof_document", "").strip(),
    )


def load_capability_library(csv_path: Path | None = None) -> list[CapabilityRecord]:
    path = csv_path or settings.capability_csv_path
    if not path.exists():
        raise FileNotFoundError(f"Capability library not found: {path}")

    raw_text = path.read_text(encoding="utf-8-sig")
    lines = raw_text.splitlines()
    header_index = _find_header_line_index(lines)

    records: list[CapabilityRecord] = []
    reader = csv.DictReader(io.StringIO("\n".join(lines[header_index:])))
    for row in reader:
        normalized = _normalize_row(row)
        record = _row_to_record(normalized)
        if record:
            records.append(record)

    if not records:
        raise ValueError(f"No capability records parsed from {path}")

    return records


def capability_to_document_text(record: CapabilityRecord) -> str:
    return "\n".join(
        [
            f"Title: {record.title}",
            f"Domain: {record.domain}",
            f"Description: {record.description}",
            f"Certifications: {', '.join(record.certifications)}",
            f"Client types: {', '.join(record.client_types)}",
            f"Evidence: {record.evidence_text}",
        ]
    )
