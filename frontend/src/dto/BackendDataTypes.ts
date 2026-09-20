
export interface Subscriber {
    user_id: number;
    username?: string;
    first_name?: string;
    last_name?: string;
    timestamp: string;
}

export interface SubscriberChanges {
    new: Subscriber[];
    removed: Subscriber[];
}

export interface SubscriberLifecycleEntry {
    user_id: number;
    username?: string;
    first_name?: string;
    last_name?: string;
    added: string;
    removed: string | null;
    duration_seconds: number;
}

export interface SubscriberLifecycle {
    past: SubscriberLifecycleEntry[];
    current: SubscriberLifecycleEntry[];
}

export interface TagData {
    id: number;
    name: string;
    probability?: number;
}

export interface Post {
    text: string;
    post_id: number;
    views?: number;
    reactions?: number;
    comments?: number;
    title?: string;
    tags?: TagData[];
}

export interface PostMetricsDataPoint {
    timestamp: string;
    views: number;
 }

export interface PostChange extends Post {
      views_old?: number;
      views_new?: number;
      views_diff?: number;
      reactions_old?: number;
      reactions_new?: number;
      reactions_diff?: number;
      comments_old?: number;
      comments_new?: number;
      comments_diff?: number;
      is_new?: boolean;
}

export interface SimilarPost extends Post {
    similarity: number;
}

export interface SimilarPosts {
    available: boolean;
    posts: SimilarPost[];
}

export interface Digest {
    period: string;
    subscribers: SubscriberChanges;
    posts: PostChange[];
    views_total: number;
    reactions_total: number;
    comments_total: number;
}

// export * as BackendDataTypes from './BackendDataTypes'