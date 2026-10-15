# Announcements

Short spoken English notices in a cloned voice, rendered locally with [mlx-audio](https://github.com/Blaizzy/mlx-audio)
on Apple Silicon.

```sh
make say TEXT="Build finished. All tests passed."
make say MODEL=chatterbox TEXT="Tests failed."
make say MODEL=kokoro VOICE=af_heart TEXT="Deploy done."
```

Each text renders once to `out/<model>-<voice>/<md5 of text>.wav`, and later calls only replay that file. `make clean`
empties the cache.

## Models

| MODEL | Voice | New phrase | With `make serve` | Notes |
|---|---|---|---|---|
| `higgs` (default) | clone of `voices/<VOICE>.wav` | about 16 s | about 5 s | Higgs TTS 3 4B from `../models/higgs-tts-3` (8.7 GB); the first run downloads it through the root Makefile |
| `chatterbox` | clone of `voices/<VOICE>.wav` | 8–9 s | about 4 s | `mlx-community/chatterbox-turbo-fp16` (5.6 GB) |
| `kokoro` | built-in, default `bm_fable` | about 7 s | about 3 s | `prince-canuma/Kokoro-82M` (0.7 GB), no cloning; voices are listed in [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) |

Times run from the call until playback ends (phrases of about 2 s), measured on this Mac. A replayed phrase
costs only its playback.

## Server

`make serve` runs `mlx_audio.server` on port 8765 in the foreground and keeps every model it has served loaded
until you stop it with Ctrl-C. `make say` sends its request there first and falls back to a one-off run when the
server isn't up. The first request per model loads it (about 40 s for Higgs). With all three loaded, the server
uses about 12 GB of memory.

## Setup

You need `uv`, `ffmpeg` and `jq` (built into recent macOS). `uvx` builds the pinned mlx-audio environment on the first call (about a minute);
there's nothing to install by hand.

A clone voice is `voices/<name>.wav` (about 10 s of clean speech) plus `voices/<name>.txt` holding its exact
transcript. `voices/patrick.wav` is cut by the Makefile from `patrick_original.mp3`, 124.1–136.4 s.

## Shell function

```sh
gandalf() {
  make -s -C ~/Developer/voices/announcements say TEXT="$*" >/dev/null 2>&1
}
```
