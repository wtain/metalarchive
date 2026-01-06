import React, { useEffect, useState } from "react";
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
    }, []);

    return (
        <PostList posts={posts} client={client} />
    )
}