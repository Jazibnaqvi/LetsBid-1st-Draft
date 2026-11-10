import re
from datetime import datetime

from app.schemas.go_nogo import GoNoGoRecommendation, GoNoGoRequest, GoNoGoResponse, ScoreFactor
from app.schemas.ner import NerEntities
from app.schemas.rag import RequirementMatch
from app.services.capability_loader import load_capability_library

CURRENT_YEAR = datetime.now().year

FACTOR_WEIGHTS = {
    "domain_match": 0.25,
    "certification_match": 0.20,
    "client_type_match": 0.15,
    "contract_value_fit": 0.15,
    "recency_of_similar_projects": 0.15,
    "historical_bid_outcome": 0.10,
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_domains(entities: NerEntities, bid_domain: str | None) -> set[str]:
    domains = {_normalize(bid_domain)} if bid_domain else set()
    for req in entities.mandatory_requirements:
        domains.add(_normalize(req.text))
        if req.category:
            domains.add(_normalize(req.category))
    for clause in entities.compliance_clauses:
        domains.add(_normalize(clause.text))
    domains.discard("")
    return domains


def _extract_certifications(entities: NerEntities) -> set[str]:
    certs: set[str] = set()
    for clause in entities.compliance_clauses:
        text = _normalize(clause.text)
        if clause.standard:
            certs.add(_normalize(clause.standard))
        for token in ("iso 27001", "iso 9001", "iso 14001", "soc 2", "cmmi", "pci"):
            if token in text:
                certs.add(token)
    return certs


def _extract_client_types(entities: NerEntities, bid_client_type: str | None) -> set[str]:
    types = {_normalize(bid_client_type)} if bid_client_type else set()
    keywords = ("government", "financial", "healthcare", "retail", "ngo", "telecom", "education")
    corpus = " ".join(
        entity.source_quote
        for entity in (
            entities.mandatory_requirements
            + entities.compliance_clauses
            + entities.evaluation_criteria
        )
    ).lower()
    for keyword in keywords:
        if keyword in corpus:
            types.add(keyword)
    types.discard("")
    return types


def _extract_contract_value(entities: NerEntities, bid_contract_value: float | None) -> float | None:
    if bid_contract_value is not None:
        return bid_contract_value
    for figure in entities.budget_figures:
        if figure.amount:
            digits = re.sub(r"[^\d.]", "", figure.amount.replace(",", ""))
            if digits:
                try:
                    return float(digits)
                except ValueError:
                    continue
    return None


def _score_domain_match(domains: set[str], matches: list[RequirementMatch]) -> tuple[float, str]:
    if not domains:
        return 0.5, "No explicit domain detected; using neutral score."

    capabilities = load_capability_library()
    hits = 0
    for domain_hint in domains:
        for cap in capabilities:
            if domain_hint in _normalize(cap.domain) or domain_hint in _normalize(cap.description):
                hits += 1
                break

    if matches:
        avg_similarity = sum(m.matches[0].similarity_score for m in matches if m.matches) / max(
            len([m for m in matches if m.matches]), 1
        )
        score = min(1.0, (hits / max(len(domains), 1)) * 0.5 + avg_similarity * 0.5)
    else:
        score = hits / max(len(domains), 1)

    return round(score, 4), f"Matched {hits} domain hints against capability library."


def _score_certification_match(certs: set[str]) -> tuple[float, str]:
    if not certs:
        return 0.5, "No certifications extracted; neutral score applied."

    capabilities = load_capability_library()
    all_caps = {_normalize(cert) for cap in capabilities for cert in cap.certifications}
    hits = sum(1 for cert in certs if any(cert in cap_cert or cap_cert in cert for cap_cert in all_caps))
    score = hits / max(len(certs), 1)
    return round(score, 4), f"Matched {hits}/{len(certs)} required certifications."


def _score_client_type_match(client_types: set[str]) -> tuple[float, str]:
    if not client_types:
        return 0.5, "No client type detected; neutral score applied."

    capabilities = load_capability_library()
    hits = 0
    for client_type in client_types:
        for cap in capabilities:
            if any(client_type in _normalize(ct) for ct in cap.client_types):
                hits += 1
                break
    score = hits / max(len(client_types), 1)
    return round(score, 4), f"Matched {hits}/{len(client_types)} client type indicators."


def _score_contract_value_fit(contract_value: float | None) -> tuple[float, str]:
    if contract_value is None:
        return 0.5, "No contract value found; neutral score applied."

    capabilities = load_capability_library()
    fits = [
        cap
        for cap in capabilities
        if cap.min_contract_value <= contract_value <= cap.max_contract_value
    ]
    score = min(1.0, len(fits) / 3)
    return round(score, 4), f"{len(fits)} capabilities fit contract value range."


def _score_recency(matches: list[RequirementMatch]) -> tuple[float, str]:
    years: list[int] = []
    for match in matches:
        for item in match.matches[:2]:
            year = item.capability.project_year
            if year:
                years.append(year)

    if not years:
        capabilities = load_capability_library()
        years = [cap.project_year for cap in capabilities if cap.project_year]

    if not years:
        return 0.3, "No project recency data available."

    avg_year = sum(years) / len(years)
    age = max(0, CURRENT_YEAR - avg_year)
    score = max(0.0, min(1.0, 1.0 - age / 5))
    return round(score, 4), f"Average project year {avg_year:.0f} ({age:.0f} years ago)."


def _score_historical_outcome(matches: list[RequirementMatch]) -> tuple[float, str]:
    outcomes: list[str] = []
    for match in matches:
        for item in match.matches[:2]:
            if item.capability.bid_outcome:
                outcomes.append(item.capability.bid_outcome.lower())

    if not outcomes:
        capabilities = load_capability_library()
        outcomes = [cap.bid_outcome.lower() for cap in capabilities if cap.bid_outcome]

    if not outcomes:
        return 0.5, "No historical bid outcomes available."

    wins = sum(1 for outcome in outcomes if outcome == "won")
    losses = sum(1 for outcome in outcomes if outcome == "lost")
    score = (wins + 0.25 * sum(1 for o in outcomes if o == "no_bid")) / len(outcomes)
    if losses > wins:
        score *= 0.8
    return round(score, 4), f"Historical outcomes: {wins} won, {losses} lost from {len(outcomes)} samples."


def _recommendation(score: float) -> GoNoGoRecommendation:
    if score >= 70:
        return GoNoGoRecommendation.GO
    if score >= 50:
        return GoNoGoRecommendation.CONDITIONAL
    return GoNoGoRecommendation.NO_GO


def calculate_go_nogo(request: GoNoGoRequest) -> GoNoGoResponse:
    domains = _extract_domains(request.entities, request.bid_domain)
    certs = _extract_certifications(request.entities)
    client_types = _extract_client_types(request.entities, request.bid_client_type)
    contract_value = _extract_contract_value(request.entities, request.bid_contract_value)

    calculators = {
        "domain_match": lambda: _score_domain_match(domains, request.requirement_matches),
        "certification_match": lambda: _score_certification_match(certs),
        "client_type_match": lambda: _score_client_type_match(client_types),
        "contract_value_fit": lambda: _score_contract_value_fit(contract_value),
        "recency_of_similar_projects": lambda: _score_recency(request.requirement_matches),
        "historical_bid_outcome": lambda: _score_historical_outcome(request.requirement_matches),
    }

    factors: list[ScoreFactor] = []
    total_score = 0.0

    for name, weight in FACTOR_WEIGHTS.items():
        score, rationale = calculators[name]()
        weighted = score * weight * 100
        total_score += weighted
        factors.append(
            ScoreFactor(
                name=name.replace("_", " ").title(),
                weight=weight,
                score=score,
                weighted_score=round(weighted, 2),
                rationale=rationale,
            )
        )

    final_score = round(total_score, 2)
    win_probability = round(min(0.95, max(0.05, final_score / 100)), 4)
    recommendation = _recommendation(final_score)

    summary = (
        f"Overall score {final_score}/100 with {win_probability:.0%} estimated win probability. "
        f"Recommendation: {recommendation.value}."
    )

    return GoNoGoResponse(
        score=final_score,
        win_probability=win_probability,
        recommendation=recommendation,
        factors=factors,
        summary=summary,
    )
