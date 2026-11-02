
import { SMMetricsClient } from "@/client/SMMetricsClient";
import React from "react";
import Spinner from "./Spinner";
import PostGrid from "./PostGrid";
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
            <PostGrid posts={posts} client={client} />
        </div>
    )
}