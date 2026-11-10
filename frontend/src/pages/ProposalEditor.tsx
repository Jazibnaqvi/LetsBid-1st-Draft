import { useProject } from "../context/ProjectContext";
import ProposalDraft from "../components/ProposalDraft";
import PageHeader from "../components/ui/PageHeader";

export default function ProposalEditor() {
  const { activeProject, updateProposalSections } = useProject();
  const proposal = activeProject!.analysis!.proposal;

  return (
    <div>
      <PageHeader
        title="Proposal Editor"
        description="Review AI-generated section drafts, edit content, and approve each section."
      />

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <ProposalDraft
          proposalId={proposal.proposal_id}
          documentName={proposal.document_name}
          sections={proposal.sections}
          onUpdate={updateProposalSections}
        />
      </div>
    </div>
  );
}
