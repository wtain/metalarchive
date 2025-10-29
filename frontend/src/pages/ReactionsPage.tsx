import React, { useEffect, useState } from "react";
import axios from "axios";
import ChartCard, { ChartDataPoint } from "../components/ChartCard";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import PeriodSelector, { Period } from "../components/PeriodSelector";
import PostCard from "../components/PostCard";
import { Button } from "@/components/ui/button"
import MetricDisplay from "../components/MetricDisplay"
import { useNavigate } from "react-router-dom";
import { Subscriber, SubscriberChanges, PostChange, Digest } from "../dto/BackendDataTypes";

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
          data.posts.map(post =>
            <PostCard post={post} key={post.post_id} />
          )
      }
      </main>
    </div>
  );
}
