interface ProgressProps {
  value: number;
  max?: number;
  color?: string;
  className?: string;
}

export function Progress({
  value,
  max = 100,
  color = "bg-accent-blue",
  className = "",
}: ProgressProps) {
  const pct = Math.min((value / max) * 100, 100);

  return (
    <div className={`w-full h-2 bg-bg-tertiary rounded-full overflow-hidden ${className}`}>
      <div
        className={`h-full rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
