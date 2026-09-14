from storage_client.models import BatchRun, Post, PostEmbedding, PostHeader, PostMetric, PostTags


def make_vector(first, filler=0.0):
    vector = [filler] * 384
    vector[0] = first
    return vector


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


def test_similar_posts_orders_by_cosine_similarity_and_hydrates_title(client, db_session):
    db_session.add_all([
        Post(id=1, text="Target post"),
        Post(id=2, text="Close post"),
        Post(id=3, text="Far post"),
    ])
    db_session.add(PostHeader(post_id=2, title="Close Title"))
    db_session.add(PostEmbedding(post_id=1, model_name="m", embedding=make_vector(1.0)))
    db_session.add(PostEmbedding(post_id=2, model_name="m", embedding=make_vector(0.9, filler=0.01)))
    db_session.add(PostEmbedding(post_id=3, model_name="m", embedding=make_vector(-1.0)))
    db_session.commit()

    response = client.get("/api/posts/similar?post_id=1")
    assert response.status_code == 200
    data = response.json()

    assert data["available"] is True
    assert [p["post_id"] for p in data["posts"]] == [2, 3]
    assert data["posts"][0]["title"] == "Close Title"
    assert data["posts"][0]["similarity"] > data["posts"][1]["similarity"]


def test_similar_posts_excludes_target_and_respects_limit(client, db_session):
    db_session.add(Post(id=1, text="Target"))
    db_session.add(PostEmbedding(post_id=1, model_name="m", embedding=make_vector(1.0)))
    for i in range(2, 8):
        db_session.add(Post(id=i, text=f"Post {i}"))
        db_session.add(PostEmbedding(post_id=i, model_name="m", embedding=make_vector(0.5)))
    db_session.commit()

    response = client.get("/api/posts/similar?post_id=1&limit=3")
    data = response.json()

    assert data["available"] is True
    assert len(data["posts"]) == 3
    assert all(p["post_id"] != 1 for p in data["posts"])


def test_similar_posts_unavailable_without_embedding(client, db_session):
    db_session.add(Post(id=1, text="No embedding yet"))
    db_session.commit()

    response = client.get("/api/posts/similar?post_id=1")
    assert response.status_code == 200
    assert response.json() == {"available": False, "posts": []}
