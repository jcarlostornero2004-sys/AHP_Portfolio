interface BadgeProps {
  children: React.ReactNode;
  color?: "green" | "red" | "blue" | "gold" | "gray";
  className?: string;
}

const colorMap = {
  green: "bg-accent-green/20 text-accent-green",
  red: "bg-accent-red/20 text-accent-red",
  blue: "bg-accent-blue/20 text-accent-blue",
  gold: "bg-accent-gold/20 text-accent-gold",
  gray: "bg-bg-tertiary text-text-secondary",
};

export function Badge({ children, color = "gray", className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorMap[color]} ${className}`}
    >
      {children}
    </span>
  );
}
