export default function PredictionBadge({ value }: { value: string }) {
  const styles: Record<string, string> = {
    HIGH: "bg-green-500/15 text-green-400 border-green-500/30",
    MEDIUM: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    LOW: "bg-red-500/15 text-red-400 border-red-500/30",
  };
  return (
    <span
      className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
        styles[value] || "bg-neutral-800 text-neutral-400 border-neutral-700"
      }`}
    >
      {value}
    </span>
  );
}
