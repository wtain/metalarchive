import { useEffect, useState } from "react"
import { Menu } from "lucide-react"
import Navbar from "@/components/Navbar"
import Sidebar from "@/components/Sidebar"
import { Outlet } from "react-router-dom"

const SIDEBAR_STORAGE_KEY = "sidebarOpen"

function loadSidebarOpen(): boolean {
  try {
    return localStorage.getItem(SIDEBAR_STORAGE_KEY) !== "false"
  } catch {
    return true
  }
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(loadSidebarOpen)

  useEffect(() => {
    try {
      localStorage.setItem(SIDEBAR_STORAGE_KEY, String(sidebarOpen))
    } catch {
      // storage unavailable: the choice just won't persist
    }
  }, [sidebarOpen])

  return (
    <div className="min-h-screen flex bg-gray-50">
      <button
        onClick={() => setSidebarOpen((open) => !open)}
        aria-label={sidebarOpen ? "Hide menu" : "Show menu"}
        className={`fixed top-3 left-4 z-50 rounded-md p-2 focus:outline-none ${
          sidebarOpen ? "text-gray-300 hover:text-white hover:bg-gray-700" : "text-gray-600 hover:text-indigo-600 hover:bg-gray-100"
        }`}
      >
        <Menu size={24} />
      </button>

      <Sidebar open={sidebarOpen} />

      <div className="flex-1 min-w-0 flex flex-col">
        <Navbar sidebarOpen={sidebarOpen} />

        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default App
