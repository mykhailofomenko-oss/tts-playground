# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["supertonic==1.3.1"]
# ///
from common import MODELS, cli, done, items, out
from supertonic import TTS

args = cli(["F1", "F2", "F3", "F4", "F5", "M1", "M2", "M3", "M4", "M5"])
tts = TTS(model_dir=MODELS / "supertonic", auto_download=False)

for voice in args.voices:
    style = tts.get_voice_style(voice_name=voice)
    for name, text in items(args):
        wav, _ = tts.synthesize(text, voice_style=style, lang="uk")
        path = out("supertonic", voice, name)
        tts.save_audio(wav, str(path))
        done(args, path)
