import React, { useEffect, useState } from "react";
import axios from "axios";
import ChartCard, { ChartDataPoint } from "../components/ChartCard";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import PeriodSelector, { Period } from "../components/PeriodSelector";
import { Button } from "@/components/ui/button"
import MetricDisplay from "../components/MetricDisplay"
import { useNavigate } from "react-router-dom";

interface Subscriber {
}

interface SubscriberChanges {
    new: Subscriber[];
    removed: Subscriber[];
}

interface PostChange {
      text: string;
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

  const navigate = useNavigate();

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
                <p className="text-sm text-black-500 mb-2">{d.text.substring(0, 200)}...</p>
                <p className="text-sm font-bold text-gray-500 mb-2">Views</p>
                <MetricDisplay value={d.views_new} valueDiff={d.views_diff} />
                <p className="text-sm font-bold text-gray-500 mb-2">Reactions</p>
                <MetricDisplay value={d.reactions_new} valueDiff={d.reactions_diff} />
                <p className="text-sm font-bold text-gray-500 mb-2">Comments</p>
                <MetricDisplay value={d.comments_new} valueDiff={d.comments_diff} />
                <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white" onClick={
                () => {
                    navigate(`/posts/${d.post_id}`);
                }
                }>View Details</Button>
              </CardContent>
            </Card>
          )
      }
      </main>
    </div>
  );
}
