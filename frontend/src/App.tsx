import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

type Change = { date: string; added: number; removed: number }

function App() {
  const [data, setData] = useState<Change[]>([])

  useEffect(() => {
    // Example API fetch
    fetch("/api/subscribers/daily")
      .then((res) => res.json())
      .then((d) => setData(d))
      .catch(() => setData([]))
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow p-4">
        <h1 className="text-2xl font-bold text-indigo-600">Subscribers Dashboard</h1>
      </header>

      <main className="flex-1 container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="shadow-md hover:shadow-lg transition">
          <CardHeader>
            <CardTitle>Subscribers Change</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500 mb-2">Last 7 days</p>
            <div className="text-3xl font-bold text-green-600">+152</div>
          </CardContent>
        </Card>

        <Card className="shadow-md hover:shadow-lg transition">
          <CardHeader>
            <CardTitle>Reactions Change</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500 mb-2">Last 7 days</p>
            <div className="text-3xl font-bold text-blue-600">+87</div>
          </CardContent>
        </Card>

        <Card className="shadow-md hover:shadow-lg transition">
          <CardHeader>
            <CardTitle>Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">View Details</Button>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

export default App
