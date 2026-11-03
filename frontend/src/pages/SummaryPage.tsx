import React, { useEffect, useState } from "react";
import { Card } from "../components/ui/card";
import PeriodSelector, { Period } from "../components/PeriodSelector";
import { Subscriber, Summary } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";
import { Link } from "react-router-dom";
import SubscriberLabel from "../components/SubscriberLabel";
import { SMMetricsClient } from "@/client/SMMetricsClient";
import Spinner from "../components/Spinner";
import FreshnessWidget from "../components/FreshnessWidget";
import LastPostWidget from "../components/LastPostWidget";

// Same cadence as the other pages: data only changes with the ~15min scrape.
const REFRESH_INTERVAL_MS = 60_000;

function formatChange(change: number): string {
  return change > 0 ? `+${change}` : `${change}`;
}

function changeColor(change: number): string {
  if (change > 0) return "text-green-600";
  if (change < 0) return "text-red-600";
  return "text-gray-500";
}

function StatCard({ title, total, change }: { title: string; total: number; change?: number }) {
  return (
    <Card className="shadow-sm px-3 py-2">
      <div className="text-xs text-gray-500">{title}</div>
      <div className="flex items-baseline gap-2">
        <span className="text-xl font-bold leading-tight">{total.toLocaleString()}</span>
        {change !== undefined && (
          <span className={`text-sm ${changeColor(change)}`}>{formatChange(change)}</span>
        )}
      </div>
    </Card>
  );
}

function SubscriberList({ title, rows, client }: { title: string; rows: Subscriber[]; client: SMMetricsClient }) {
  return (
    <div>
      <h3 className="font-semibold mb-2">{title} ({rows.length})</h3>
      {rows.length === 0 ? (
        <div className="text-gray-500">None</div>
      ) : (
        <ul className="space-y-1">
          {rows.map((s) => (
            <li key={`${s.user_id}-${s.timestamp}`} className="flex justify-between gap-4 border-b py-1">
              <SubscriberLabel subscriber={s} client={client} />
              <span className="text-gray-500 whitespace-nowrap">{new Date(s.timestamp).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function SummaryPage(props: BasePageProperties) {
  const [period, setPeriod] = useState<Period>("daily");
  const [data, setData] = useState<Summary | null>(null);

  const client = props.metricsClient;

  useEffect(() => {
    setData(null);
    const fetchSummary = () => client.getSummary(period).then(setData);
    fetchSummary();

    // Silent refetch (no reset to "Loading...") so new scrapes appear on their own.
    const intervalId = setInterval(() => {
      if (document.visibilityState === "visible") fetchSummary();
    }, REFRESH_INTERVAL_MS);
    return () => clearInterval(intervalId);
  }, [client, period]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Summary</h1>
      <div className="flex flex-wrap gap-2 mb-3">
        <FreshnessWidget client={client} />
        <LastPostWidget client={client} />
      </div>
      <PeriodSelector value={period} onChange={setPeriod} />

      {data === null && <Spinner />}
      {data !== null && !data.available && (
        <div className="text-gray-500">Not enough data for this period yet.</div>
      )}

      {data?.available && data.posts && data.subscribers && data.views && data.reactions && data.comments && (
        <>
          <div className="text-sm text-gray-500 mb-4">
            {new Date(data.from!).toLocaleString()} → {new Date(data.to!).toLocaleString()}
          </div>

          <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(8.5rem,1fr))] mb-6">
            <StatCard title="Subscribers" total={data.subscribers.total} change={data.subscribers.change} />
            <StatCard title="Posts" total={data.posts.total} change={data.posts.new_count} />
            <StatCard title="Views" total={data.views.total} change={data.views.change} />
            <StatCard title="Reactions" total={data.reactions.total} change={data.reactions.change} />
            <StatCard title="Comments" total={data.comments.total} change={data.comments.change} />
          </div>

          <h2 className="text-lg font-semibold mb-2">Subscribers</h2>
          <div className="grid gap-6 md:grid-cols-2 mb-8">
            <SubscriberList title="Joined" rows={data.subscribers.new} client={client} />
            <SubscriberList title="Left" rows={data.subscribers.removed} client={client} />
          </div>

          <h2 className="text-lg font-semibold mb-2">New posts ({data.posts.new_count})</h2>
          {data.posts.new.length === 0 ? (
            <div className="text-gray-500">None</div>
          ) : (
            <ul className="space-y-1">
              {data.posts.new.map((post) => (
                <li key={post.post_id} className="border-b py-1 flex justify-between gap-4">
                  <div className="flex flex-wrap items-baseline gap-x-3">
                    <Link to={`/posts/${post.post_id}`} className="text-blue-600 hover:underline">
                      {post.post_id}. {post.title ?? "???"}
                    </Link>
                    {post.published_at && (
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {new Date(post.published_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                  <span className="text-gray-500 whitespace-nowrap">
                    {post.views} views · {post.reactions} reactions · {post.comments} comments
                  </span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
