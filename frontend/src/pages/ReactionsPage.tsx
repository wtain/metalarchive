import React, { useEffect, useState } from "react";
import axios from "axios";
import ChartCard, { ChartDataPoint } from "../components/ChartCard";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import PeriodSelector, { Period } from "../components/PeriodSelector";
import { Button } from "@/components/ui/button"

interface Subscriber {
}

interface SubscriberChanges {
    new: Subscriber[];
    removed: Subscriber[];
}

interface PostChange {
      post_id: number;
      views_old: number;
      views_new: number;
      views_diff: number;
      reactions_old: number;
      reactions_new: number;
      reactions_diff: number;
      comments_old: number;
      comments_new: number;
      comments_diff: number;
}

interface Digest {
    period: string;
    subscribers: SubscriberChanges;
    posts: PostChange[];
}

export default function ReactionsPage() {
  const [period, setPeriod] = useState<Period>("daily");
  const [data, setData] = useState<Digest>({posts: []});

  useEffect(() => {
    axios
      .get<{ data: ChartDataPoint[] }>(`http://127.0.0.1:8001/api/reports/digest?period=${period}`)
      .then((res) => setData(res.data))
      .catch(console.error);
  }, [period]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Reactions</h1>
      <PeriodSelector value={period} onChange={setPeriod} />
      <main className="flex-1 container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {
          data.posts.map(d =>
            <Card className="shadow-md hover:shadow-lg transition" key={d.post_id}>
              <CardHeader>
                <CardTitle>{d.post_id}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500 mb-2">Views</p>
                <div className="text-3xl font-bold text-green-600">{d.views_new} (+{d.views_diff})</div>
                <p className="text-sm text-gray-500 mb-2">Reactions</p>
                <div className="text-3xl font-bold text-green-600">{d.reactions_new} (+{d.reactions_diff})</div>
                <p className="text-sm text-gray-500 mb-2">Comments</p>
                <div className="text-3xl font-bold text-green-600">{d.comments_new} (+{d.comments_diff})</div>
              </CardContent>
            </Card>
          )
      }
      </main>
    </div>
  );
}
