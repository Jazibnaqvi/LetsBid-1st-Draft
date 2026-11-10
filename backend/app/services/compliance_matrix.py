from app.schemas.compliance import ComplianceMatrixResponse, ComplianceRow, ComplianceStatus
from app.schemas.rag import RequirementMatch


def build_compliance_matrix(
    requirement_matches: list[RequirementMatch],
    pass_threshold: float = 0.65,
    partial_threshold: float = 0.45,
) -> ComplianceMatrixResponse:
    rows: list[ComplianceRow] = []
    summary = {"Pass": 0, "Fail": 0, "Partial": 0}

    for row_id, item in enumerate(requirement_matches):
        best_match = item.matches[0] if item.matches else None
        similarity = best_match.similarity_score if best_match else 0.0
        has_proof = bool(best_match and best_match.proof_document)
        has_capability = best_match is not None and similarity >= partial_threshold

        if similarity >= pass_threshold and has_proof:
            status = ComplianceStatus.PASS
            notes = "Requirement supported by capability evidence."
        elif has_capability and (similarity >= partial_threshold or has_proof):
            status = ComplianceStatus.PARTIAL
            notes = "Partial match — capability found but evidence may be incomplete."
        else:
            status = ComplianceStatus.FAIL
            notes = "No adequate capability match or proof found."

        missing_capability = not has_capability
        missing_proof = has_capability and not has_proof

        if missing_capability:
            notes += " Missing capability."
        if missing_proof:
            notes += " Missing proof document."

        rows.append(
            ComplianceRow(
                row_id=row_id,
                requirement_text=item.requirement_text,
                source_quote=item.source_quote,
                page=item.page,
                section=item.section,
                status=status,
                matched_capability_id=best_match.capability_id if best_match else None,
                matched_capability_title=best_match.title if best_match else None,
                evidence_text=best_match.evidence_text if best_match else None,
                proof_document=best_match.proof_document if best_match else None,
                similarity_score=similarity if best_match else None,
                missing_capability=missing_capability,
                missing_proof=missing_proof,
                notes=notes.strip(),
            )
        )
        summary[status.value] += 1

    return ComplianceMatrixResponse(rows=rows, summary=summary)
