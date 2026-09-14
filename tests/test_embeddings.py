import pytest

from aitools.embeddings import EmbeddingsExtractor, EMBEDDING_DIMENSIONS

pytestmark = pytest.mark.integration


def test_get_embedding_returns_expected_dimension_for_russian_text():
    extractor = EmbeddingsExtractor()

    embedding = extractor.get_embedding("Новый пост про технологии и разработку программного обеспечения.")

    assert len(embedding) == EMBEDDING_DIMENSIONS
    assert all(isinstance(value, float) for value in embedding)
    assert any(value != 0.0 for value in embedding)


def test_similar_russian_texts_are_closer_than_unrelated_ones():
    extractor = EmbeddingsExtractor()

    def cosine_similarity(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        return dot / (norm_a * norm_b)

    post_a = extractor.get_embedding("Обновил себе компьютер, заменил оперативную память и процессор.")
    post_b = extractor.get_embedding("Собрал новый игровой ПК с современным железом.")
    post_c = extractor.get_embedding("Сегодня прекрасная погода для прогулки в парке с собакой.")

    assert cosine_similarity(post_a, post_b) > cosine_similarity(post_a, post_c)
