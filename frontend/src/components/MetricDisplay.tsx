import React from "react";
import type { LucideIcon } from "lucide-react";

interface MetricDisplayProps {
  icon: LucideIcon;
  label: string;
  value: number;
  valueDiff: number;
  // Render the value itself as a gain ("+12") - for numbers that already are a change.
  signed?: boolean;
}

// Compact "icon value +delta" - the label is only for hover/screen readers.
export default function MetricDisplay({ icon: Icon, label, value, valueDiff, signed }: MetricDisplayProps) {
    return (
        <span className="inline-flex items-center gap-1 text-sm text-gray-700" title={label}>
            <Icon className="h-4 w-4 text-gray-400" aria-label={label} />
            <span className="font-medium">{signed && value > 0 ? "+" : ""}{value.toLocaleString()}</span>
            {valueDiff > 0 && <span className="text-xs text-green-600">+{valueDiff.toLocaleString()}</span>}
        </span>
    )
}
