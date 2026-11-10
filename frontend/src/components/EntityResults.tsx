import { useState } from "react";

import type { NerEntities } from "../api/client";

const ENTITY_LABELS: Record<keyof NerEntities, string> = {
  mandatory_requirements: "Mandatory Requirements",
  evaluation_criteria: "Evaluation Criteria",
  submission_deadlines: "Submission Deadlines",
  question_answer_sections: "Q&A Sections",
  budget_figures: "Budget Figures",
  evaluation_weights: "Evaluation Weights",
  compliance_clauses: "Compliance Clauses",
};

interface EntityResultsProps {
  entities: NerEntities;
  counts: Record<string, number>;
}

export default function EntityResults({ entities, counts }: EntityResultsProps) {
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});

  const toggle = (key: string) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="space-y-3">
      {(Object.keys(ENTITY_LABELS) as Array<keyof NerEntities>).map((key) => {
        const items = entities[key];
        const count = counts[key] ?? items.length;
        const isOpen = openSections[key] ?? count > 0;

        return (
          <div key={key} className="rounded-lg border border-slate-200 bg-white">
            <button
              type="button"
              onClick={() => toggle(key)}
              className="flex w-full items-center justify-between px-4 py-3 text-left"
            >
              <span className="font-medium text-slate-900">{ENTITY_LABELS[key]}</span>
              <span className="rounded-full bg-brand-100 px-2.5 py-0.5 text-sm font-semibold text-brand-700">
                {count}
              </span>
            </button>

            {isOpen && items.length > 0 && (
              <ul className="space-y-3 border-t border-slate-100 px-4 py-3">
                {items.map((item, index) => (
                  <li key={index} className="rounded-md bg-slate-50 p-3 text-sm">
                    <p className="font-medium text-slate-900">
                      {item.question ?? item.text ?? item.source_quote}
                    </p>
                    {item.answer && (
                      <p className="mt-1 text-slate-600">
                        <span className="font-medium">Answer:</span> {item.answer}
                      </p>
                    )}
                    {item.date_text && (
                      <p className="mt-1 text-slate-600">
                        <span className="font-medium">Date:</span> {item.date_text}
                      </p>
                    )}
                    {item.amount && (
                      <p className="mt-1 text-slate-600">
                        <span className="font-medium">Amount:</span> {item.amount}
                        {item.currency ? ` ${item.currency}` : ""}
                      </p>
                    )}
                    {item.weight_percent != null && (
                      <p className="mt-1 text-slate-600">
                        <span className="font-medium">Weight:</span> {item.weight_percent}%
                      </p>
                    )}
                    <p className="mt-2 text-xs text-slate-500">
                      {item.page != null && <span>Page {item.page} · </span>}
                      {item.section && <span>{item.section} · </span>}
                      <span className="italic">"{item.source_quote.slice(0, 120)}
                        {item.source_quote.length > 120 ? "…" : ""}"</span>
                    </p>
                  </li>
                ))}
              </ul>
            )}

            {isOpen && items.length === 0 && (
              <p className="border-t border-slate-100 px-4 py-3 text-sm text-slate-500">
                No entities found.
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
