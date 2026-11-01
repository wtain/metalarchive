import React, { useEffect, useState } from "react";
import PeriodSelector, { Period } from "../components/PeriodSelector";
import { Subscriber, SubscriberChanges } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

import Spinner from "../components/Spinner";
import SubscriberLabel from "../components/SubscriberLabel";
import { SMMetricsClient } from "@/client/SMMetricsClient";

// Full refetch on an interval so a freshly scraped batch shows up without a
// manual reload - data only changes with the ~15min scrape.
const REFRESH_INTERVAL_MS = 60_000;

function SubscriberTable({ title, rows, client }: { title: string; rows: Subscriber[]; client: SMMetricsClient }) {
  return (
    <div className="mb-8">
      <h2 className="text-lg font-semibold mb-2">{title} ({rows.length})</h2>
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b">
            <th className="py-2 pr-4">Username</th>
            <th className="py-2 pr-4">Name</th>
            <th className="py-2 pr-4">Date/Time</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((s) => (
            <tr key={`${s.user_id}-${s.timestamp}`} className="border-b">
              <td className="py-2 pr-4">{s.username ? `@${s.username}` : "(none)"}</td>
              <td className="py-2 pr-4"><SubscriberLabel subscriber={s} client={client} /></td>
              <td className="py-2 pr-4">{new Date(s.timestamp).toLocaleString()}</td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td className="py-2 text-gray-500" colSpan={3}>None</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default function SubscriberChangesPage(props: BasePageProperties) {
  const [period, setPeriod] = useState<Period>("daily");
  const [data, setData] = useState<SubscriberChanges | null>(null);

  const client = props.metricsClient;

  useEffect(() => {
    // Back to the spinner on a period switch only - interval refetches update in place.
    setData(null);
    const fetchChanges = () => client.getSubscriberChanges(period).then((data) => setData(data));
    fetchChanges();

    const intervalId = setInterval(() => {
      if (document.visibilityState === "visible") fetchChanges();
    }, REFRESH_INTERVAL_MS);
    return () => clearInterval(intervalId);
  }, [client, period]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Subscriber Changes</h1>
      <PeriodSelector value={period} onChange={setPeriod} />
      {data === null ? (
        <Spinner />
      ) : (
        <>
          <SubscriberTable title="New" rows={data.new} client={client} />
          <SubscriberTable title="Unsubscribed" rows={data.removed} client={client} />
        </>
      )}
    </div>
  );
}
