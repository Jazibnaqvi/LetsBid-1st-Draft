interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  accent?: "default" | "success" | "warning" | "danger";
}

const ACCENTS = {
  default: "border-slate-200 bg-white text-slate-900",
  success: "border-green-200 bg-green-50 text-green-900",
  warning: "border-amber-200 bg-amber-50 text-amber-900",
  danger: "border-red-200 bg-red-50 text-red-900",
};

export default function StatCard({ label, value, subtext, accent = "default" }: StatCardProps) {
  return (
    <div className={`rounded-lg border p-5 shadow-sm ${ACCENTS[accent]}`}>
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
      {subtext && <p className="mt-1 text-xs text-slate-500">{subtext}</p>}
    </div>
  );
}
