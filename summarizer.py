from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from keyphrasetransformer import KeyPhraseTransformer

kp = KeyPhraseTransformer()

# 1. Load Russian summarization model (RuT5 multitask)
model_name = "cointegrated/rut5-base-multitask"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 2. Example post text (replace with your content)
# text = """
# 🚀 Сегодня я расскажу, как ускорить сборку Docker образов в CI/CD.
# Мы рассмотрим кеширование, multi-stage сборку и оптимизацию слоёв.
# С примерами на GitHub Actions и GitLab.
# Подробнее: [ссылка]
# """

text = """
Интервью - это всегда стресс для кандидата. Конечно: от его результата зависит будущее. И не всегда просто произвести хорошее впечатление на интервьювера за час разговора. Но это ещё и стресс для самого интервьювера, даже достаточно опытного. Иногда, когда задаёшь вопрос кандидату, а ответ звучит нерелевантным, кажется, что это я чего-то не понимаю, а не то, что кандидат просто не отвечает на поставленный вопрос, или не понял его. Например, спрашиваешь человека про пример ситуации из опыта, а он начинает описывать гипотетическую ситуацию. Или спрашиваешь, какой урок человек вынес из данной истории - а в ответ получаешь список технологий, с которыми он поработал. После такого, анализируя интервью, в следующий раз стараешься формулировать вопросы более чётко, но это не всегда помогает - потому, что проблема далеко не всегда в вопросе. Иногда просто надо принять факт, что кандидаты тоже люди и могут не понять вопрос и постесняться уточнить, или сразу начать отвечать заготовленной историей, которая не совсем соотносится с заданным вопросом. Поговорил с коллегами - у них такое тоже бывает. А у вас бывают такие мысли? Как справляетесь?
"""

# 3. Preprocess: remove markdown-like links (simple regex) and extra spaces
import re
clean_text = re.sub(r'\[.*?\]\(.*?\)', '', text)
clean_text = re.sub(r'\s+', ' ', clean_text).strip()

# 4. Prepare input for RuT5 (it expects a task prefix)
# input_text = f"суммаризировать: {clean_text}"
input_text = f"headline: {clean_text}"

# 5. Tokenize and generate title
inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
summary_ids = model.generate(
    **inputs,
    max_new_tokens=50,     # length of the title
    num_beams=4,           # beam search for quality
    no_repeat_ngram_size=2 # avoid repeating phrases
)

title = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
print("Generated title:", title)

######

# Clean markdown links
# text_clean = re.sub(r'\[.*?\]\(.*?\)', '', text).strip()
#
# input_text = f"keywords: {text_clean}"
#
# inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
#
# summary_ids = model.generate(
#     **inputs,
#     max_new_tokens=40,
#     num_beams=4,
#     no_repeat_ngram_size=2
# )
#
# keywords = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
# print("Extracted tags:", keywords)

# import nltk
# nltk.download('punkt_tab')
#
# tags = kp.get_key_phrases(clean_text)
# print("Tags: ", tags)


from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# Russian embedding model (high quality)
# model = SentenceTransformer('cointegrated/rubert-tiny2')
# model = SentenceTransformer('cointegrated/rubert-tiny2')
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
kw_model = KeyBERT(model)

# text = """
# Сегодня разбираемся, как оптимизировать FastAPI приложение на проде.
# Говорим про middlewares, профилирование, кэширование и работу с asyncio.
# """

text = clean_text

keywords = kw_model.extract_keywords(
    text,
    # keyphrase_ngram_range=(1, 2),
    keyphrase_ngram_range=(1, 1),
    # stop_words='russian',

    use_mmr=True,
    diversity=0.7,

    top_n=10
)

print(keywords)
