import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { SubscriberDetails } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";
import { SubscriberAvatar, subscriberDisplayName } from "../components/SubscriberLabel";

function formatDuration(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function formatDate(value: string | null): string {
  return value ? new Date(value).toLocaleString() : "—";
}

function InfoTable({ rows }: { rows: [string, React.ReactNode][] }) {
  return (
    <table className="w-full max-w-xl text-left border-collapse mb-8">
      <tbody>
        {rows.map(([label, value]) => (
          <tr key={label} className="border-b">
            <th className="py-2 pr-4 font-medium text-gray-500 w-56">{label}</th>
            <td className="py-2">{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function SubscriberDetailsPage(props: BasePageProperties) {
  const { id } = useParams();
  const [data, setData] = useState<SubscriberDetails | null>(null);
  const [notFound, setNotFound] = useState(false);

  const client = props.metricsClient;

  useEffect(() => {
    setData(null);
    setNotFound(false);
    client
      .getSubscriberDetails(Number(id))
      .then(setData)
      .catch(() => setNotFound(true));
  }, [client, id]);

  if (notFound) return <p className="text-gray-500">Subscriber not found.</p>;
  if (!data) return <p className="text-gray-500">Loading...</p>;

  const subscribed = data.status === "subscribed";

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <SubscriberAvatar subscriber={data} client={client} className="h-16 w-16 text-2xl" />
        <div>
          <h1 className="text-2xl font-bold">{subscriberDisplayName(data)}</h1>
          <span
            className={`inline-block mt-1 px-2 py-0.5 rounded text-sm ${
              subscribed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
            }`}
          >
            {subscribed ? "Subscribed" : "Left"}
          </span>
        </div>
      </div>

      <InfoTable
        rows={[
          ["User ID", data.user_id],
          ["Username", data.username ? `@${data.username}` : "(none)"],
          ["First name", data.first_name || "—"],
          ["Last name", data.last_name || "—"],
          ["First seen", formatDate(data.first_seen)],
          ["Last seen", formatDate(data.last_seen)],
          subscribed
            ? ["Subscribed since", formatDate(data.subscribed_since)]
            : ["Left at", formatDate(data.left_at)],
          ["Times joined", data.stints_count],
          ["Rejoins", data.rejoin_count],
          ["Total time subscribed", formatDuration(data.total_subscribed_seconds)],
        ]}
      />

      <h2 className="text-lg font-semibold mb-2">Subscription history ({data.stints.length})</h2>
      <table className="w-full text-left border-collapse mb-8">
        <thead>
          <tr className="border-b">
            <th className="py-2 pr-4">Added</th>
            <th className="py-2 pr-4">Removed</th>
            <th className="py-2 pr-4">Duration</th>
          </tr>
        </thead>
        <tbody>
          {data.stints.map((stint, i) => (
            <tr key={`${stint.added}-${i}`} className="border-b">
              <td className="py-2 pr-4">{formatDate(stint.added)}</td>
              <td className="py-2 pr-4">{stint.removed ? formatDate(stint.removed) : "still subscribed"}</td>
              <td className="py-2 pr-4">{formatDuration(stint.duration_seconds)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="text-lg font-semibold mb-2">Names ({data.name_history.length})</h2>
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b">
            <th className="py-2 pr-4">Username</th>
            <th className="py-2 pr-4">Name</th>
            <th className="py-2 pr-4">First seen</th>
            <th className="py-2 pr-4">Last seen</th>
          </tr>
        </thead>
        <tbody>
          {data.name_history.map((record, i) => (
            <tr key={i} className="border-b">
              <td className="py-2 pr-4">{record.username ? `@${record.username}` : "(none)"}</td>
              <td className="py-2 pr-4">{[record.first_name, record.last_name].filter(Boolean).join(" ") || "(unknown)"}</td>
              <td className="py-2 pr-4">{formatDate(record.first_seen)}</td>
              <td className="py-2 pr-4">{formatDate(record.last_seen)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
