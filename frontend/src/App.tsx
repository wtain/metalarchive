import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface AppProps {
  children: React.ReactNode;
}

type Change = { date: string; added: number; removed: number }

function App({ children }: AppProps) {

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow p-4">
        <h1 className="text-2xl font-bold text-indigo-600">Subscribers Dashboard</h1>
      </header>

      <main className="flex-1 container mx-auto p-6">{children}</main>
    </div>
  )
}

export default App
