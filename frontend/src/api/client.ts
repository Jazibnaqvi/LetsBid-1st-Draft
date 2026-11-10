const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

async function parseError(response: Response): Promise<string> {
  const errorBody = await response.json().catch(() => null);
  return typeof errorBody?.detail === "string"
    ? errorBody.detail
    : `API error: ${response.status}`;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json() as Promise<T>;
}

export interface NerEntity {
  text?: string;
  source_quote: string;
  page?: number | null;
  section?: string | null;
  question?: string;
  answer?: string | null;
  date_text?: string;
  amount?: string | null;
  weight_percent?: number | null;
  criterion?: string | null;
  category?: string | null;
}

export interface NerEntities {
  mandatory_requirements: NerEntity[];
  evaluation_criteria: NerEntity[];
  submission_deadlines: NerEntity[];
  question_answer_sections: NerEntity[];
  budget_figures: NerEntity[];
  evaluation_weights: NerEntity[];
  compliance_clauses: NerEntity[];
}

export interface ComplianceRow {
  row_id: number;
  requirement_text: string;
  source_quote: string;
  status: "Pass" | "Fail" | "Partial";
  matched_capability_id: string | null;
  matched_capability_title: string | null;
  evidence_text: string | null;
  proof_document: string | null;
  similarity_score: number | null;
  missing_capability: boolean;
  missing_proof: boolean;
  notes: string;
}

export interface ProposalSection {
  section_id: string;
  title: string;
  draft_content: string;
  edited_content: string | null;
  evidence_refs: string[];
  status: "draft" | "approved";
}

export interface AnalyzeResult {
  ingestion: {
    metadata: {
      filename: string;
      file_type: string;
      page_count: number | null;
      segment_count: number;
      word_count: number;
    };
    full_text: string;
  };
  ner: {
    metadata: {
      model: string;
      entity_counts: Record<string, number>;
      truncated: boolean;
    };
    entities: NerEntities;
  };
  rag: {
    requirement_matches: Array<{
      requirement_index: number;
      requirement_text: string;
      source_quote: string;
      matches: Array<{
        capability_id: string;
        title: string;
        evidence_text: string;
        proof_document: string;
        similarity_score: number;
      }>;
    }>;
    total_requirements: number;
    matched_requirements: number;
  };
  compliance: {
    rows: ComplianceRow[];
    summary: Record<string, number>;
  };
  go_nogo: {
    score: number;
    win_probability: number;
    recommendation: "GO" | "NO-GO" | "CONDITIONAL";
    factors: Array<{
      name: string;
      weight: number;
      score: number;
      weighted_score: number;
      rationale: string;
    }>;
    summary: string;
  };
  proposal: {
    proposal_id: string;
    document_name: string;
    sections: ProposalSection[];
    created_at: string;
  };
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  analyzeDocument: async (file: File): Promise<AnalyzeResult> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/analyze/document`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(await parseError(response));
    }

    return response.json() as Promise<AnalyzeResult>;
  },

  updateProposalSection: (proposalId: string, sectionId: string, editedContent: string) =>
    request<ProposalSection>(`/proposals/${proposalId}/sections/${sectionId}`, {
      method: "PUT",
      body: JSON.stringify({ edited_content: editedContent }),
    }),

  approveProposalSection: (proposalId: string, sectionId: string) =>
    request<ProposalSection>(`/proposals/${proposalId}/sections/${sectionId}/approve`, {
      method: "POST",
    }),

  exportProposal: (proposalId: string) =>
    request<{ content: string; document_name: string }>(`/proposals/${proposalId}/export`),
};
