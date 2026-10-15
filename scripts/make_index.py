"""Writes outputs/index.html: every outputs/<engine>/<voice>/<name>.wav as a click-to-play grid."""
import html
from urllib.parse import quote

from common import ROOT

sentences = (ROOT / "inputs" / "sentences.txt").read_text(encoding="utf-8").splitlines()
names = [f"{i:02}" for i in range(1, len(sentences) + 1)] + ["custom"]
head = "".join(f'<th title="{html.escape(s)}">{i}</th>' for i, s in enumerate(sentences, 1)) + "<th>custom</th>"
rows = []
for engine in sorted(p for p in (ROOT / "outputs").iterdir() if p.is_dir()):
    rows.append(f'<tr><th colspan="{len(names) + 1}" class="engine">{engine.name}</th></tr>')
    for voice in sorted(p for p in engine.iterdir() if p.is_dir()):
        cells = "".join(
            f'<td><button data-src="{quote(f"{engine.name}/{voice.name}/{n}.wav")}">▶</button></td>'
            if (voice / f"{n}.wav").exists() else "<td></td>"
            for n in names
        )
        rows.append(f"<tr><td class=voice>{html.escape(voice.name)}</td>{cells}</tr>")

(ROOT / "outputs" / "index.html").write_text(f"""<!doctype html>
<meta charset="utf-8"><title>Ukrainian TTS</title>
<style>
:root {{ color-scheme: light dark; font: 14px system-ui; }}
body {{ margin: 16px; }}
table {{ border-collapse: collapse; }}
td, th {{ padding: 2px 4px; text-align: center; }}
th[title] {{ cursor: help; text-decoration: underline dotted; }}
.engine {{ text-align: left; padding-top: 16px; font-size: 16px; }}
.voice {{ text-align: left; white-space: nowrap; }}
button {{ cursor: pointer; }}
button.playing {{ background: #4a8; color: white; }}
ol {{ columns: 2; }}
</style>
<h1>Ukrainian TTS samples</h1>
<ol>{"".join(f"<li>{html.escape(s)}</li>" for s in sentences)}</ol>
<table><tr><th></th>{head}</tr>{"".join(rows)}</table>
<script>
const player = new Audio();
let current;
document.addEventListener("click", e => {{
  const b = e.target.closest("button[data-src]");
  if (!b) return;
  current?.classList.remove("playing");
  if (current === b && !player.paused) {{ player.pause(); current = null; return; }}
  player.src = b.dataset.src; player.play(); b.classList.add("playing"); current = b;
}});
player.onended = () => current?.classList.remove("playing");
</script>
""", encoding="utf-8")
print(ROOT / "outputs" / "index.html")
