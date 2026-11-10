from app.db.chroma import chroma_client
from app.schemas.capability import CapabilityRecord
from app.schemas.ner import MandatoryRequirement
from app.schemas.rag import CapabilityMatch, RagIndexResponse, RagMatchResponse, RequirementMatch
from app.services.capability_loader import capability_to_document_text, load_capability_library

COLLECTION_NAME = "capability_library"


def _distance_to_similarity(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - distance))


def _record_from_metadata(metadata: dict) -> CapabilityRecord:
    return CapabilityRecord(
        capability_id=metadata["capability_id"],
        title=metadata["title"],
        description=metadata["description"],
        domain=metadata["domain"],
        certifications=metadata.get("certifications", "").split("|") if metadata.get("certifications") else [],
        client_types=metadata.get("client_types", "").split("|") if metadata.get("client_types") else [],
        min_contract_value=float(metadata.get("min_contract_value", 0)),
        max_contract_value=float(metadata.get("max_contract_value", 0)),
        project_year=int(metadata.get("project_year", 0)),
        bid_outcome=metadata.get("bid_outcome", ""),
        evidence_text=metadata.get("evidence_text", ""),
        proof_document=metadata.get("proof_document", ""),
    )


def _metadata_from_record(record: CapabilityRecord) -> dict:
    return {
        "capability_id": record.capability_id,
        "title": record.title,
        "description": record.description,
        "domain": record.domain,
        "certifications": "|".join(record.certifications),
        "client_types": "|".join(record.client_types),
        "min_contract_value": record.min_contract_value,
        "max_contract_value": record.max_contract_value,
        "project_year": record.project_year,
        "bid_outcome": record.bid_outcome,
        "evidence_text": record.evidence_text,
        "proof_document": record.proof_document,
    }


def index_capability_library(force: bool = False) -> RagIndexResponse:
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    if collection.count() > 0 and not force:
        return RagIndexResponse(
            indexed_count=collection.count(),
            collection=COLLECTION_NAME,
            message="Capability library already indexed.",
        )

    if force and collection.count() > 0:
        chroma_client.client.delete_collection(COLLECTION_NAME)
        collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    records = load_capability_library()
    collection.add(
        ids=[record.capability_id for record in records],
        documents=[capability_to_document_text(record) for record in records],
        metadatas=[_metadata_from_record(record) for record in records],
    )

    return RagIndexResponse(
        indexed_count=len(records),
        collection=COLLECTION_NAME,
        message=f"Indexed {len(records)} capability records.",
    )


def ensure_indexed() -> None:
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    if collection.count() == 0:
        index_capability_library()


def match_requirements(
    requirements: list[MandatoryRequirement],
    top_k: int = 3,
) -> RagMatchResponse:
    ensure_indexed()
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    requirement_matches: list[RequirementMatch] = []
    matched_count = 0

    for index, requirement in enumerate(requirements):
        query_text = f"{requirement.text}\n{requirement.source_quote}"
        results = collection.query(query_texts=[query_text], n_results=top_k)

        matches: list[CapabilityMatch] = []
        if results["ids"] and results["ids"][0]:
            for idx, capability_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][idx]
                distance = results["distances"][0][idx] if results.get("distances") else 1.0
                similarity = _distance_to_similarity(distance)
                record = _record_from_metadata(metadata)
                matches.append(
                    CapabilityMatch(
                        capability_id=capability_id,
                        title=record.title,
                        domain=record.domain,
                        evidence_text=record.evidence_text,
                        proof_document=record.proof_document,
                        similarity_score=round(similarity, 4),
                        capability=record,
                    )
                )

        if matches:
            matched_count += 1

        requirement_matches.append(
            RequirementMatch(
                requirement_index=index,
                requirement_text=requirement.text,
                source_quote=requirement.source_quote,
                page=requirement.page,
                section=requirement.section,
                matches=matches,
            )
        )

    return RagMatchResponse(
        requirement_matches=requirement_matches,
        total_requirements=len(requirements),
        matched_requirements=matched_count,
    )
