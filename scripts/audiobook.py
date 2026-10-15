# /// script
# requires-python = ">=3.10"
# dependencies = ["soundfile", "numpy"]
# ///
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SENTENCE_PAUSE, PARAGRAPH_PAUSE = 0.35, 0.9


def trim(audio, threshold=0.01):
    loud = np.flatnonzero(np.abs(audio) > threshold)
    return audio[loud[0]:loud[-1] + 1] if loud.size else audio[:0]


folder = Path(sys.argv[1])
parts, paragraph, rate = [], None, None
for wav in sorted(folder.glob("*.wav")):
    audio, rate = sf.read(wav, dtype="float32")
    if paragraph is not None:
        pause = SENTENCE_PAUSE if wav.stem.split("-")[0] == paragraph else PARAGRAPH_PAUSE
        parts.append(np.zeros(int(pause * rate), dtype="float32"))
    parts.append(trim(audio))
    paragraph = wav.stem.split("-")[0]

book = np.concatenate(parts)
book *= 0.9 / np.abs(book).max()
mp3 = folder.with_suffix(".mp3")
sf.write(mp3, book, rate)
print(f"{mp3} ({len(book) / rate / 60:.1f} min)")
