import re
from collections import Counter
from math import log

from natasha import Doc, MorphVocab, NewsEmbedding, NewsMorphTagger, Segmenter

from aitools.common import clean_text

# NOUN/PROPN cover Russian content words once lemmatized; X ("foreign/unanalyzed")
# is included because this channel's text is full of untranslated English tech
# terms (php, mcp, github) that Natasha can't assign a Russian POS to - dropping
# them would throw away exactly the tags that read as most relevant. Natasha's
# lemmatizer still normalizes X tokens (just lowercases them), which is enough.
RELEVANT_POS = {"NOUN", "PROPN", "X"}
MIN_TOKEN_LENGTH = 3
HAS_LETTER = re.compile(r"[a-zA-Zа-яёА-ЯЁ]")


class TagsExtractor:

    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self._morph_tagger = None
        self.doc_frequencies = Counter()
        self.corpus_size = 0

    def _get_morph_tagger(self):
        if self._morph_tagger is None:
            self._morph_tagger = NewsMorphTagger(NewsEmbedding())
        return self._morph_tagger

    def _lemmatize_candidates(self, text):
        doc = Doc(clean_text(text))
        doc.segment(self.segmenter)
        doc.tag_morph(self._get_morph_tagger())

        lemmas = []
        for token in doc.tokens:
            if token.pos not in RELEVANT_POS:
                continue
            if len(token.text) < MIN_TOKEN_LENGTH or not HAS_LETTER.search(token.text):
                continue
            token.lemmatize(self.morph_vocab)
            lemmas.append(token.lemma)
        return lemmas

    def fit_corpus(self, texts):
        """Computes document frequencies for IDF weighting over a batch of posts.
        Call once before get_tags() for that batch - without it, every lemma gets
        the same IDF weight and ranking falls back to plain term frequency."""
        self.doc_frequencies = Counter()
        self.corpus_size = 0
        for text in texts:
            if not text:
                continue
            self.corpus_size += 1
            self.doc_frequencies.update(set(self._lemmatize_candidates(text)))

    def get_tags(self, text, top_n=7):
        term_frequencies = Counter(self._lemmatize_candidates(text))

        def score(lemma, term_frequency):
            document_frequency = self.doc_frequencies.get(lemma, 0) + 1
            inverse_document_frequency = log((self.corpus_size + 1) / document_frequency) + 1
            return term_frequency * inverse_document_frequency

        scored = [(lemma, score(lemma, tf)) for lemma, tf in term_frequencies.items()]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_n]
