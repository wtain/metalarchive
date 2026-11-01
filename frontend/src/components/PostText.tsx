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

// Cuts markdown to `maxLength` *visible* characters: a link counts only for its
// label, not its (often very long) URL, and is never cut in half, so the
// preview doesn't end up as a few words plus a mangled "[text](https://...".
export function truncateMarkdown(text: string, maxLength: number): string {
  const link = /\[([^\]]*)\]\(([^)\s]*)\)/g;
  let visible = 0;
  let result = "";
  let last = 0;

  const take = (chunk: string): boolean => {
    const room = maxLength - visible;
    if (chunk.length <= room) {
      result += chunk;
      visible += chunk.length;
      return true;
    }
    result += chunk.substring(0, room);
    visible = maxLength;
    return false;
  };

  for (const match of text.matchAll(link)) {
    if (!take(text.substring(last, match.index))) return `${result}...`;
    const [whole, label, url] = match;
    const room = maxLength - visible;
    if (label.length > room) {
      return `${result}[${label.substring(0, room)}](${url})...`;
    }
    result += whole;
    visible += label.length;
    last = match.index! + whole.length;
  }
  if (!take(text.substring(last))) return `${result}...`;
  return result;
}

export default function PostText({ text, maxLength }: PostTextProps) {
  const content = maxLength != null ? truncateMarkdown(text, maxLength) : text;

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
