import React, { useEffect, useState } from "react";
import ChartCard from "../components/ChartCard";
import { useParams, Link } from "react-router-dom";
import PostText from "../components/PostText";
import { Post, PostMetricsDataPoint, SimilarPosts } from "@/dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";


export default function PostDetailsPage(props: BasePageProperties) {
  const { id } = useParams<{ id: string }>();
  const [post, setPost] = useState<Post | null>(null);
  const [views, setViews] = useState<PostMetricsDataPoint[] | null>(null);
  const [similar, setSimilar] = useState<SimilarPosts | null>(null);

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

  useEffect(() => {
    if (!id) return;
    client.getSimilarPosts(parseInt(id))
      .then((data) => setSimilar(data));
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
      {
        similar &&
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-2">Similar Posts</h2>
            {
              similar.available && similar.posts.length > 0
                ? (
                  <ul className="space-y-1">
                    {similar.posts.map((p) => (
                      <li key={p.post_id}>
                        <Link to={`/posts/${p.post_id}`} className="text-blue-600 hover:underline">
                          {p.title ?? `Post ${p.post_id}`}
                        </Link>
                        <span className="text-gray-400 text-sm ml-2">{(p.similarity * 100).toFixed(0)}% similar</span>
                      </li>
                    ))}
                  </ul>
                )
                : <p className="text-gray-500 text-sm">Similar posts not available for this post yet.</p>
            }
          </div>
      }
    </div>
  );
}
