import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import PostList from "../components/PostList";
import { Post } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

export default function SearchResultsPage(props: BasePageProperties) {

    const [searchParams] = useSearchParams();
    const tag = searchParams.get("tag") ?? undefined;

    const [posts, setPosts] = useState<Post[] | null>(null);

    const client = props.metricsClient;

    useEffect(() => {
        setPosts(null);
        client
            .listPosts(tag)
            .then((posts) => setPosts(posts));
    }, [tag]);

    if (posts === null) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">
                {tag ? `Posts tagged "${tag}"` : "Search results"}
            </h1>
            {
                posts.length === 0
                    ? <p className="text-gray-500">No posts found.</p>
                    : <PostList posts={posts} client={client} title={null} />
            }
        </div>
    );
}
