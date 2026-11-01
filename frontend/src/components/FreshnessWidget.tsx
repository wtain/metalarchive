import React, { useEffect, useState } from "react";
import { Card } from "./ui/card";
import { SMMetricsClient } from "@/client/SMMetricsClient";

const REFRESH_INTERVAL_MS = 60_000;
// The scraper runs every 15 minutes; well past that, the data is stale.
const STALE_AFTER_MINUTES = 45;

function plural(n: number, unit: string): string {
  return `${n} ${unit}${n === 1 ? "" : "s"}`;
}

function formatAge(minutes: number): string {
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${plural(minutes, "minute")} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${plural(hours, "hour")} ago`;
  return `${plural(Math.floor(hours / 24), "day")} ago`;
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
    <Card className={`shadow-sm px-3 py-2 mb-3 ${stale ? "border-amber-400 bg-amber-50" : ""}`}>
      <div className="flex flex-wrap items-baseline gap-x-3">
        <span className={`text-lg font-bold ${stale ? "text-amber-700" : "text-green-700"}`}>
          Refreshed {formatAge(minutes)}
        </span>
        <span className="text-xs text-gray-500">Data as of {asOf.toLocaleString()}</span>
      </div>
    </Card>
  );
}
