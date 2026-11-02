import React from "react";
import PostCard from "./PostCard";
import { PostChange } from "../dto/BackendDataTypes";
import { SMMetricsClient } from "@/client/SMMetricsClient";

// The card grid shared by every page that lists posts.
export default function PostGrid({ posts, client }: { posts: PostChange[]; client: SMMetricsClient }) {
  return (
    <main className="flex-1 container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {posts.map((post) => (
        <PostCard post={post} key={post.post_id} client={client} />
      ))}
    </main>
  );
}
