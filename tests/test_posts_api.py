from storage_client.models import BatchRun, Post, PostHeader, PostMetric, PostTags


def test_list_posts_includes_hydrated_title_tags_and_latest_metrics(client, db_session):
    db_session.add(BatchRun(id=1))
    db_session.add(Post(id=1, text="Hello world"))
    db_session.add(PostHeader(post_id=1, title="Hello Title"))
    db_session.add(PostTags(post_id=1, name="python", probability=0.9))
    db_session.add(PostMetric(post_id=1, run_id=1, views=10, reactions=2, comments=1))
    db_session.commit()

    response = client.get("/api/posts/posts")
    assert response.status_code == 200

    posts = response.json()
    assert len(posts) == 1
    post = posts[0]
    assert post["post_id"] == 1
    assert post["title"] == "Hello Title"
    assert post["tags"] == [{"id": 1, "name": "python", "probability": 0.9}]
    assert post["views"] == 10
    assert post["reactions"] == 2
    assert post["comments"] == 1


def test_list_posts_without_header_or_metrics_defaults_gracefully(client, db_session):
    db_session.add(Post(id=2, text="No header yet"))
    db_session.commit()

    response = client.get("/api/posts/posts")
    assert response.status_code == 200

    post = response.json()[0]
    assert post["title"] is None
    assert post["tags"] == []
    assert post["views"] is None


def test_list_posts_only_uses_metrics_from_latest_run(client, db_session):
    db_session.add_all([BatchRun(id=1), BatchRun(id=2)])
    db_session.add(Post(id=1, text="Hello"))
    db_session.add(PostMetric(post_id=1, run_id=1, views=10, reactions=1, comments=0))
    db_session.add(PostMetric(post_id=1, run_id=2, views=50, reactions=3, comments=1))
    db_session.commit()

    response = client.get("/api/posts/posts")
    post = response.json()[0]

    assert post["views"] == 50
    assert post["reactions"] == 3
