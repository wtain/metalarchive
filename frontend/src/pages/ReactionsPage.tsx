import React, { useCallback, useEffect, useState } from "react";
import PeriodSelector, { Period } from "../components/PeriodSelector";
import Spinner from "../components/Spinner";
import PostGrid from "../components/PostGrid";
import PostMetrics from "../components/PostMetrics";
import { Digest } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

// Full refetch on an interval - real data only changes every ~15min (scheduled
// scrape) or on a manual trigger, so this is just about not staring at stale
// numbers, not keeping pace with fast-changing data.
const REFRESH_INTERVAL_MS = 60_000;

export default function ReactionsPage(props: BasePageProperties) {
  const [period, setPeriod] = useState<Period>("daily");
  const [data, setData] = useState<Digest | null>(null);

  const client = props.metricsClient;

  const fetchDigest = useCallback(() => {
    client
      .getDigest(period)
      .then((digest) => setData(digest));
  }, [client, period]);

  useEffect(() => {
    // Spinner again on a period switch; the interval refetches update in place.
    setData(null);
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
      {data === null ? <Spinner /> : (<>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-2 text-sm text-gray-500">
        <span>Gained over the {period} period:</span>
        <PostMetrics
          signed
          views={{ value: data.views_total }}
          reactions={{ value: data.reactions_total }}
          comments={{ value: data.comments_total }}
        />
      </div>
      <PostGrid posts={data.posts} client={client} />
      </>)}
    </div>
  );
}
