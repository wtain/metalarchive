import React from "react";
import ReactMarkdown from "react-markdown";

const CHANNEL_NAME = "blackholelogs";

function mapUrl(originalUrl: string) {
  if (originalUrl.startsWith(`https://t.me/${CHANNEL_NAME}/`)) {
    const id = originalUrl.split("/").pop();
    return `/posts/${id}`;
  }
  return originalUrl;
}

interface PostTextProps {
  text: string;
  maxLength?: number;
}

export default function PostText({ text, maxLength }: PostTextProps) {
  const content = maxLength != null && text.length > maxLength
    ? `${text.substring(0, maxLength)}...`
    : text;

  return (
    <ReactMarkdown
      components={{
        a: ({ href, children, ...props }) => (
          <a href={mapUrl(href!)} className="text-blue-600" rel="noopener noreferrer" {...props}>
            {children}
          </a>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
