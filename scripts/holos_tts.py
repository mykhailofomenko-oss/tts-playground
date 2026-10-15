# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#   "torch==2.8.0", "torchaudio==2.8.0", "transformers==5.0.0", "numpy<2", "sentencepiece", "ctranslate2", "soundfile",
#   "ukrainian-word-stress @ git+https://github.com/patriotyk/ukrainian-word-stress.git",
#   "ipa-uk @ git+https://github.com/patriotyk/ipa-uk.git",
#   "holos @ git+https://github.com/patriotyk/HolosTTS@57ca2955a3d08c8ce45f7fdd23810f2af66cdfbc",
# ]
# ///
import soundfile as sf
import torch
from holos.models import HolosTTS, VoiceEncoder

from common import MODELS, cli, done, items, out, refs
from uk_phonemes import phonemize

d = MODELS / "holos"
model = HolosTTS(str(d / "holos.pt"), device="cpu", voices_path=str(d / "voices.pt"))
clones = refs()
args = cli([*model.list_voices(), *(f"clone-{r}" for r in clones)])
encoder = VoiceEncoder(str(d / "voice_encoder.pt"), device="cpu") if any(v.startswith("clone-") for v in args.voices) else None

for voice in args.voices:
    style = encoder.encode(str(clones[voice.removeprefix("clone-")][0])) if voice.startswith("clone-") else voice
    for name, text in items(args):
        audio = model.generate(phonemize(text), voice=style)
        path = out("holos", voice, name)
        sf.write(path, audio.squeeze().cpu().numpy(), 24000)
        done(args, path)
