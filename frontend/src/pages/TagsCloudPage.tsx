import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Tag from "../components/Tag";
import { TagCloudEntry } from "../dto/BackendDataTypes";
import { BasePageProperties } from "@/utils/BasePageProperties";

const MIN_FONT_SIZE = 14;
const MAX_FONT_SIZE = 40;

function fontSizeFor(count: number, minCount: number, maxCount: number): number {
    if (maxCount === minCount) {
        return (MIN_FONT_SIZE + MAX_FONT_SIZE) / 2;
    }
    const ratio = (count - minCount) / (maxCount - minCount);
    return MIN_FONT_SIZE + ratio * (MAX_FONT_SIZE - MIN_FONT_SIZE);
}

export default function TagsCloudPage(props: BasePageProperties) {

    const [tags, setTags] = useState<TagCloudEntry[] | null>(null);
    const navigate = useNavigate();

    const client = props.metricsClient;

    useEffect(() => {
        client
            .getTagCloud()
            .then((tags) => setTags(tags));
    }, []);

    if (tags === null) {
        return <div>Loading...</div>;
    }

    if (tags.length === 0) {
        return (
            <div>
                <h1 className="text-2xl font-bold mb-4">Tags</h1>
                <p className="text-gray-500">No tags yet.</p>
            </div>
        );
    }

    const counts = tags.map((t) => t.count);
    const minCount = Math.min(...counts);
    const maxCount = Math.max(...counts);

    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Tags</h1>
            <div className="flex flex-wrap items-center gap-3">
                {tags.map((tag) => (
                    <Tag
                        key={tag.name}
                        label={`${tag.name} (${tag.count})`}
                        clickable
                        onClick={() => navigate(`/search?tag=${encodeURIComponent(tag.name)}`)}
                        style={{ fontSize: fontSizeFor(tag.count, minCount, maxCount) }}
                    />
                ))}
            </div>
        </div>
    );
}
