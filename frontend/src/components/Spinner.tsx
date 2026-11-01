import React from "react";
import { LoaderCircle } from "lucide-react";

// Shown while a page's data is still on its way, as opposed to the "nothing
// here" text for data that arrived empty.
export default function Spinner({ size = 32 }: { size?: number }) {
  return (
    <div role="status" aria-label="Loading" className="flex justify-center py-12 text-indigo-500">
      <LoaderCircle size={size} className="animate-spin" />
    </div>
  );
}
