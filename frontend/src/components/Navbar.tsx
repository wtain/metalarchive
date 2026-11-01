type NavbarProps = {
  sidebarOpen: boolean
}

export default function Navbar({ sidebarOpen }: NavbarProps) {
  return (
    // Left padding leaves room for App's floating menu button when the
    // sidebar is hidden (when shown, the button sits over the sidebar header).
    <header className={`bg-white shadow p-4 flex items-center gap-4 ${sidebarOpen ? "" : "pl-16"}`}>
      <h1 className="text-2xl font-bold text-indigo-600">Dashboard</h1>
    </header>
  )
}
