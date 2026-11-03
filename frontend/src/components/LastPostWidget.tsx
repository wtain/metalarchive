import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "./ui/card";
import { SMMetricsClient } from "@/client/SMMetricsClient";
import { LastPost } from "@/dto/BackendDataTypes";
import { formatRelativeTime } from "@/utils/relativeTime";

const REFRESH_INTERVAL_MS = 30_000;
const DAY_MS = 24 * 3600 * 1000;

// Dark shades, since the cards sit on a white background.
function ageColor(elapsedMs: number): string {
  if (elapsedMs < 3 * DAY_MS) return "text-green-700";
  if (elapsedMs < 7 * DAY_MS) return "text-yellow-700";
  return "text-red-700";
}

export default function LastPostWidget({ client }: { client: SMMetricsClient }) {
  const [lastPost, setLastPost] = useState<LastPost | null>(null);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const load = () => client.getLastPost().then(setLastPost);
    load();
    // One timer drives both: re-fetch the post and re-render the relative age.
    const id = setInterval(() => {
      setNow(Date.now());
      if (document.visibilityState === "visible") load();
    }, REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [client]);

  if (!lastPost?.published_at) return null;

  const published = new Date(lastPost.published_at);
  const elapsedMs = now - published.getTime();

  return (
    <Card className="shadow-sm px-3 py-2">
      <div className="text-xs text-gray-500">Last post</div>
      <div className="flex flex-wrap items-baseline gap-x-3">
        <Link to={`/posts/${lastPost.post_id}`} className="text-lg font-bold hover:underline">
          {published.toLocaleString()}
        </Link>
        <span className={`text-xs font-medium ${ageColor(elapsedMs)}`}>{formatRelativeTime(elapsedMs)}</span>
      </div>
      {lastPost.title && <div className="max-w-sm text-sm text-gray-700 line-clamp-2">{lastPost.title}</div>}
    </Card>
  );
}
