
import { ChartDataPoint } from "@/components/ChartCard";
import { Digest, Post, PostMetricsDataPoint } from "@/dto/BackendDataTypes";
import axios from "axios";

export class SMMetricsClient {

    baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    async listPosts(): Promise<Post[]> {
        const result = await axios
          .get<{ data: Post[] }>(`${this.baseUrl}/api/posts/posts`);
        return result.data;
    }

    async getPost(id: number): Promise<Post> {
        // http://127.0.0.1:8001
        const result = await axios
            .get<{ data: Post }>(`${this.baseUrl}/api/posts/post?id=${id}`, {
                mode: 'no-cors',
                headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
                },
            });
        return result.data;
    }

    async getPostMetrics(postId: number): Promise<PostMetricsDataPoint[]> {
        const result = await axios
        .get<{ data: PostMetricsDataPoint[] }>(`${this.baseUrl}/api/posts/metrics?id=${postId}`, {
            mode: 'no-cors',
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
            },
        });
        return result.data;
    }

    async getDigest(period: string): Promise<Digest> {
        const result = await axios
            .get<{ data: Digest }>(`${this.baseUrl}/api/reports/digest?period=${period}`);
        return result.data;
    }

    async getSubscribersCountHistory(period: string): Promise<ChartDataPoint[]> {
      const result = await axios
        .get<{ data: ChartDataPoint[] }>(`${this.baseUrl}/api/subscribers/count-over-time?period=${period}`, {
            mode: 'no-cors',
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
            },
        });
        return result.data.data;
    }

    async getTopPosts(): Promise<Post[]> {
        const result = await axios
          .get<{ data: Post[] }>(`${this.baseUrl}/api/reports/top`);
        return result.data;
    }
}