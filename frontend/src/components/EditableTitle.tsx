import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { SMMetricsClient } from "@/client/SMMetricsClient";

interface EditableTitleProps {
  postId: number;
  initialTitle: string;
  client: SMMetricsClient;
}

// todo: to utils
const useFocus = () => {
    const htmlElRef = useRef<HTMLInputElement>(null)
    const setFocus = () => {
        if (htmlElRef.current) {
            htmlElRef.current.focus();
            htmlElRef.current.select();
        }
    }

    return [ htmlElRef, setFocus ] 
}

export default function EditableTitle({ postId, initialTitle, client }: EditableTitleProps) {
  const [title, setTitle] = useState<string>(initialTitle);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [inputRef, setInputFocus] = useFocus()

  useEffect(() => {
    setTitle(initialTitle);
  }, [initialTitle]);

  useEffect(() => {
    if (isEdit) {
        setInputFocus();
    }
  }, [isEdit]); 

  const saveTitle = async () => {
    setSaving(true);
    try {
      await client.updatePostTitle(postId, encodeURIComponent(title));
      setSaved(true);
      setTimeout(() => setSaved(false), 1500);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
        {isEdit ? 
            <div>
                <Input
                    ref={inputRef}
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            saveTitle();
                            setIsEdit(false);
                        }
                        if (e.key === "Escape") {
                            setIsEdit(false);
                        }
                    }}
                    className="max-w-md"
                />

                <Button onClick={saveTitle} disabled={saving}>
                    {saving ? "Saving..." : saved ? "Saved!" : "Save"}
                </Button>
            </div>
            : 
            <div onClick={() => {
                    // console.log(title);
                    setIsEdit(true);
                }}>
                {title}
            </div>
        }
    </div>
  );
}
