import { Link } from "react-router-dom"

type SidebarProps = {
  open: boolean
}

// Docked column (not an overlay): when open it takes its own width, so page
// content sits beside it. Toggled by the floating button in App.
export default function Sidebar({ open }: SidebarProps) {
  if (!open) return null

  return (
    <aside className="sticky top-0 h-screen w-64 shrink-0 overflow-y-auto bg-gray-800 text-white">
      <div className="p-4 pl-16 flex items-center border-b border-gray-700 h-[3.75rem]">
        <h2 className="text-xl font-semibold">Menu</h2>
      </div>
      <nav className="p-4 space-y-3">
        <Link to="/summary" className="block hover:bg-gray-700 rounded px-3 py-2">
          Summary
        </Link>
        <Link to="/subscribers" className="block hover:bg-gray-700 rounded px-3 py-2">
          Subscribers
        </Link>
        <Link to="/subscriber-changes" className="block hover:bg-gray-700 rounded px-3 py-2">
          Subscriber Changes
        </Link>
        <Link to="/subscriber-lifecycle" className="block hover:bg-gray-700 rounded px-3 py-2">
          Subscriber Lifecycle
        </Link>
        <Link to="/reactions" className="block hover:bg-gray-700 rounded px-3 py-2">
          Reactions
        </Link>
        <Link to="/posts" className="block hover:bg-gray-700 rounded px-3 py-2">
          Posts
        </Link>
        <Link to="/tags" className="block hover:bg-gray-700 rounded px-3 py-2">
          Tags
        </Link>
        <Link to="/top" className="block hover:bg-gray-700 rounded px-3 py-2">
          Top
        </Link>
      </nav>
    </aside>
  )
}
