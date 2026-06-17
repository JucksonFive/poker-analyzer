import { cn } from "@/shared/utils/cn";

interface StatCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  trend?: "up" | "down" | "neutral";
  format?: "currency" | "percent" | "number" | "text";
  className?: string;
}

/**
 * A stat card used across the dashboard and player analysis pages.
 *
 * Props:
 * - label: Stat name (e.g., "VPIP", "Net Won")
 * - value: Primary stat value
 * - subValue: Secondary info (e.g., "250 hands")
 * - trend: Direction arrow color
 * - format: How to render the value
 */
export function StatCard({
  label,
  value,
  subValue,
  trend,
  format = "number",
  className,
}: StatCardProps) {
  const trendColor =
    trend === "up"
      ? "text-stat-positive"
      : trend === "down"
        ? "text-stat-negative"
        : "text-stat-neutral";

  const formatValue = (v: string | number): string => {
    const num = typeof v === "string" ? parseFloat(v) : v;
    if (isNaN(num)) return String(v);

    switch (format) {
      case "currency":
        return num < 0 ? `-$${Math.abs(num).toFixed(2)}` : `$${num.toFixed(2)}`;
      case "percent":
        return `${num.toFixed(1)}%`;
      case "number":
        return num.toLocaleString();
      default:
        return String(v);
    }
  };

  return (
    <div
      className={cn(
        "bg-slate-800 rounded-lg p-4 border border-slate-700",
        className,
      )}
    >
      <div className="text-xs text-slate-400 uppercase tracking-wide mb-1">
        {label}
      </div>
      <div className={cn("text-2xl font-semibold", trendColor)}>
        {formatValue(value)}
      </div>
      {subValue && (
        <div className="text-xs text-slate-500 mt-1">{subValue}</div>
      )}
    </div>
  );
}
