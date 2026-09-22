import React from "react";
import Chart from "react-apexcharts";
import { ApexOptions } from "apexcharts";
import { SubscriberLifecycleEntry } from "../dto/BackendDataTypes";
import { displayName } from "../pages/SubscriberLifecyclePage";

interface SubscriberLifecycleDiagramProps {
  entries: SubscriberLifecycleEntry[];
}

const PAST_COLOR = "#94a3b8";
const CURRENT_COLOR = "#22c55e";
const ROW_HEIGHT_PX = 24;
const MIN_HEIGHT_PX = 200;

// A Telegram username is unique, so it's a safe label on its own. Without one
// (e.g. generic "Private Contact" placeholder names), two different users can
// share the exact same display name - rangeBarGroupRows below groups bars by
// matching label, so an ambiguous label would visually merge unrelated
// people's timelines into one row. The user_id suffix guards against that.
function rowLabel(entry: SubscriberLifecycleEntry): string {
  return entry.username
    ? `${displayName(entry)} (@${entry.username})`
    : `${displayName(entry)} #${entry.user_id}`;
}

export default function SubscriberLifecycleDiagram({ entries }: SubscriberLifecycleDiagramProps) {
  const now = Date.now();

  const sorted = [...entries].sort(
    (a, b) => new Date(a.added).getTime() - new Date(b.added).getTime()
  );

  const series = [
    {
      data: sorted.map((entry) => ({
        x: rowLabel(entry),
        y: [
          new Date(entry.added).getTime(),
          entry.removed ? new Date(entry.removed).getTime() : now,
        ],
        fillColor: entry.removed ? PAST_COLOR : CURRENT_COLOR,
      })),
    },
  ];

  const options: ApexOptions = {
    chart: {
      type: "rangeBar",
      toolbar: { show: true },
      // Default ('auto') binds mouse wheel / trackpad scroll to zoom whenever
      // the toolbar's reset button is present (it is here), which hijacks
      // page scroll while hovering a chart this tall. Scrolling past it
      // matters more than wheel-zoom, so turn just that off - drag-select
      // zoom and the toolbar buttons still work.
      zoom: {
        allowMouseWheelZoom: false,
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: "70%",
        rangeBarGroupRows: true,
      },
    },
    xaxis: {
      type: "datetime",
    },
    tooltip: {
      x: { format: "dd MMM yyyy HH:mm" },
    },
  };

  if (entries.length === 0) {
    return <p className="text-gray-500">No subscriber data yet.</p>;
  }

  return (
    <Chart
      options={options}
      series={series}
      type="rangeBar"
      height={Math.max(MIN_HEIGHT_PX, sorted.length * ROW_HEIGHT_PX)}
    />
  );
}
