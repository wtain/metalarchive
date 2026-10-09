import React from "react";
import Chart from "react-apexcharts";
import { ApexOptions } from "apexcharts";

export interface ChartDataPoint {
  timestamp: string;
  count: number;
}

interface ChartCardProps {
  title: string;
  data: ChartDataPoint[];
}

export default function ChartCard({ title, data }: ChartCardProps) {
  const series = [
    {
      name: "Count",
      data: data.map((d) => d.count),
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
      categories: data.map((d) => d.timestamp),
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
      {data.length === 0
        ? <p className="text-gray-500">No data yet.</p>
        : <Chart options={options} series={series} type="line" height={300} />
      }
    </div>
  );
}
