import re
from unicodedata import normalize

import ctranslate2
from ipa_uk import ipa
from transformers import M2M100Tokenizer
from ukrainian_word_stress import StressSymbol, Stressifier

from common import MODELS

stressify = Stressifier()
translator = ctranslate2.Translator(str(MODELS / "verbalizer-ct2"), device="cpu", compute_type="int8")
tokenizer = M2M100Tokenizer.from_pretrained(MODELS / "verbalizer-tokenizer")
tokenizer.src_lang = "uk"


def verbalize(text):
    """Numbers and abbreviations to words, e.g. "250" -> "двісті п'ятдесят"."""
    source = tokenizer.convert_ids_to_tokens(tokenizer.encode(text))
    result = translator.translate_batch([source], target_prefix=[[tokenizer.lang_code_to_token["uk"]]], beam_size=1)
    return tokenizer.decode(tokenizer.convert_tokens_to_ids(result[0].hypotheses[0][1:]))


# Mirrors the preprocessing in the patriotyk/styletts2-ukrainian HF space; "+" after a vowel forces stress.
def phonemize(text):
    if re.search(r"\d", text):
        text = verbalize(text)
    text = normalize("NFKC", text.replace('"', "").replace("+", StressSymbol.CombiningAcuteAccent))
    text = re.sub(r"[᠆‐‑‒–—―⁻₋−⸺⸻]", "-", text).strip()
    if text[-1] not in ".?!:-":
        text += "."
    return ipa(stressify(re.sub(r" - ", ": ", text)))
