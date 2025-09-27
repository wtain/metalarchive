import pandas as pd
import ast

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

    # Fill NAs
    old = old.fillna({"views": 0, "forwards": 0, "comments": 0, "reactions": ""})
    new = new.fillna({"views": 0, "forwards": 0, "comments": 0, "reactions": ""})

    # Ensure numeric types
    for col in ["views", "forwards", "comments"]:
        old[col] = old[col].astype(int)
        new[col] = new[col].astype(int)

    # --- MERGE on message_id, keep all posts ---
    merged = pd.merge(
        old, new,
        on="message_id", how="outer",
        suffixes=("_old", "_new")
    )

    # Fill missing (new posts won't exist in old)
    merged = merged.fillna({
        "views_old": 0,
        "forwards_old": 0,
        "comments_old": 0,
        "reactions_old": "",
        "text_excerpt_old": "",
    })

    # --- Views/Forwards Report ---
    merged["views_diff"] = merged["views_new"] - merged["views_old"]
    merged["forwards_diff"] = merged["forwards_new"] - merged["forwards_old"]
    merged["comments_diff"] = merged["comments_new"] - merged["comments_old"]

    views_report = merged[[
        "message_id", "text_excerpt_new", "views_old", "views_new", "views_diff",
        "forwards_old", "forwards_new", "forwards_diff",
        "comments_old", "comments_new", "comments_diff"
    ]].rename(columns={"text_excerpt_new": "text_excerpt"})

    # --- Reactions Report ---
    def parse_reactions(val):
        try:
            return ast.literal_eval(val) if val else {}
        except Exception:
            return {}

    merged["reactions_old_parsed"] = merged["reactions_old"].apply(parse_reactions)
    merged["reactions_new_parsed"] = merged["reactions_new"].apply(parse_reactions)

    reactions_changes = []
    for _, row in merged.iterrows():
        old_r = row["reactions_old_parsed"]
        new_r = row["reactions_new_parsed"]

        # Compare counts for each emoji
        diffs = {}
        for key in set(old_r.keys()) | set(new_r.keys()):
            old_val = old_r.get(key, 0)
            new_val = new_r.get(key, 0)
            if old_val != new_val:
                diffs[key] = new_val - old_val

        if diffs:
            reactions_changes.append({
                "message_id": row["message_id"],
                "text_excerpt": row["text_excerpt_new"],
                "reactions_diff": diffs
            })

    reactions_report = pd.DataFrame(reactions_changes)

    return views_report, reactions_report

# Example usage:
# joined, left = compare_subscribers("subscribers_20250914_093000.csv", "subscribers_20250915_093000.csv")
# print("New subscribers:\n", joined)
# print("Unsubscribed:\n", left)

# post_changes = compare_posts("posts_20250914_093000.csv", "posts_20250915_093000.csv")
# print(post_changes)

# views_report, reactions_report = compare_posts("results/posts/posts_20250919_173327.csv", "results/posts/posts_20250919_212502.csv")
# print(views_report)
# print(reactions_report)

# Save reports as CSV
# views_report.to_csv("results/reports/diff_posts_views-20250919_173327-20250919_212502.csv", index=False, encoding="utf-8")
# reactions_report.to_csv("results/reports/diff_posts_reactions-20250919_173327-20250919_212502.csv", index=False, encoding="utf-8")

joined, left = compare_subscribers("results/subscribers/subscribers_20250926_111348.csv",
                                   "results/subscribers/subscribers_20250926_143710.csv")
print("New subscribers:\n", joined)
print("Unsubscribed:\n", left)