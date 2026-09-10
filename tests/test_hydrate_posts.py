from storage_client.models import Post, PostHeader, PostTags
from storage_client.posts import fetch_titles_and_tags, hydrate_posts


def test_fetch_titles_and_tags_groups_tags_by_post(db_session):
    db_session.add_all([
        Post(id=1, text="a"),
        Post(id=2, text="b"),
        PostHeader(post_id=1, title="Title 1"),
        PostTags(post_id=1, name="tag-a", probability=0.5),
        PostTags(post_id=1, name="tag-b", probability=0.4),
    ])
    db_session.commit()

    details = fetch_titles_and_tags(db_session, [1, 2])

    assert details[1]["title"] == "Title 1"
    assert {tag["name"] for tag in details[1]["tags"]} == {"tag-a", "tag-b"}
    assert details[2] == {"title": None, "tags": []}


def test_fetch_titles_and_tags_empty_input_returns_empty_dict(db_session):
    assert fetch_titles_and_tags(db_session, []) == {}


def test_hydrate_posts_attaches_title_and_tags_in_place(db_session):
    db_session.add_all([Post(id=1, text="a"), PostHeader(post_id=1, title="T")])
    db_session.commit()

    posts = [{"post_id": 1, "text": "a"}]
    result = hydrate_posts(db_session, posts)

    assert result is posts
    assert posts[0]["title"] == "T"
    assert posts[0]["tags"] == []


def test_hydrate_posts_defaults_for_post_with_no_header_or_tags(db_session):
    posts = [{"post_id": 999, "text": "orphan"}]

    hydrate_posts(db_session, posts)

    assert posts[0]["title"] is None
    assert posts[0]["tags"] == []
