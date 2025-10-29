import { Menu } from "lucide-react"

type NavbarProps = {
  onMenuClick: () => void
}

export default function Navbar({ onMenuClick }: NavbarProps) {
  return (
    <header className="bg-white shadow p-4 flex items-center gap-4">
      <button
        onClick={onMenuClick}
        className="text-gray-600 hover:text-indigo-600 focus:outline-none"
      >
        <Menu size={24} />
      </button>
      <h1 className="text-2xl font-bold text-indigo-600">Dashboard</h1>
    </header>
  )
}
