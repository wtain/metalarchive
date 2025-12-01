import React, { useEffect, useState } from "react";
import axios from "axios";
import PostCard from "../components/PostCard";
import PostList from "../components/PostList";
import { Post } from "../dto/BackendDataTypes";

export default function PostListPage() {

    const [posts, setPosts] = useState<Post[]>([]);

    useEffect(() => {
        axios
          .get<{ data: Post[] }>(`http://127.0.0.1:8001/api/posts/posts`)
          .then((res) => setPosts(res.data))
          .catch(console.error);
    }, []);

    return (
        <PostList posts={posts} />
    )
}