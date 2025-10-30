
interface Subscriber {
}

interface SubscriberChanges {
    new: Subscriber[];
    removed: Subscriber[];
}

interface Post {
      text: string;
      post_id: number;
}

interface PostChange extends Post {
      views_old?: number;
      views_new?: number;
      views_diff?: number;
      reactions_old?: number;
      reactions_new?: number;
      reactions_diff?: number;
      comments_old?: number;
      comments_new?: number;
      comments_diff?: number;
}

interface Digest {
    period: string;
    subscribers: SubscriberChanges;
    posts: PostChange[];
}
