
import re


def clean_text(text):
    cleaned_text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text
