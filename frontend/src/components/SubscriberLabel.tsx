import React from "react";
import { Link } from "react-router-dom";
import { SMMetricsClient } from "@/client/SMMetricsClient";

interface SubscriberIdentity {
  user_id: number;
  username?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  photo_url?: string | null;
}

export function subscriberDisplayName(subscriber: SubscriberIdentity): string {
  const name = [subscriber.first_name, subscriber.last_name].filter(Boolean).join(" ");
  return name || "(unknown)";
}

export function SubscriberAvatar({
  subscriber,
  client,
  className = "h-8 w-8 text-sm",
}: {
  subscriber: SubscriberIdentity;
  client: SMMetricsClient;
  className?: string;
}) {
  if (subscriber.photo_url) {
    return (
      <img
        src={`${client.baseUrl}${subscriber.photo_url}`}
        alt=""
        className={`${className} rounded-full object-cover shrink-0`}
      />
    );
  }
  // No photo (none set, or not downloaded yet): first letter on a neutral disc.
  const initial = (subscriberDisplayName(subscriber).replace("(", "")[0] ?? "?").toUpperCase();
  return (
    <span className={`${className} rounded-full bg-gray-200 text-gray-600 inline-flex items-center justify-center shrink-0`}>
      {initial}
    </span>
  );
}

// Avatar + name, linking to the subscriber's details page.
export default function SubscriberLabel({
  subscriber,
  client,
}: {
  subscriber: SubscriberIdentity;
  client: SMMetricsClient;
}) {
  return (
    <Link
      to={`/subscribers/${subscriber.user_id}`}
      className="inline-flex items-center gap-2 text-blue-600 hover:underline"
    >
      <SubscriberAvatar subscriber={subscriber} client={client} />
      <span>{subscriberDisplayName(subscriber)}</span>
    </Link>
  );
}
