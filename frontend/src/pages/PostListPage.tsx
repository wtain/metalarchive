import React, { useEffect, useState } from "react";
import axios from "axios";
import PostList from "../components/PostList";
import { Post } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

export default function PostListPage(props: BasePageProperties) {

    const [posts, setPosts] = useState<Post[]>([]);

    const client = props.metricsClient;

    useEffect(() => {
        client
            .listPosts()
            .then((posts) => setPosts(posts));
        // axios
        //   .get<{ data: Post[] }>(`http://127.0.0.1:8001/api/posts/posts`)
        //   .then((res) => setPosts(res.data))
        //   .catch(console.error);
    }, []);

    return (
        <PostList posts={posts} />
    )
}