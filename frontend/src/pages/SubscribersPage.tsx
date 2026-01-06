import React, { useEffect, useState } from "react";
import ChartCard, { ChartDataPoint } from "../components/ChartCard";
import PeriodSelector, { Period } from "../components/PeriodSelector";
import { BasePageProperties } from "@/utils/BasePageProperties";

export default function SubscribersPage(props: BasePageProperties) {
  const [period, setPeriod] = useState<Period>("default");
  const [data, setData] = useState<ChartDataPoint[]>([]);

  const client = props.metricsClient;

  useEffect(() => {
    client
      .getSubscribersCountHistory(period)
      .then((data) => setData(data));
  }, [period]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Subscribers</h1>
      <PeriodSelector value={period} onChange={setPeriod} />
      <ChartCard title={`Subscribers (${period})`} data={data} />
    </div>
  );
}
