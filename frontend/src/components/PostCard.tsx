
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "@/components/ui/button"
import EditableTitle from "../components/EditableTitle"
import EditableTagList from "../components/EditableTagList"
import MetricDisplay from "../components/MetricDisplay"
import TagList from "../components/TagList"
import { PostChange, Digest, TagData } from "../dto/BackendDataTypes";
import { useNavigate } from "react-router-dom";

interface PostCardProps {
    post: PostChange;
}

export default function PostCard({ post }: PostCardProps ) {

    const navigate = useNavigate();

    const [title, setTitle] = useState<string>("???");
    const [tags, setTags] = useState<TagData[]>([]);

    useEffect(() => {
        axios
          .get<{ data: string }>(`http://127.0.0.1:8001/api/posts/post_header?post_id=${post.post_id}`)
          .then((res) => {
            // console.log(res.data);
            // setTitle("AAA")
            // console.log("AAA");
            setTitle(res.data)
          })
          .catch(console.error);
    }, []);

    useEffect(() => {
      axios
        .get<{ data: TagData[] }>(`http://127.0.0.1:8001/api/posts/post_tags?post_id=${post.post_id}`)
        .then((res) => setTags(res.data))
        .catch(console.error);
  }, []);

  // const removeTag = (tag: string) => {
  //   setTags((t) => t.filter((x) => x !== tag));
  // };

  // const clickedTag = (tag: string) => {
  //   console.log("Clicked tag:", tag);
  // };

    return (
        <Card className="shadow-md hover:shadow-lg transition">
          <CardHeader>
            <CardTitle>
              {post.post_id}. <EditableTitle postId={post.post_id} initialTitle={title} />
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Readonly */}
            {/* <TagList
              tags={tags.map(t => {
                return t.name;
              })}
              onRemoveTag={removeTag}
              onClickTag={clickedTag}
            /> */}
            <EditableTagList postId={post.post_id} initialTags={tags} />
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