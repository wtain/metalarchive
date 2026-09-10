
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "@/components/ui/button"
import EditableTitle from "../components/EditableTitle"
import EditableTagList from "../components/EditableTagList"
import MetricDisplay from "../components/MetricDisplay"
import PostText from "../components/PostText"
import { PostChange } from "../dto/BackendDataTypes";
import { useNavigate } from "react-router-dom";
import { SMMetricsClient } from "@/client/SMMetricsClient";

interface PostCardProps {
    post: PostChange;
    client: SMMetricsClient;
}

export default function PostCard({ post, client }: PostCardProps ) {

    const navigate = useNavigate();

    return (
        <Card className={`shadow-md hover:shadow-lg transition ${post.is_new ? "bg-green-50 border-green-400" : ""}`}>
          <CardHeader>
            <CardTitle>
              {post.is_new && <span className="mr-2">🆕✨ NEW</span>}
              {post.post_id}. <EditableTitle postId={post.post_id} initialTitle={post.title ?? "???"} client={client} />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <EditableTagList postId={post.post_id} initialTags={post.tags ?? []} client={client} />
            <div className="text-sm text-black-500 mb-2">
              <PostText text={post.text} maxLength={200} />
            </div>
            {
              (post.views_new ?? post.views) != null &&
                <div>
                  <p className="text-sm font-bold text-gray-500 mb-2">Views</p>
                  <MetricDisplay value={post.views_new ?? post.views ?? 0} valueDiff={post.views_diff ?? 0} />
                </div>
            }
            {
              (post.reactions_new ?? post.reactions) != null &&
                <div>
                  <p className="text-sm font-bold text-gray-500 mb-2">Reactions</p>
                  <MetricDisplay value={post.reactions_new ?? post.reactions ?? 0} valueDiff={post.reactions_diff ?? 0} />
                </div>
            }
            {
              (post.comments_new ?? post.comments) != null &&
                <div>
                  <p className="text-sm font-bold text-gray-500 mb-2">Comments</p>
                  <MetricDisplay value={post.comments_new ?? post.comments ?? 0} valueDiff={post.comments_diff ?? 0} />
                </div>
            }
            <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white" onClick={
            () => {
                navigate(`/posts/${post.post_id}`);
            }
            }>View Details</Button>
          </CardContent>
        </Card>
    )
}