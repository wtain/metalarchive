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

    // axios
    //   .get<{ data: Post }>(`http://127.0.0.1:8001/api/posts/post?id=${id}`, {
    //       mode: 'no-cors',
    //       headers: {
    //         'Access-Control-Allow-Origin': '*',
    //         'Content-Type': 'application/json',
    //       },
    //   })
    //   .then((data) => setPost(data.data))
    //   .catch(console.error);
  }, [id]);

  useEffect(() => {
    if (!id) return;
    client.getPostMetrics(parseInt(id))
      .then((data) => setViews(data));
    // axios
    //   .get<{ data: PostMetricsDataPoint[] }>(`http://127.0.0.1:8001/api/posts/metrics?id=${id}`, {
    //       mode: 'no-cors',
    //       headers: {
    //         'Access-Control-Allow-Origin': '*',
    //         'Content-Type': 'application/json',
    //       },
    //   })
    //   .then((data) => setViews(data.data))
    //   .catch(console.error);
  }, [id]);

  if (!post || !views) return <p className="p-6 text-gray-500">Loading...</p>;

  // var text = post.text

  // let regex = new RegExp(/\[(.+)\]\((.+)\)/, "g")
  // var text = post.text.replace(regex, (_, p1, p2) => `<A href=${p2}>${p1}</A>`)

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


/*

<ReactMarkdown
  components={{
    a: ({node, ...props}) => (
      <a {...props} className="text-blue-600 underline" target="_blank"/>
    )
  }}
>
  {post.text}
</ReactMarkdown>


<ReactMarkdown
  components={{
    a: ({node, href, children, ...props}) => {
      const newHref = mapUrl(href);

      return (
        <a
          href={newHref}
          className="text-blue-600 underline"
          target="_blank"
          rel="noopener noreferrer"
          {...props}
        >
          {children}
        </a>
      );
    }
  }}
>


<ReactMarkdown
  components={{
    a: ({node, href, children, ...props}) => {
      const route = mapHrefToRoute(href);

      if (route) {
        return (
          <Link to={route} className="text-blue-600 underline">
            {children}
          </Link>
        );
      }

      // default external link
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline"
          {...props}
        >
          {children}
        </a>
      );
    }
  }}
>
  {post.text}
</ReactMarkdown>

 */