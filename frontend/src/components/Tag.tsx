import { X } from "lucide-react";
import type { CSSProperties } from "react";

export interface TagProps {
  label: string;
  onRemove?: () => void;
  onClick?: () => void;
  clickable?: boolean;
  style?: CSSProperties;
}

export default function Tag({ label, onRemove, onClick, clickable, style }: TagProps) {
  return (
    <span
      onClick={onClick}
      style={style}
      className={`
        inline-flex items-center gap-1 px-2 py-1
        text-sm rounded-full border border-gray-300
        bg-gray-100 text-gray-800
        ${clickable ? "cursor-pointer hover:bg-gray-200" : ""}
      `}
    >
      {label}

      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-1 rounded-full hover:bg-gray-300 p-0.5"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </span>
  );
}
