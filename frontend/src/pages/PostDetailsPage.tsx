import React, { useEffect, useState } from "react";
import axios from "axios";
import ChartCard, { ChartDataPoint } from "../components/ChartCard";
import PeriodSelector, { Period } from "../components/PeriodSelector";
import { useParams } from "react-router-dom";

interface Post {
  id: string;
  text: string;
}

interface PostMetricsDataPoint {
   timestamp: string;
   views: number;
}

export default function PostDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const [post, setPost] = useState<Post | null>(null);
  const [views, setViews] = useState<PostMetricsDataPoint[] | null>(null);

  useEffect(() => {
    if (!id) return;
    axios
      .get<{ data: Post }>(`http://127.0.0.1:8001/api/posts/post?id=${id}`, {
          mode: 'no-cors',
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
          },
      })
      .then((data) => setPost(data.data))
      .catch(console.error);
  }, [id]);

  useEffect(() => {
    if (!id) return;
    axios
      .get<{ data: PostMetricsDataPoint[] }>(`http://127.0.0.1:8001/api/posts/metrics?id=${id}`, {
          mode: 'no-cors',
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
          },
      })
      .then((data) => setViews(data.data))
      .catch(console.error);
  }, [id]);

  if (!post || !views) return <p className="p-6 text-gray-500">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Post</h1>
      <ChartCard title={`Post ${id}`} data={views.map((v) => {
        return { timestamp: v.timestamp, count: v.views };
      })} />
      <p className="text-sm text-black-500 mb-2">{post.text}</p>
    </div>
  );
}