
import { ChartDataPoint } from "@/components/ChartCard";
import { Digest, Post, PostMetricsDataPoint, TagData } from "@/dto/BackendDataTypes";
import axios from "axios";

const HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
};

const CONFIG = {
    mode: 'no-cors',
    headers: HEADERS,
};

// todo: segregate?
// todo: /api part to "apiUrl"?
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
        const result = await axios
            .get<{ data: Post }>(`${this.baseUrl}/api/posts/post?id=${id}`, CONFIG);
        return result.data;
    }

    async getPostMetrics(postId: number): Promise<PostMetricsDataPoint[]> {
        const result = await axios
        .get<{ data: PostMetricsDataPoint[] }>(`${this.baseUrl}/api/posts/metrics?id=${postId}`, CONFIG);
        return result.data;
    }

    async getDigest(period: string): Promise<Digest> {
        const result = await axios
            .get<{ data: Digest }>(`${this.baseUrl}/api/reports/digest?period=${period}`);
        return result.data;
    }

    async getSubscribersCountHistory(period: string): Promise<ChartDataPoint[]> {
      const result = await axios
        .get<{ data: ChartDataPoint[] }>(`${this.baseUrl}/api/subscribers/count-over-time?period=${period}`, CONFIG);
        return result.data.data;
    }

    async getTopPosts(): Promise<Post[]> {
        const result = await axios
          .get<{ data: Post[] }>(`${this.baseUrl}/api/reports/top`);
        return result.data;
    }

    async getPostTitle(id: number): Promise<string> {
        const result = await axios
            .get<{ data: string }>(`${this.baseUrl}/api/posts/post_header?post_id=${id}`);
        return result.data;
    }

    async getPostTags(id: number): Promise<TagData[]> {
        const result = await axios
            .get<{ data: TagData[] }>(`${this.baseUrl}/api/posts/post_tags?post_id=${id}`);
        return result.data;
    }

    async updatePostTitle(postId: number, newTitle: string) {
        await axios.post(`${this.baseUrl}/api/posts/post_header?post_id=${postId}&title=${newTitle}`);
    }

    async addPostTag(postId: number, tag: string): Promise<TagData> {
        const result = await axios.post(`${this.baseUrl}/api/tags/add?post_id=${postId}&name=${tag}`);
        return result.data;
    }

    async deletePostTag(tagId: number) {
        await axios.delete(`${this.baseUrl}/api/tags/delete?tag_id=${tagId}`);
    }
}