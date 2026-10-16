from storage_client.models import Post, PostTags


def test_tag_cloud_counts_posts_per_tag_ordered_descending(client, db_session):
    db_session.add_all([Post(id=1, text="A"), Post(id=2, text="B"), Post(id=3, text="C")])
    db_session.add_all([
        PostTags(post_id=1, name="thrash", probability=0.9),
        PostTags(post_id=2, name="thrash", probability=0.8),
        PostTags(post_id=3, name="doom", probability=0.7),
    ])
    db_session.commit()

    response = client.get("/api/tags/cloud")
    assert response.status_code == 200
    assert response.json() == [
        {"name": "thrash", "count": 2},
        {"name": "doom", "count": 1},
    ]


def test_tag_cloud_empty_when_no_tags(client, db_session):
    response = client.get("/api/tags/cloud")
    assert response.status_code == 200
    assert response.json() == []
