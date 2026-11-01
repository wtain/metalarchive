import { useState } from "react"
import { NavLink } from "react-router-dom"
import { ChevronDown, ChevronRight } from "lucide-react"

type SidebarProps = {
  open: boolean
}

type NavItem = { label: string; to: string }
type NavGroup = { label: string; items: NavItem[] }

const HOME: NavItem = { label: "Summary", to: "/" }

const GROUPS: NavGroup[] = [
  {
    label: "Subscribers",
    items: [
      { label: "Overview", to: "/subscribers" },
      { label: "Changes", to: "/subscriber-changes" },
      { label: "Lifecycle", to: "/subscriber-lifecycle" },
    ],
  },
  {
    label: "Posts",
    items: [
      { label: "All", to: "/posts" },
      { label: "Reactions", to: "/reactions" },
      { label: "Tags", to: "/tags" },
      { label: "Top", to: "/top" },
    ],
  },
]

function itemClass({ isActive }: { isActive: boolean }, indent: string) {
  return `block rounded px-3 py-1.5 text-sm ${indent} ${
    isActive ? "bg-indigo-50 text-indigo-700 font-medium" : "text-gray-700 hover:bg-gray-100"
  }`
}

function Group({ group }: { group: NavGroup }) {
  const [expanded, setExpanded] = useState(true)
  const Chevron = expanded ? ChevronDown : ChevronRight

  return (
    <div>
      <button
        onClick={() => setExpanded((value) => !value)}
        aria-expanded={expanded}
        className="flex w-full items-center gap-1 rounded px-2 py-1.5 text-sm font-semibold text-gray-900 hover:bg-gray-100 focus:outline-none"
      >
        <Chevron size={16} className="text-gray-400" />
        {group.label}
      </button>
      {expanded && (
        <div className="ml-4 mt-0.5 space-y-0.5 border-l border-gray-200 pl-2">
          {group.items.map((item) => (
            <NavLink key={item.to} to={item.to} className={(state) => itemClass(state, "")}>
              {item.label}
            </NavLink>
          ))}
        </div>
      )}
    </div>
  )
}

// Docked column (not an overlay): when open it takes its own width, so page
// content sits beside it. Toggled by the floating button in App.
export default function Sidebar({ open }: SidebarProps) {
  if (!open) return null

  return (
    <aside className="sticky top-0 h-screen w-52 shrink-0 overflow-y-auto border-r border-gray-200 bg-white">
      <div className="p-4 pl-16 flex items-center border-b border-gray-200 h-[3.75rem]">
        <h2 className="text-lg font-semibold text-gray-900">Menu</h2>
      </div>
      <nav className="p-3 space-y-2">
        <NavLink to={HOME.to} end className={(state) => itemClass(state, "font-semibold")}>
          {HOME.label}
        </NavLink>
        {GROUPS.map((group) => (
          <Group key={group.label} group={group} />
        ))}
      </nav>
    </aside>
  )
}
