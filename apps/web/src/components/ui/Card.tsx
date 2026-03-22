interface CardProps {
  children: React.ReactNode;
  className?: string;
  glass?: boolean;
}

export function Card({ children, className = "", glass = false }: CardProps) {
  const base = glass
    ? "glass rounded-xl p-6"
    : "bg-bg-secondary border border-border rounded-xl p-6";
  return <div className={`${base} ${className}`}>{children}</div>;
}
