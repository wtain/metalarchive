import React, { useEffect, useState } from "react";
import axios from "axios";
import PostCard from "../components/PostCard";
import { Post } from "../dto/BackendDataTypes";

export default function PostListPage() {

    const [posts, setPosts] = useState<Post[]>([]);

    useEffect(() => {
        axios
          .get<{ data: Post[] }>(`http://127.0.0.1:8001/api/posts/posts`)
          .then((res) => setPosts(res.data))
          .catch(console.error);
    }, []);

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