import React, { useEffect, useState } from "react";
import axios from "axios";
import ChartCard, { ChartDataPoint } from "../components/ChartCard";
import PeriodSelector, { Period } from "../components/PeriodSelector";

export default function SubscribersPage() {
  const [period, setPeriod] = useState<Period>("default");
  const [data, setData] = useState<ChartDataPoint[]>([]);

  useEffect(() => {
    axios
      .get<{ data: ChartDataPoint[] }>(`http://127.0.0.1:8001/api/subscribers/count-over-time?period=${period}`, {
          mode: 'no-cors',
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
          },
      })
      .then((res) => setData(res.data.data))
      .catch(console.error);
  }, [period]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Subscribers</h1>
      <PeriodSelector value={period} onChange={setPeriod} />
      <ChartCard title={`Subscribers (${period})`} data={data} />
    </div>
  );
}
