from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from aitools.common import clean_text

model_name = "cointegrated/rut5-base-multitask"


class TitleExtractor:

    def __init__(self):
        # 1. Load Russian summarization model (RuT5 multitask)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def get_title(self, text):

        cleaned_text = clean_text(text)

        input_text = f"headline: {cleaned_text}"

        # 5. Tokenize and generate title
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = self.model.generate(
            **inputs,
            max_new_tokens=50,  # length of the title
            num_beams=4,  # beam search for quality
            no_repeat_ngram_size=2  # avoid repeating phrases
        )

        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
