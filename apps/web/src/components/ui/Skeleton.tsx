interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse bg-bg-tertiary rounded ${className}`}
    />
  );
}

export function StatCardSkeleton() {
  return (
    <div className="bg-bg-secondary border border-border rounded-xl p-6">
      <Skeleton className="h-4 w-24 mb-2" />
      <Skeleton className="h-9 w-32 mb-1" />
      <Skeleton className="h-3 w-20" />
    </div>
  );
}
