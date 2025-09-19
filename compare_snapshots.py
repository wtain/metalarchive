import pandas as pd

def compare_subscribers(old_file, new_file):
    old = pd.read_csv(old_file, dtype=str)
    new = pd.read_csv(new_file, dtype=str)

    old_ids = set(old["user_id"])
    new_ids = set(new["user_id"])

    joined = new[new["user_id"].isin(new_ids - old_ids)]
    left = old[old["user_id"].isin(old_ids - new_ids)]

    return joined, left

def compare_posts(old_file, new_file):
    old = pd.read_csv(old_file)
    new = pd.read_csv(new_file)

    # Merge by message_id
    merged = pd.merge(old, new, on="message_id", suffixes=("_old", "_new"))

    merged["views_diff"] = merged["views_new"] - merged["views_old"]
    merged["forwards_diff"] = merged["forwards_new"] - merged["forwards_old"]
    merged["reactions_diff"] = merged["reactions_new"].astype(str) != merged["reactions_old"].astype(str)

    return merged[["message_id", "text_excerpt_old", "views_diff", "forwards_diff", "reactions_diff"]]

# Example usage:
# joined, left = compare_subscribers("subscribers_20250914_093000.csv", "subscribers_20250915_093000.csv")
# print("New subscribers:\n", joined)
# print("Unsubscribed:\n", left)

# post_changes = compare_posts("posts_20250914_093000.csv", "posts_20250915_093000.csv")
# print(post_changes)

post_changes = compare_posts("posts_20250919_173327.csv", "posts_20250919_212502.csv")
print(post_changes)

joined, left = compare_subscribers("subscribers_20250919_173327.csv", "subscribers_20250920_014518.csv")
print("New subscribers:\n", joined)
print("Unsubscribed:\n", left)