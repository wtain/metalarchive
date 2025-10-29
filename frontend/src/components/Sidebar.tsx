import { Link } from "react-router-dom"

type SidebarProps = {
  open: boolean
  onClose: () => void
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <div
      className={`fixed top-0 left-0 h-full bg-gray-800 text-white w-64 transform ${
        open ? "translate-x-0" : "-translate-x-full"
      } transition-transform duration-300 ease-in-out z-50`}
    >
      <div className="p-4 flex justify-between items-center border-b border-gray-700">
        <h2 className="text-xl font-semibold">Menu</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white focus:outline-none"
        >
          ✕
        </button>
      </div>
      <nav className="p-4 space-y-3">
        <Link to="/subscribers" className="block hover:bg-gray-700 rounded px-3 py-2" onClick={onClose}>
          Subscribers
        </Link>
        <Link to="/reactions" className="block hover:bg-gray-700 rounded px-3 py-2" onClick={onClose}>
          Reactions
        </Link>
      </nav>
    </div>
  )
}
