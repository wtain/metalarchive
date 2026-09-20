import React, { useEffect, useState } from "react";
import { SubscriberLifecycle, SubscriberLifecycleEntry } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

function displayName(entry: SubscriberLifecycleEntry): string {
  const name = [entry.first_name, entry.last_name].filter(Boolean).join(" ");
  return name || "(unknown)";
}

function formatDuration(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function PastSubscribersTable({ rows }: { rows: SubscriberLifecycleEntry[] }) {
  return (
    <div className="mb-8">
      <h2 className="text-lg font-semibold mb-2">Past Subscribers ({rows.length})</h2>
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b">
            <th className="py-2 pr-4">Username</th>
            <th className="py-2 pr-4">Name</th>
            <th className="py-2 pr-4">Added</th>
            <th className="py-2 pr-4">Removed</th>
            <th className="py-2 pr-4">Duration</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((s, i) => (
            <tr key={`${s.user_id}-${s.added}-${i}`} className="border-b">
              <td className="py-2 pr-4">{s.username ? `@${s.username}` : "(none)"}</td>
              <td className="py-2 pr-4">{displayName(s)}</td>
              <td className="py-2 pr-4">{new Date(s.added).toLocaleString()}</td>
              <td className="py-2 pr-4">{s.removed ? new Date(s.removed).toLocaleString() : ""}</td>
              <td className="py-2 pr-4">{formatDuration(s.duration_seconds)}</td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td className="py-2 text-gray-500" colSpan={5}>None</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function CurrentSubscribersTable({ rows }: { rows: SubscriberLifecycleEntry[] }) {
  return (
    <div className="mb-8">
      <h2 className="text-lg font-semibold mb-2">Current Subscribers ({rows.length})</h2>
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b">
            <th className="py-2 pr-4">Username</th>
            <th className="py-2 pr-4">Name</th>
            <th className="py-2 pr-4">Added</th>
            <th className="py-2 pr-4">Duration</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((s) => (
            <tr key={s.user_id} className="border-b">
              <td className="py-2 pr-4">{s.username ? `@${s.username}` : "(none)"}</td>
              <td className="py-2 pr-4">{displayName(s)}</td>
              <td className="py-2 pr-4">{new Date(s.added).toLocaleString()}</td>
              <td className="py-2 pr-4">{formatDuration(s.duration_seconds)}</td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td className="py-2 text-gray-500" colSpan={4}>None</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default function SubscriberLifecyclePage(props: BasePageProperties) {
  const [data, setData] = useState<SubscriberLifecycle | null>(null);

  const client = props.metricsClient;

  useEffect(() => {
    client
      .getSubscriberLifecycle()
      .then((data) => setData(data));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Subscriber Lifecycle</h1>
      {
        data
          ? (
            <>
              <PastSubscribersTable rows={data.past} />
              <CurrentSubscribersTable rows={data.current} />
            </>
          )
          : <p className="text-gray-500">Loading...</p>
      }
    </div>
  );
}
