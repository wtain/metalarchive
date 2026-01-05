import { useState, useEffect } from "react";
import Tag from "./Tag";
import { TagData } from "../dto/BackendDataTypes";

// interface TagData {
//   id: number;
//   label: string;
// }

interface EditableTagListProps {
  postId: number;
//   initialTags: TagData[];
    // initialTags: string[];
    initialTags: TagData[];
}

export default function EditableTagList({ postId, initialTags }: EditableTagListProps) {
  const [tags, setTags] = useState(initialTags);
  const [newTag, setNewTag] = useState("");

  useEffect(() => {
    setTags(initialTags);
  }, [initialTags]);

  const addTag = async () => {
    if (!newTag.trim()) return;

    const tag = newTag.trim();
    setNewTag("");

    const res = await fetch(`http://127.0.0.1:8001/api/tags/add?post_id=${postId}&name=${encodeURIComponent(tag)}`, {
      method: "POST",
    });

    const created = await res.json(); // expects: { id: number, label: string }

    setTags((prev) => [...prev, created]);
  };

  // const removeTag = async (tagId: number) => {
  const removeTag = async (tagId: number) => {
    await fetch(`http://127.0.0.1:8001/api/tags/delete?tag_id=${tagId}`, {
      method: "DELETE",
    });
    // setTags((prev) => prev.filter((t) => t.id !== tagId));
    setTags((prev) => prev.filter((t) => t.id !== tagId));
  };

  return (
    <div className="space-y-3">
      {/* Tag List */}
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
        //   <Tag
        //     key={tag.id}
        //     label={tag.label}
        //     onRemove={() => removeTag(tag.id)}
        //   />
          <Tag
            key={tag.id}
            label={tag.name}
            onRemove={() => removeTag(tag.id)}
          />
        ))}
      </div>

      {/* Add Tag Input */}
      <div className="flex items-center gap-2">
        <input
          className="border px-2 py-1 rounded w-40"
          placeholder="Add tag..."
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addTag()}
        />
        {/* <button
          onClick={addTag}
          className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Add
        </button> */}
      </div>
    </div>
  );
}
