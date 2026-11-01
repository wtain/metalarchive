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
        group inline-flex items-center px-2 py-0.5
        text-xs rounded-full bg-gray-100 text-gray-700
        ${clickable ? "cursor-pointer hover:bg-indigo-50 hover:text-indigo-700" : ""}
      `}
    >
      {label}

      {onRemove && (
        // Takes no room until the tag is hovered (always shown on touch screens, which have no hover).
        <button
          type="button"
          aria-label={`Remove ${label}`}
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-0 max-w-0 overflow-hidden opacity-0 transition-all
            group-hover:ml-1 group-hover:max-w-4 group-hover:opacity-100
            focus-visible:ml-1 focus-visible:max-w-4 focus-visible:opacity-100
            [@media(hover:none)]:ml-1 [@media(hover:none)]:max-w-4 [@media(hover:none)]:opacity-100
            rounded-full hover:bg-gray-300"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </span>
  );
}
