
import React, { useEffect, useState } from "react";
import PostCard from "../components/PostCard";
import { Post } from "../dto/BackendDataTypes";

interface PostListProps {
    posts: Post[];
}

export default function PostList({ posts }: PostListProps) {
    if (posts.length == 0) {
        return (
            <div>Loading...</div>
        )
    }

    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Posts</h1>
            <main className="flex-1 container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {
                  posts.map(post =>
                    <PostCard post={post} key={post.post_id} />
                  )
              }
            </main>
        </div>
    )
}