import { useState, useEffect } from "react";
import Tag from "./Tag";
import { TagData } from "../dto/BackendDataTypes";
import { SMMetricsClient } from "@/client/SMMetricsClient";

interface EditableTagListProps {
  postId: number;
  initialTags: TagData[];
  client: SMMetricsClient;
}

export default function EditableTagList({ postId, initialTags, client }: EditableTagListProps) {
  const [tags, setTags] = useState(initialTags);
  const [newTag, setNewTag] = useState("");

  useEffect(() => {
    setTags(initialTags);
  }, [initialTags]);

  const addTag = async () => {
    if (!newTag.trim()) return;

    const tag = newTag.trim();
    setNewTag("");

    const created = await client.addPostTag(postId, encodeURIComponent(tag));

    setTags((prev) => [...prev, created]);
  };

  const removeTag = async (tagId: number) => {
    await client.deletePostTag(tagId);
    setTags((prev) => prev.filter((t) => t.id !== tagId));
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <Tag
            key={tag.id}
            label={tag.name}
            onRemove={() => removeTag(tag.id)}
          />
        ))}
      </div>

      <div className="flex items-center gap-2">
        <input
          className="border px-2 py-1 rounded w-40"
          placeholder="Add tag..."
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addTag()}
        />
      </div>
    </div>
  );
}
