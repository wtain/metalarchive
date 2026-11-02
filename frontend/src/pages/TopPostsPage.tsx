import React, { useEffect, useState } from "react";
import PostList from "../components/PostList";
import { Post } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

export default function TopPostsPage(props: BasePageProperties) {

    const [posts, setPosts] = useState<Post[] | null>(null);

    const client = props.metricsClient;

    useEffect(() => {
        client
            .getTopPosts()
            .then((posts) => setPosts(posts));
    }, []);

    return (
        <PostList posts={posts} client={client} title="Top posts" />
    )
}