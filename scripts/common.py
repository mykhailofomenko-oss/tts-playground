import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
MODELS = ROOT / "models"


def cli(voices):
    p = argparse.ArgumentParser()
    p.add_argument("voices", nargs="*", default=list(voices), help=f"default: {' '.join(voices)}")
    p.add_argument("-t", "--text", help="say this instead of sentences.txt, then play it")
    p.add_argument("-f", "--file", type=Path, help="read a long text, one chunk per <stem>/<paragraph>-<chunk>.wav")
    return p.parse_args()


def chunks(text, limit=200):
    for p, para in enumerate((s for s in text.splitlines() if s.strip()), 1):
        parts = []
        for sentence in re.split(r"(?<=[.!?…])\s+", para.strip()):
            if parts and len(parts[-1]) + len(sentence) < limit:
                parts[-1] += " " + sentence
            else:
                parts.append(sentence)
        yield from ((f"{p:04}-{c:02}", part) for c, part in enumerate(parts, 1))


def items(args, limit=200):
    if args.file:
        return [(f"{args.file.stem}/{name}", t) for name, t in chunks(args.file.read_text(encoding="utf-8"), limit)]
    if args.text:
        return [("custom", args.text)]
    lines = (ROOT / "inputs" / "sentences.txt").read_text(encoding="utf-8").splitlines()
    return [(f"{i:02}", t) for i, t in enumerate(lines, 1) if t.strip()]


def out(engine, voice, name):
    path = ROOT / "outputs" / engine / voice / f"{name}.wav"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def refs():
    """Voice-cloning references: inputs/clones/<name>.wav with its transcript in inputs/clones/<name>.txt."""
    return {w.stem: (w, w.with_suffix(".txt").read_text(encoding="utf-8").strip()) for w in sorted((ROOT / "inputs" / "clones").glob("*.wav"))}


def done(args, path):
    print(path)
    if args.text:
        subprocess.run(["afplay", path])
