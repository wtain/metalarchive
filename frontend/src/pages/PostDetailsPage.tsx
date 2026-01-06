import React, { useEffect, useState } from "react";
import ChartCard from "../components/ChartCard";
import { useParams, Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { Post, PostMetricsDataPoint } from "@/dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";


export default function PostDetailsPage(props: BasePageProperties) {
  const { id } = useParams<{ id: string }>();
  const [post, setPost] = useState<Post | null>(null);
  const [views, setViews] = useState<PostMetricsDataPoint[] | null>(null);

  const CHANNEL_NAME = "blackholelogs";

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

  function mapUrl(originalUrl: string) {
    // 👇 Your custom logic
    if (originalUrl.startsWith(`https://t.me/${CHANNEL_NAME}/`)) {
      const id = originalUrl.split("/").pop();
      return `/posts/${id}`;
    }
  
    // default: return original
    return originalUrl;
  }

  return (
    <div>
      <Link to="/reactions">Back to posts</Link>
      <h1 className="text-2xl font-bold mb-4">Post</h1>
      <ChartCard title={`Post ${id}`} data={views.map((v) => {
        return { timestamp: v.timestamp, count: v.views };
      })} />
      <p className="text-sm text-black-500 mb-2">
        <ReactMarkdown 
          components={{
            a: ({node, href, children, ...props}) => {
              const newHref = mapUrl(href!);
        
              return (
                <a
                  href={newHref}
                  className="text-blue-600"
                  rel="noopener noreferrer"
                  {...props}
                >
                  {children}
                </a>
              );
            }
          }}>
          {post.text}
        </ReactMarkdown>
      </p>
    </div>
  );
}
