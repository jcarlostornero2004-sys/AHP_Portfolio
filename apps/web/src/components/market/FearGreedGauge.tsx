"use client";

interface FearGreedGaugeProps {
  value: number;
  label: string;
}

export function FearGreedGauge({ value, label }: FearGreedGaugeProps) {
  // Semicircle gauge: value 0-100 maps to -90deg to +90deg
  const rotation = -90 + (value / 100) * 180;

  const getColor = (v: number) => {
    if (v <= 20) return "#ef4444";
    if (v <= 40) return "#f97316";
    if (v <= 60) return "#f59e0b";
    if (v <= 80) return "#84cc16";
    return "#22c55e";
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-48 h-24 overflow-hidden">
        {/* Background arc */}
        <div className="absolute inset-0">
          <svg viewBox="0 0 200 100" className="w-full h-full">
            <defs>
              <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#ef4444" />
                <stop offset="25%" stopColor="#f97316" />
                <stop offset="50%" stopColor="#f59e0b" />
                <stop offset="75%" stopColor="#84cc16" />
                <stop offset="100%" stopColor="#22c55e" />
              </linearGradient>
            </defs>
            <path
              d="M 20 95 A 80 80 0 0 1 180 95"
              fill="none"
              stroke="url(#gaugeGrad)"
              strokeWidth="12"
              strokeLinecap="round"
            />
          </svg>
        </div>

        {/* Needle */}
        <div
          className="absolute bottom-0 left-1/2 w-0.5 h-16 bg-text-primary origin-bottom transition-transform duration-1000"
          style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
        >
          <div
            className="w-3 h-3 rounded-full -ml-[5px] -mt-1"
            style={{ backgroundColor: getColor(value) }}
          />
        </div>
      </div>

      <div className="text-center">
        <div className="text-4xl font-bold" style={{ color: getColor(value) }}>
          {value}
        </div>
        <div className="text-sm text-text-secondary">{label}</div>
      </div>
    </div>
  );
}
