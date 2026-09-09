import React, { useEffect, useState } from "react";
import ChartCard from "../components/ChartCard";
import { useParams, Link } from "react-router-dom";
import PostText from "../components/PostText";
import { Post, PostMetricsDataPoint } from "@/dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";


export default function PostDetailsPage(props: BasePageProperties) {
  const { id } = useParams<{ id: string }>();
  const [post, setPost] = useState<Post | null>(null);
  const [views, setViews] = useState<PostMetricsDataPoint[] | null>(null);

  const client = props.metricsClient;

  useEffect(() => {
    if (!id) return;
    client
      .getPost(parseInt(id))
      .then((post) => setPost(post));
  }, [id]);

  useEffect(() => {
    if (!id) return;
    client.getPostMetrics(parseInt(id))
      .then((data) => setViews(data));
  }, [id]);

  if (!post || !views) return <p className="p-6 text-gray-500">Loading...</p>;

  return (
    <div>
      <Link to="/reactions">Back to posts</Link>
      <h1 className="text-2xl font-bold mb-4">Post</h1>
      <ChartCard title={`Post ${id}`} data={views.map((v) => {
        return { timestamp: v.timestamp, count: v.views };
      })} />
      <div className="text-sm text-black-500 mb-2">
        <PostText text={post.text} />
      </div>
    </div>
  );
}
