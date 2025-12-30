from aitools.common import clean_text
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer


class TagsExtractor:

    def __init__(self):
        self.kw_model = None

    def _get_kw_model(self):
        if self.kw_model is None:
            model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.kw_model = KeyBERT(model)
        return self.kw_model

    def get_tags(self, text):

        cleaned_text = clean_text(text)

        text = cleaned_text

        keywords = self._get_kw_model().extract_keywords(
            text,
            keyphrase_ngram_range=(1, 1),

            use_mmr=True,
            diversity=0.7,

            top_n=10
        )

        return keywords
