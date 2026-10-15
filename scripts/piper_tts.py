# /// script
# requires-python = ">=3.9,<3.14"
# dependencies = ["piper-tts==1.8.0"]
# ///
import subprocess
import sys
import wave

from piper import PhonemeType, PiperVoice, SynthesisConfig

from common import MODELS, cli, done, items, out

MODELS = MODELS / "piper"
SPEAKERS = {
    "uk_UA-lada-x_low": [0],
    "uk_UA-ukrainian_tts-medium": [0, 1, 2],
    "uk_UA-mykyta-high": [0],
    "uk_UA-oleksa-high": [0],
    "uk_UA-tetiana-high": [0],
}

args = cli(SPEAKERS)

for model in args.voices:
    if not (MODELS / f"{model}.onnx").exists():
        subprocess.run([sys.executable, "-m", "piper.download_voices", "--data-dir", MODELS, model], check=True)
    voice = PiperVoice.load(MODELS / f"{model}.onnx")
    # text-type models map raw characters and only know lowercase
    prep = str.lower if voice.config.phoneme_type == PhonemeType.TEXT else str
    speakers = SPEAKERS.get(model, [0])
    for speaker in speakers:
        for name, text in items(args):
            path = out("piper", model if len(speakers) == 1 else f"{model}-s{speaker}", name)
            with wave.open(str(path), "wb") as wav:
                voice.synthesize_wav(prep(text), wav, SynthesisConfig(speaker_id=speaker))
            done(args, path)
