# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["omnivoice==0.2.1", "torch==2.8.0", "torchaudio==2.8.0", "num2words", "soundfile"]
# ///
import soundfile as sf
import torch
from omnivoice import OmniVoice

from common import MODELS, cli, done, items, out, refs

clones = refs()
args = cli(["auto", *(f"clone-{r}" for r in clones)])
model = OmniVoice.from_pretrained(str(MODELS / "omnivoice"), device_map="mps", dtype=torch.float32)

for voice in args.voices:
    prompt = None
    if voice.startswith("clone-"):
        wav, ref_text = clones[voice.removeprefix("clone-")]
        prompt = model.create_voice_clone_prompt(str(wav), ref_text=ref_text)
    for name, text in items(args):
        audio = model.generate(text=text, language="uk", voice_clone_prompt=prompt, normalize_text=True)
        path = out("omnivoice", voice, name)
        sf.write(path, audio[0], 24000)
        done(args, path)
