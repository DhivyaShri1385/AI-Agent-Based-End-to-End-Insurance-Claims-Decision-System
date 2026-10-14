interface Props {
  label: string;
  tone: "success" | "warning" | "danger" | "neutral";
}

const tones: Record<Props["tone"], string> = {
  success: "bg-green-100 text-success",
  warning: "bg-amber-100 text-warning",
  danger: "bg-red-100 text-danger",
  neutral: "bg-slate-100 text-slate-600",
};

export default function StatusBadge({ label, tone }: Props) {
  return (
    <span className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${tones[tone]}`}>
      {label}
    </span>
  );
}
