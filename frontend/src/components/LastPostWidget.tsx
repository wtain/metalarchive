import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "./ui/card";
import { SMMetricsClient } from "@/client/SMMetricsClient";
import { LastPost } from "@/dto/BackendDataTypes";
import { formatRelativeTime } from "@/utils/relativeTime";

const REFRESH_INTERVAL_MS = 30_000;

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

  return (
    <Card className="shadow-sm px-3 py-2">
      <div className="text-xs text-gray-500">Last post</div>
      <div className="flex flex-wrap items-baseline gap-x-3">
        <Link to={`/posts/${lastPost.post_id}`} className="text-lg font-bold hover:underline">
          {published.toLocaleString()}
        </Link>
        <span className="text-xs text-gray-500">{formatRelativeTime(now - published.getTime())}</span>
      </div>
    </Card>
  );
}
