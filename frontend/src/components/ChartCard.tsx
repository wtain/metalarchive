import React from "react";
import Chart from "react-apexcharts";
import { ApexOptions } from "apexcharts";
import Spinner from "./Spinner";
import { formatAxisLabel, formatTooltipLabel, isShortRange } from "../utils/chartTimeLabels";

export interface ChartDataPoint {
  timestamp: string;
  count: number;
}

interface ChartCardProps {
  title: string;
  // null while the data is still loading
  data: ChartDataPoint[] | null;
  // Backend period of the series ("weekly" / "monthly" labels are ambiguous
  // without it - see utils/chartTimeLabels.ts).
  period?: string;
}

// The "default" subscriber-count period returns one raw point per batch run
// (every ~15 min since mid-2025 - 25k+ points), which hangs the chart trying
// to render that many SVG elements. Downsamples to at most MAX_POINTS by
// taking the last value in each bucket - representative for a count that can
// both rise and fall (unlike max, which would visually fabricate spikes),
// and for a monotonically-increasing series (post views) it's equivalent to
// max anyway. No-op for the already-small daily/weekly/monthly views.
const MAX_POINTS = 500;

function downsample(data: ChartDataPoint[], maxPoints: number): ChartDataPoint[] {
  if (data.length <= maxPoints) return data;

  const bucketSize = Math.ceil(data.length / maxPoints);
  const result: ChartDataPoint[] = [];
  for (let i = 0; i < data.length; i += bucketSize) {
    const bucket = data.slice(i, i + bucketSize);
    result.push(bucket[bucket.length - 1]);
  }
  return result;
}

export default function ChartCard({ title, data, period }: ChartCardProps) {
  const displayData = downsample(data ?? [], MAX_POINTS);
  const labels = displayData.map((d) => d.timestamp);
  const showTime = isShortRange(labels, period);

  const series = [
    {
      name: "Count",
      data: displayData.map((d) => d.count),
    },
  ];

  const options: ApexOptions = {
    chart: {
      type: "line",
      toolbar: { show: true },
      // Default ('auto') binds mouse wheel / trackpad scroll to zoom whenever
      // the toolbar's reset button is present (it is here), hijacking page
      // scroll while hovering the chart - same fix as the lifecycle diagram.
      // Drag-select zoom and the toolbar's reset button still work.
      zoom: {
        allowMouseWheelZoom: false,
      },
    },
    // category, not datetime: period-bucketed labels from the backend (e.g.
    // weekly's ISO-week "2026-41") aren't parseable calendar dates, so this
    // treats every timestamp as an opaque label - same as the previous
    // recharts rendering - rather than risk misparsing those.
    xaxis: {
      type: "category",
      categories: labels,
      labels: {
        // Apex also calls this with non-string values while parsing categories.
        formatter: (value: unknown) =>
          typeof value === "string" ? formatAxisLabel(value, { period, showTime }) : String(value ?? ""),
        rotate: 0,
        hideOverlappingLabels: true,
      },
      // ~8 labels is plenty for short "Nov 1" style text; Apex otherwise
      // tries to label every category and crams them.
      tickAmount: 8,
    },
    tooltip: {
      x: { formatter: (value: unknown, opts?: { dataPointIndex?: number }) => {
          const raw = labels[opts?.dataPointIndex ?? -1] ?? value
          return typeof raw === "string" ? formatTooltipLabel(raw, period) : String(raw ?? "")
        },
      },
    },
    stroke: {
      curve: "smooth",
      width: 2,
    },
    colors: ["#2563eb"],
    dataLabels: { enabled: false },
    markers: { size: 0 },
  };

  return (
    <div className="bg-white rounded-2xl shadow p-4 mb-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      {data === null
        ? <Spinner />
        : data.length === 0
          ? <p className="text-gray-500">No data yet.</p>
          : <Chart options={options} series={series} type="line" height={300} />
      }
    </div>
  );
}
