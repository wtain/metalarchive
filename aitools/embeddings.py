from sentence_transformers import SentenceTransformer

from aitools.common import clean_text

# Same multilingual model already used for tag extraction (aitools/tags.py) -
# proven to work well on the Russian post text this channel produces, and
# already cached locally, so no new model to download.
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSIONS = 384


class EmbeddingsExtractor:

    def __init__(self):
        self.model = None

    def _get_model(self):
        if self.model is None:
            self.model = SentenceTransformer(MODEL_NAME)
        return self.model

    def get_embedding(self, text):
        cleaned_text = clean_text(text)
        return self._get_model().encode(cleaned_text).tolist()
