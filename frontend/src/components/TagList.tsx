import Tag from "./Tag";

export interface TagListProps {
  tags: string[];
  onRemoveTag?: (tag: string) => void;
  onClickTag?: (tag: string) => void;
}

export default function TagList({ tags, onRemoveTag, onClickTag }: TagListProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <Tag
          key={tag}
          label={tag}
          clickable={!!onClickTag}
          onRemove={onRemoveTag ? () => onRemoveTag(tag) : undefined}
          onClick={onClickTag ? () => onClickTag(tag) : undefined}
        />
      ))}
    </div>
  );
}
