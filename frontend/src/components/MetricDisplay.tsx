import React from "react";

interface MetricDisplayProps {
  value: number;
  valueDiff: number;
}

export default function MetricDisplay({ value, valueDiff }: MetricDisplayProps) {
    return (
        <div className="text-xl text-green-600">{value}
        {
            (valueDiff > 0) ? ` (+${valueDiff})` : ""
        }
        </div>
    )
}