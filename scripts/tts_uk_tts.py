# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["tts-uk==1.3.7", "soundfile"]
# ///
import os

import soundfile as sf

from common import MODELS, cli, done, items, out

# tts_uk downloads its acoustic model into ./models/ of the working directory at import time
(MODELS / "tts_uk").mkdir(parents=True, exist_ok=True)
os.chdir(MODELS / "tts_uk")
from tts_uk.inference import synthesis  # noqa: E402

args = cli(["tetiana", "mykyta", "lada"])

for voice in args.voices:
    for name, text in items(args):
        _, wave, _ = synthesis(
            text=text, voice=voice, n_takes=1, use_latest_take=False, token_dur_scaling=1,
            f0_mean=0, f0_std=0, energy_mean=0, energy_std=0,
            sigma_decoder=0.8, sigma_token_duration=0.666, sigma_f0=1, sigma_energy=1,
        )
        path = out("tts_uk", voice, name)
        sf.write(path, wave.squeeze().cpu().numpy(), 44100)
        done(args, path)
