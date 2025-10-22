import React, { useEffect, useState } from "react";
import axios from "axios";
import ChartCard, { ChartDataPoint } from "../components/ChartCard";
import PeriodSelector, { Period } from "../components/PeriodSelector";

export default function ReactionsPage() {
  const [period, setPeriod] = useState<Period>("daily");
  const [data, setData] = useState<ChartDataPoint[]>([]);

  useEffect(() => {
    axios
      .get<{ data: ChartDataPoint[] }>(`/api/reactions/changes?period=${period}`)
      .then((res) => setData(res.data.data))
      .catch(console.error);
  }, [period]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Reactions</h1>
      <PeriodSelector value={period} onChange={setPeriod} />
      <ChartCard title={`Reactions (${period})`} data={data} />
    </div>
  );
}
