import { useState, useEffect, useRef } from "react";
import { Plus } from "lucide-react";
import Tag from "./Tag";
import { TagData } from "../dto/BackendDataTypes";
import { SMMetricsClient } from "@/client/SMMetricsClient";

interface EditableTagListProps {
  postId: number;
  initialTags: TagData[];
  client: SMMetricsClient;
  onClickTag?: (name: string) => void;
  // Show at most this many tags, the rest collapse into a "+N" chip that expands on click.
  maxVisible?: number;
}

const chipClass = "inline-flex items-center rounded-full px-2 py-0.5 text-xs";

export default function EditableTagList({ postId, initialTags, client, onClickTag, maxVisible }: EditableTagListProps) {
  const [tags, setTags] = useState(initialTags);
  const [newTag, setNewTag] = useState("");
  const [adding, setAdding] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setTags(initialTags);
  }, [initialTags]);

  useEffect(() => {
    if (adding) inputRef.current?.focus();
  }, [adding]);

  const addTag = async () => {
    const tag = newTag.trim();
    if (!tag) return;
    setNewTag("");

    const created = await client.addPostTag(postId, encodeURIComponent(tag));

    setTags((prev) => [...prev, created]);
  };

  const closeInput = () => {
    setAdding(false);
    setNewTag("");
  };

  const removeTag = async (tagId: number) => {
    await client.deletePostTag(tagId);
    setTags((prev) => prev.filter((t) => t.id !== tagId));
  };

  const collapsed = maxVisible !== undefined && !expanded && tags.length > maxVisible;
  const visibleTags = collapsed ? tags.slice(0, maxVisible) : tags;

  return (
    <div className="flex flex-wrap items-center gap-1.5 mb-2">
      {visibleTags.map((tag) => (
        <Tag
          key={tag.id}
          label={tag.name}
          onRemove={() => removeTag(tag.id)}
          onClick={onClickTag ? () => onClickTag(tag.name) : undefined}
          clickable={!!onClickTag}
        />
      ))}

      {collapsed && (
        <button
          type="button"
          onClick={() => setExpanded(true)}
          className={`${chipClass} text-gray-500 hover:bg-gray-100`}
        >
          +{tags.length - maxVisible!}
        </button>
      )}

      {adding ? (
        <input
          ref={inputRef}
          className={`${chipClass} w-24 border border-indigo-300 outline-none focus:ring-1 focus:ring-indigo-300`}
          placeholder="New tag"
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          onBlur={closeInput}
          onKeyDown={(e) => {
            if (e.key === "Enter") addTag();
            if (e.key === "Escape") closeInput();
          }}
        />
      ) : (
        <button
          type="button"
          aria-label="Add tag"
          onClick={() => setAdding(true)}
          className={`${chipClass} border border-dashed border-gray-300 text-gray-400 hover:border-indigo-300 hover:text-indigo-600`}
        >
          <Plus className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}
