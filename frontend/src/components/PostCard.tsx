
import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "@/components/ui/button"
import MetricDisplay from "../components/MetricDisplay"
import { Subscriber, SubscriberChanges, PostChange, Digest } from "../dto/BackendDataTypes";
import { useNavigate } from "react-router-dom";

interface PostCardProps {
    post: PostChange;
}

export default function PostCard({ post }: PostCardProps ) {

    const navigate = useNavigate();

    return (
        <Card className="shadow-md hover:shadow-lg transition">
          <CardHeader>
            <CardTitle>{post.post_id}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-black-500 mb-2">{post.text.substring(0, 200)}...</p>
            { 
              post.views_new != null &&
                <div>
                  <p className="text-sm font-bold text-gray-500 mb-2">Views</p>
                  <MetricDisplay value={post.views_new} valueDiff={post.views_diff} />
                </div>
            }            
            {
              post.reactions_new != null &&
                <div>
                  <p className="text-sm font-bold text-gray-500 mb-2">Reactions</p>
                  <MetricDisplay value={post.reactions_new} valueDiff={post.reactions_diff} />      
                </div>
            }
            {
              post.comments_new != null &&
                <div>
                  <p className="text-sm font-bold text-gray-500 mb-2">Comments</p>
                  <MetricDisplay value={post.comments_new} valueDiff={post.comments_diff} />
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