# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#   "torch==2.8.0", "torchaudio==2.8.0", "transformers==5.0.0", "numpy<2", "sentencepiece", "ctranslate2", "soundfile",
#   "ukrainian-word-stress @ git+https://github.com/patriotyk/ukrainian-word-stress.git",
#   "ipa-uk @ git+https://github.com/patriotyk/ipa-uk.git",
#   "styletts2-inference @ git+https://github.com/patriotyk/styletts2-inference@209352700cf703a05ff94501290095dd9072fd5f",
# ]
# ///
import soundfile as sf
import torch
from styletts2_inference.models import StyleTTS2

from common import MODELS, cli, done, items, out
from uk_phonemes import phonemize

multi = MODELS / "styletts2-multi"
styles = {p.stem: p for p in sorted((multi / "voices").glob("*.pt"))}
args = cli(["filatov", *styles])
models = {}


def load(name):
    d = MODELS / name
    if name not in models:
        models[name] = StyleTTS2(config_path=d / "config.yml", weights_path=d / "pytorch_model.bin")
    return models[name]


for voice in args.voices:
    model = load("styletts2-single" if voice == "filatov" else "styletts2-multi")
    style = torch.load(MODELS / "styletts2-single" / "style.pt" if voice == "filatov" else styles[voice])
    for name, text in items(args):
        wav = model(model.tokenizer.encode(phonemize(text)), speed=1.0, s_prev=style)
        path = out("styletts2", voice, name)
        sf.write(path, wav.cpu().numpy(), 24000)
        done(args, path)
