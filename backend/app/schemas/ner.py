from pydantic import BaseModel, Field

from app.schemas.documents import DocumentIngestionResponse


class NerEntityBase(BaseModel):
    text: str = Field(description="Normalized entity value")
    source_quote: str = Field(description="Verbatim excerpt from the source document")
    page: int | None = Field(default=None, description="Source page when known")
    section: str | None = Field(default=None, description="Source section/heading when known")


class MandatoryRequirement(NerEntityBase):
    category: str | None = Field(default=None, description="e.g. technical, legal, administrative")


class EvaluationCriterion(NerEntityBase):
    criterion_name: str | None = None


class SubmissionDeadline(NerEntityBase):
    deadline_type: str | None = Field(
        default=None,
        description="e.g. proposal_submission, questions, pre_bid_meeting",
    )
    date_text: str = Field(description="Deadline as stated in the document")
    parsed_date: str | None = Field(default=None, description="ISO-8601 date if inferable")


class QuestionAnswerSection(BaseModel):
    question: str
    answer: str | None = None
    source_quote: str
    page: int | None = None
    section: str | None = None


class BudgetFigure(NerEntityBase):
    amount: str | None = Field(default=None, description="Numeric amount as stated")
    currency: str | None = None
    context: str | None = Field(default=None, description="What the budget figure refers to")


class EvaluationWeight(NerEntityBase):
    criterion: str | None = None
    weight_percent: float | None = Field(default=None, description="Weight as a percentage")


class ComplianceClause(NerEntityBase):
    clause_type: str | None = Field(default=None, description="e.g. certification, insurance, legal")
    standard: str | None = Field(default=None, description="Referenced standard or regulation")


class NerEntities(BaseModel):
    mandatory_requirements: list[MandatoryRequirement] = Field(default_factory=list)
    evaluation_criteria: list[EvaluationCriterion] = Field(default_factory=list)
    submission_deadlines: list[SubmissionDeadline] = Field(default_factory=list)
    question_answer_sections: list[QuestionAnswerSection] = Field(default_factory=list)
    budget_figures: list[BudgetFigure] = Field(default_factory=list)
    evaluation_weights: list[EvaluationWeight] = Field(default_factory=list)
    compliance_clauses: list[ComplianceClause] = Field(default_factory=list)


class NerExtractionMetadata(BaseModel):
    model: str
    input_char_count: int
    truncated: bool = False
    entity_counts: dict[str, int]


class NerExtractionResponse(BaseModel):
    task: str = "ner"
    metadata: NerExtractionMetadata
    entities: NerEntities


class NerTextRequest(BaseModel):
    text: str = Field(min_length=1, description="Raw or ingested document text for NER")


class NerDocumentExtractionResponse(BaseModel):
    ingestion: DocumentIngestionResponse
    ner: NerExtractionResponse
