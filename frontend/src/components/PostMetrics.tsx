import React from "react";
import { Eye, Heart, MessageCircle } from "lucide-react";
import MetricDisplay from "./MetricDisplay";

interface Metric {
  value?: number | null;
  diff?: number;
}

interface PostMetricsProps {
  views: Metric;
  reactions: Metric;
  comments: Metric;
  signed?: boolean;
}

// The single-line "views / reactions / comments" stats used on post cards and
// the Reactions page summary. A metric with no value isn't shown.
export default function PostMetrics({ views, reactions, comments, signed }: PostMetricsProps) {
  const items = [
    { icon: Eye, label: "Views", metric: views },
    { icon: Heart, label: "Reactions", metric: reactions },
    { icon: MessageCircle, label: "Comments", metric: comments },
  ];
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
      {items.map(({ icon, label, metric }) =>
        metric.value != null && (
          <MetricDisplay key={label} icon={icon} label={label} value={metric.value} valueDiff={metric.diff ?? 0} signed={signed} />
        )
      )}
    </div>
  );
}
