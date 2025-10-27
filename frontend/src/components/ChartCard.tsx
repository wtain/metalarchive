import React from "react";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export interface ChartDataPoint {
  timestamp: string;
  count: number;
}

interface ChartCardProps {
  title: string;
  data: ChartDataPoint[];
}

export default function ChartCard({ title, data }: ChartCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow p-4 mb-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
