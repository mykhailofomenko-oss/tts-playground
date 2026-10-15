# Ukrainian TTS playground

Every engine reads `inputs/sentences.txt` and writes `outputs/<engine>/<voice>/NN.wav`.

Needs macOS on Apple Silicon (MLX, MPS, `afplay`) and [uv](https://docs.astral.sh/uv/). `make help` lists everything.

```sh
make models                                    # download weights (~18 GB, pinned revisions)
make all                                       # every engine over inputs/sentences.txt, then open the index
make holos                                     # one engine, all voices
make holos VOICES="Speaker_0 clone-mykyta"     # some voices
make holos VOICES=Speaker_0 TEXT="Добрий вечір!"   # your own text, plays it (outputs/.../custom.wav)
make voices                                    # list voices per engine
make open                                      # click-to-play grid of everything in outputs/
```

| Script | Model | Voices | License | Time per voice, 14 sentences (M3 Max, excl. load) |
|---|---|---|---|---|
| `scripts/piper_tts.py` | Piper (VITS), 5 uk_UA models | 7 | MIT | 2 s |
| `scripts/tts_uk_tts.py` | RAD-TTS++ + Vocos, 44.1 kHz | tetiana, mykyta, lada | MIT | 5 s |
| `scripts/styletts2_tts.py` | StyleTTS2 Ukrainian (patriotyk) | filatov + 31 multispeaker | MIT | 16 s |
| `scripts/holos_tts.py` | HolosTTS (patriotyk, Oct 2026) | 27 presets + clones | MIT | 16 s |
| `scripts/supertonic_tts.py` | Supertonic 3, ONNX | F1–F5, M1–M5 | OpenRAIL-M | 13 s |
| `scripts/omnivoice_tts.py` | OmniVoice 0.6B (MPS) | auto + clones | CC-BY-NC | 1.7 min |
| `scripts/higgs_tts.py` | Higgs TTS 3 4B (MLX) | auto + clones | non-commercial | 1.5 min |

## Audiobook

```sh
make book FILE=inputs/hitchhiker.txt SEED=2    # -> outputs/higgs/clone-maks-tsu/hitchhiker.mp3
make book FILE=inputs/hitchhiker.txt ENGINE=holos VOICE=Speaker_0
```

Each non-empty line is a paragraph; sentences are merged into chunks of up to ~200 characters (~400 for Higgs),
rendered as `outputs/<engine>/<voice>/<stem>/<paragraph>-<chunk>.wav`, then `scripts/audiobook.py` trims them and
joins them with 0.35 s pauses between chunks and 0.9 s between paragraphs. Higgs reads digits badly; spell numbers out.
Higgs samples with temperature 0.8, top_k 50, `<|prosody:expressive_high|><|prosody:pause|>` before each chunk
(the pause keeps it from swallowing the first word), seed `SEED` (default 0).
For a file, Higgs also hears the previous chunk, and Whisper checks each chunk; a chunk it mishears
(under 90 % of the letters, or outside 0.04–0.15 s per character) is re-rendered with the next seed, up to 3 tries.

## Announcements

```sh
make -C announcements say TEXT="Build finished. All tests passed."   # Higgs, cloned voice; MODEL=chatterbox|kokoro
```

Short English notices; each text renders once and later calls replay it. See `announcements/README.md`.

## Text handling differs per engine

- `styletts2` and `holos` run `scripts/uk_phonemes.py`: numbers to words (m2m100 verbalizer), automatic stress, IPA.
  Put `+` after a vowel to force stress: `за+мок` vs `замо+к`.
- `omnivoice` turns bare integers into words (`num2words`). The others read digits as best they can.
- Piper's `ukrainian_tts-medium` is character-based: lowercase only, digits are dropped,
  and a combining acute accent (U+0301) after a vowel marks stress.
- Tags: Higgs `<|emotion:elation|>`, `<|prosody:pause|>` (see `models/higgs-tts-3/PROMPTING.md`);
  Supertonic `<laugh>`, `<breath>`; OmniVoice `[laughter]`.

## Voice cloning

`inputs/clones/<name>.wav` with its transcript in `inputs/clones/<name>.txt` becomes a `clone-<name>` voice in
holos, omnivoice and higgs. A clean 5–15 s clip in Ukrainian works best.
`mykyta` and `tetiana` are real recordings from the Apache-2.0 speech-uk OpenTTS datasets; `maks-tsu` is a local sample.
Only clone voices you have consent to use.

## Layout

- `announcements/` English notices in a cloned voice (`make -C announcements say TEXT=…`).
- `scripts/` engines and helpers, `inputs/` texts and clone clips, `outputs/` rendered audio and `index.html`.
- `models/` weights from `make models`. Piper and tts_uk fetch theirs on first run; tts_uk's vocoder and
  the stress model land in the Hugging Face cache.
- Each script declares its dependencies inline; `uv run` builds a separate env per script.
