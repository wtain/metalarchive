
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Eye, Heart, MessageCircle } from "lucide-react";
import EditableTitle from "../components/EditableTitle"
import EditableTagList from "../components/EditableTagList"
import MetricDisplay from "../components/MetricDisplay"
import PostText from "../components/PostText"
import { PostChange } from "../dto/BackendDataTypes";
import { Link, useNavigate } from "react-router-dom";
import { SMMetricsClient } from "@/client/SMMetricsClient";

interface PostCardProps {
    post: PostChange;
    client: SMMetricsClient;
}

export default function PostCard({ post, client }: PostCardProps ) {

    const navigate = useNavigate();

    return (
        <Card className={`flex flex-col overflow-hidden shadow-md hover:shadow-lg transition ${post.is_new ? "bg-green-50 border-green-400" : ""}`}>
          <CardHeader className={`p-4 border-b ${post.is_new ? "bg-green-100 border-green-300" : "bg-slate-100 border-slate-200"}`}>
            <CardTitle>
              {post.is_new && <span className="mr-2">🆕✨ NEW</span>}
              {post.post_id}. <EditableTitle postId={post.post_id} initialTitle={post.title ?? "???"} client={client} />
            </CardTitle>
            {post.published_at && (
              <p className="text-xs text-gray-500">
                Published {new Date(post.published_at).toLocaleString()}
              </p>
            )}
          </CardHeader>
          <CardContent className="flex flex-1 flex-col p-4">
            {post.images && post.images.length > 0 && (
              // At most two thumbnails side by side (one fixed-height row), so
              // a post with many images doesn't stretch the whole grid row.
              <div className={`grid gap-2 mb-3 ${post.images.length > 1 ? "grid-cols-2" : "grid-cols-1"}`}>
                {post.images.slice(0, 2).map((image, index) => (
                  <div key={image.id} className="relative">
                    <img
                      src={`${client.baseUrl}${image.url}`}
                      alt=""
                      className="w-full h-40 object-cover rounded-md"
                    />
                    {index === 1 && post.images!.length > 2 && (
                      <span className="absolute inset-0 flex items-center justify-center rounded-md bg-black/50 text-lg font-medium text-white">
                        +{post.images!.length - 2}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
            <EditableTagList
              postId={post.post_id}
              initialTags={post.tags ?? []}
              client={client}
              onClickTag={(name) => navigate(`/search?tag=${encodeURIComponent(name)}`)}
              maxVisible={4}
            />
            <div className="text-sm text-black-500 mb-2">
              <PostText text={post.text} maxLength={200} />
            </div>
            <div className="mt-auto flex items-center justify-between gap-3 border-t border-gray-200 pt-3">
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
                {(post.views_new ?? post.views) != null &&
                  <MetricDisplay icon={Eye} label="Views" value={post.views_new ?? post.views ?? 0} valueDiff={post.views_diff ?? 0} />}
                {(post.reactions_new ?? post.reactions) != null &&
                  <MetricDisplay icon={Heart} label="Reactions" value={post.reactions_new ?? post.reactions ?? 0} valueDiff={post.reactions_diff ?? 0} />}
                {(post.comments_new ?? post.comments) != null &&
                  <MetricDisplay icon={MessageCircle} label="Comments" value={post.comments_new ?? post.comments ?? 0} valueDiff={post.comments_diff ?? 0} />}
              </div>
              <Link to={`/posts/${post.post_id}`} className="text-sm text-indigo-600 hover:underline whitespace-nowrap">
                Details →
              </Link>
            </div>
          </CardContent>
        </Card>
    )
}