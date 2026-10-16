from aitools.tags import TagsExtractor


def test_get_tags_lemmatizes_inflected_nouns_to_normal_form():
    extractor = TagsExtractor()

    tags = dict(extractor.get_tags("Я зашёл на сайт банка и увидел страницу банка."))

    assert "банк" in tags
    assert "банка" not in tags


def test_get_tags_excludes_non_noun_words():
    extractor = TagsExtractor()

    tags = dict(extractor.get_tags("Он быстро и очень аккуратно открыл страницу вчера."))

    # "быстро" (adverb), "очень" (adverb), "аккуратно" (adverb), "вчера" (adverb),
    # "открыл" (verb), "и" (conjunction) should all be filtered - only the noun survives.
    assert set(tags.keys()) == {"страница"}


def test_get_tags_lowercases_foreign_tech_terms():
    extractor = TagsExtractor()

    tags = dict(extractor.get_tags("Мы обсудили PHP и Excel на созвоне."))

    assert "php" in tags
    assert "excel" in tags
    assert "PHP" not in tags
    assert "Excel" not in tags


def test_fit_corpus_downweights_terms_common_across_the_corpus():
    extractor = TagsExtractor()
    # "страница" appears in every document (uninformative); "банк" appears
    # only in the target document (distinctive) - same term frequency (1) in
    # the target text, so without IDF weighting they'd tie.
    extractor.fit_corpus([
        "Страница загружается медленно.",
        "Страница открылась быстро.",
        "Страница и банк - сайт банка открылся.",
    ])

    tags = extractor.get_tags("Страница и банк - сайт банка открылся.")
    ranked_lemmas = [lemma for lemma, _ in tags]

    assert ranked_lemmas.index("банк") < ranked_lemmas.index("страница")


def test_get_tags_respects_top_n():
    extractor = TagsExtractor()

    tags = extractor.get_tags(
        "Банк, страница, сервер, запрос, клиент, агент, процессор, память, файл, драйвер.",
        top_n=3,
    )

    assert len(tags) == 3


def test_get_tags_works_without_fit_corpus():
    extractor = TagsExtractor()

    tags = extractor.get_tags("Страница банка открылась быстро.")

    assert dict(tags).keys() == {"страница", "банк"}
