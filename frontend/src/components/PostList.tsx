
import { SMMetricsClient } from "@/client/SMMetricsClient";
import React from "react";
import Spinner from "./Spinner";
import PostCard from "../components/PostCard";
import { Post } from "../dto/BackendDataTypes";

interface PostListProps {
    posts: Post[] | null;
    client: SMMetricsClient;
    title?: string | null;
}

export default function PostList({ posts, client, title = "Posts" }: PostListProps) {
    if (posts === null) {
        return <Spinner />
    }

    if (posts.length === 0) {
        return <p className="text-gray-500">No posts yet.</p>
    }

    return (
        <div>
            {title && <h1 className="text-2xl font-bold mb-4">{title}</h1>}
            <main className="flex-1 container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {
                  posts.map(post =>
                    <PostCard post={post} key={post.post_id} client={client} />
                  )
              }
            </main>
        </div>
    )
}