import React, { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import PeriodSelector, { Period } from "../components/PeriodSelector";
import PostCard from "../components/PostCard";
import { Digest } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

// Full refetch on an interval - real data only changes every ~15min (scheduled
// scrape) or on a manual trigger, so this is just about not staring at stale
// numbers, not keeping pace with fast-changing data.
const REFRESH_INTERVAL_MS = 60_000;

export default function ReactionsPage(props: BasePageProperties) {
  const [period, setPeriod] = useState<Period>("daily");
  const [data, setData] = useState<Digest>({posts: []});

  const client = props.metricsClient;

  const fetchDigest = useCallback(() => {
    client
      .getDigest(period)
      .then((digest) => setData(digest));
  }, [client, period]);

  useEffect(() => {
    fetchDigest();

    const intervalId = setInterval(() => {
      if (document.visibilityState === "visible") {
        fetchDigest();
      }
    }, REFRESH_INTERVAL_MS);

    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        fetchDigest();
      }
    };
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      clearInterval(intervalId);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, [fetchDigest]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Reactions</h1>
      <PeriodSelector value={period} onChange={setPeriod} />
      <Card className="shadow-md hover:shadow-lg transition">
          <CardHeader>
            <CardTitle>Statistics: {period}</CardTitle>
          </CardHeader>
          <CardContent>
            <div>Views: {data.views_total}</div>
            <div>Reactions: {data.reactions_total}</div>
            <div>Comments: {data.comments_total}</div>
          </CardContent>
      </Card>
      <main className="flex-1 container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {
          data.posts.map(post =>
            <PostCard post={post} key={post.post_id} client={client} />
          )
      }
      </main>
    </div>
  );
}
