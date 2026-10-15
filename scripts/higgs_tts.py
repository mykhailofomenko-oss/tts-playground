# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["mlx-audio==0.5.8", "mlx-whisper==0.4.3", "torch"]
# ///
import difflib
import os
import re

import mlx_whisper
import numpy as np
from mlx_audio.audio_io import write as audio_write
from mlx_audio.tts import load

from common import MODELS, cli, done, items, out, refs

clones = refs()
args = cli(["auto", *(f"clone-{r}" for r in clones)])
# mlx-audio only maps the config's model_type when the path name contains it
model = load(MODELS / "higgs-tts-3", model_type="higgs_audio_v3")
seed = int(os.environ.get("SEED", 0))


def letters(text):
    return re.sub(r"[\W\d_]", "", text.lower())


def check(path, result, text):
    heard = mlx_whisper.transcribe(str(path), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="uk", temperature=0.0)["text"]
    match = difflib.SequenceMatcher(None, letters(text), letters(heard)).ratio()
    loud = np.flatnonzero(np.abs(np.array(result.audio)) > 0.01)
    rate = (loud[-1] - loud[0]) / result.sample_rate / len(text) if loud.size else 0.0
    return match, rate


for voice in args.voices:
    codes, texts = [], []
    if voice.startswith("clone-"):
        wav, ref_text = clones[voice.removeprefix("clone-")]
        codes, texts = [model.encode_reference_audio(str(wav))], [ref_text]
    previous = [], []
    for name, text in items(args, limit=400):
        path = out("higgs", voice, name)
        takes = []
        for attempt in range(3):
            # a fixed seed keeps the "auto" voice the same speaker across sentences
            result = next(model.generate(text="<|prosody:expressive_high|><|prosody:pause|>" + text, temperature=0.8, top_k=50,
                                         max_new_tokens=2048, seed=seed + attempt,
                                         ref_audio_codes_list=codes + previous[0], ref_texts=texts + previous[1]))
            audio_write(str(path), result.audio, result.sample_rate)
            if not args.file:
                break
            match, rate = check(path, result, text)
            takes.append((match, result))
            if match >= 0.9 and 0.04 <= rate <= 0.15:
                break
            print(f"{name}: attempt {attempt + 1} failed, heard {match:.0%} of the text at {rate:.3f} s/char")
        else:
            match, result = max(takes, key=lambda take: take[0])
            print(f"WARNING {name}: all attempts failed, keeping the {match:.0%} match")
            audio_write(str(path), result.audio, result.sample_rate)
        if args.file:
            previous = [model.encode_reference_audio(str(path))], [text]
        done(args, path)
