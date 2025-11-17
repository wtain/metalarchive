import React, { useEffect, useState } from "react";
import axios from "axios";
import ChartCard, { ChartDataPoint } from "../components/ChartCard";
import PeriodSelector, { Period } from "../components/PeriodSelector";
import { useParams, Link } from "react-router-dom";

interface Post {
  post_id: string;
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

  let regex = new RegExp(/\[(.+)\]\((.+)\)/, "g")
  // var text = post.text.replace(regex, (_, p1, p2) => `<A href=${p2}>${p1}</A>`)
  var text = post.text

  return (
    <div>
      <Link to="/reactions">Back to posts</Link>
      <h1 className="text-2xl font-bold mb-4">Post</h1>
      <ChartCard title={`Post ${id}`} data={views.map((v) => {
        return { timestamp: v.timestamp, count: v.views };
      })} />
      <p className="text-sm text-black-500 mb-2">{text}</p>
    </div>
  );
}