import React, { useEffect, useState } from "react";
import PeriodSelector, { Period } from "../components/PeriodSelector";
import { Subscriber, SubscriberChanges } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

function displayName(subscriber: Subscriber): string {
  const name = [subscriber.first_name, subscriber.last_name].filter(Boolean).join(" ");
  return name || "(unknown)";
}

function SubscriberTable({ title, rows }: { title: string; rows: Subscriber[] }) {
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
              <td className="py-2 pr-4">{displayName(s)}</td>
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
  const [data, setData] = useState<SubscriberChanges>({ new: [], removed: [] });

  const client = props.metricsClient;

  useEffect(() => {
    client
      .getSubscriberChanges(period)
      .then((data) => setData(data));
  }, [period]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Subscriber Changes</h1>
      <PeriodSelector value={period} onChange={setPeriod} />
      <SubscriberTable title="New" rows={data.new} />
      <SubscriberTable title="Unsubscribed" rows={data.removed} />
    </div>
  );
}
