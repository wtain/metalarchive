import React, { useEffect, useState } from "react";
import { Card } from "./ui/card";
import { SMMetricsClient } from "@/client/SMMetricsClient";
import { formatRelativeTime } from "@/utils/relativeTime";

const REFRESH_INTERVAL_MS = 60_000;
// The scraper runs every 15 minutes; well past that, the data is stale.
const STALE_AFTER_MINUTES = 45;

function formatAge(minutes: number): string {
  return minutes < 1 ? "just now" : formatRelativeTime(minutes * 60_000);
}

export default function FreshnessWidget({ client }: { client: SMMetricsClient }) {
  const [asOf, setAsOf] = useState<Date | null>(null);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const load = () => client.getFreshness().then((f) => setAsOf(f.as_of ? new Date(f.as_of) : null));
    load();
    // One timer drives both: re-fetch the timestamp and re-render the age.
    const id = setInterval(() => {
      setNow(Date.now());
      if (document.visibilityState === "visible") load();
    }, REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [client]);

  if (!asOf) return null;

  const minutes = Math.max(0, Math.floor((now - asOf.getTime()) / 60_000));
  const stale = minutes > STALE_AFTER_MINUTES;

  return (
    <Card className={`shadow-sm px-3 py-2 ${stale ? "border-amber-400 bg-amber-50" : ""}`}>
      <div className="flex flex-wrap items-baseline gap-x-3">
        <span className={`text-lg font-bold ${stale ? "text-amber-700" : "text-green-700"}`}>
          Refreshed {formatAge(minutes)}
        </span>
        <span className="text-xs text-gray-500">Data as of {asOf.toLocaleString()}</span>
      </div>
    </Card>
  );
}
