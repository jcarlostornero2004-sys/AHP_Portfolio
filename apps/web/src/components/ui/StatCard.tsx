import { Card } from "./Card";

interface StatCardProps {
  label: string;
  value: string;
  subtitle?: string;
  color?: "green" | "red" | "blue" | "gold" | "default";
  className?: string;
}

const colorMap = {
  green: "text-accent-green",
  red: "text-accent-red",
  blue: "text-accent-blue",
  gold: "text-accent-gold",
  default: "text-text-primary",
};

export function StatCard({
  label,
  value,
  subtitle,
  color = "default",
  className = "",
}: StatCardProps) {
  return (
    <Card className={`flex flex-col gap-1 ${className}`}>
      <span className="text-sm font-medium text-text-secondary uppercase tracking-wider">
        {label}
      </span>
      <span className={`text-3xl font-bold ${colorMap[color]}`}>{value}</span>
      {subtitle && (
        <span className="text-xs text-text-secondary">{subtitle}</span>
      )}
    </Card>
  );
}
