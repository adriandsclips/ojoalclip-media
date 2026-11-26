#!/usr/bin/env python3
"""Montaje por escenas (sustituye al corte por "ventana de más energía").

Dos comandos:

  python3 tools/escenas.py transcribir <Campaña> [archivo ...]
      Descarga el material de la campaña (si hace falta) y escribe /tmp/oac_src/<Campaña>/_transcripcion.json
      con los segmentos de cada vídeo (inicio, fin, texto) en el idioma de la campaña (`campañas[c].idioma`: "en"/"es").
      Imprime la transcripción con marcas de tiempo para elegir escenas.

  python3 tools/escenas.py cortar <Campaña> <archivo_fuente> <inicio_s> <fin_s> "<texto en pantalla>" "<caption>"
      Corta exactamente [inicio, fin] (la escena elegida), lo pasa a 9:16, mantiene el audio original, pone el texto
      arriba y subtítulos palabra a palabra en el idioma original, y añade el clip a la cola como "en_stock"
      con `fuente`, `escena` y `duracion`. Respeta `campañas[c].marca` (footer/logo) si existe. No hace commit.

Quien llama (la tarea programada) decide las escenas leyendo la transcripción y mirando fotogramas
(ffmpeg -ss T -frames:v 1): escena que se entienda sola, que empiece con la acción o con una frase que dé contexto
desde el primer segundo y que conserve el desenlace. Duración: la de la escena, dentro de lo que permitan las reglas.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from oac_render import render, probe  # noqa: E402
from make_stock import fetch_source, fetch_long, VID  # noqa: E402

EST = ROOT / "tools" / "estado.json"
_M = {}


def model(lang):
    from faster_whisper import WhisperModel
    name = "small.en" if lang == "en" else "small"
    if name not in _M:
        _M[name] = WhisperModel(name, device="cpu", compute_type="int8")
    return _M[name]


def audio(src, ss=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}"] + (["-t", f"{dur:.3f}"] if dur else []) + \
          ["-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32)


def src_dir(camp, C):
    return fetch_long(camp, C["fuentes_largas"]) if C.get("fuentes_largas") else \
        fetch_source(camp, C["fuente"], C.get("max_mb", 400))


def transcribir(camp, files):
    est = json.loads(EST.read_text())
    C = est["campañas"][camp]
    lang = C.get("idioma", "en")
    d = src_dir(camp, C)
    out_p = d / "_transcripcion.json"
    out = json.loads(out_p.read_text()) if out_p.exists() else {}
    vids = [d / f for f in files] if files else sorted(p for p in d.rglob("*") if p.suffix.lower() in VID)
    for f in vids:
        if f.name in out:
            continue
        kw = {} if lang == "en" else {"language": lang}
        segs, _ = model(lang).transcribe(audio(f), vad_filter=True, **kw)
        out[f.name] = {"duracion": probe(f)[2], "segmentos": [[round(s.start, 1), round(s.end, 1), s.text.strip()] for s in segs]}
        out_p.write_text(json.dumps(out, ensure_ascii=False, indent=0))
    for name, v in out.items():
        print(f"\n=== {name} ({v['duracion']:.0f} s){'  [usado]' if name in C.get('usados', []) else ''}")
        for s, e, t in v["segmentos"]:
            print(f"[{s:6.1f}-{e:6.1f}] {t}")


def subs(src, ss, dur, path, lang):
    kw = {} if lang == "en" else {"language": lang}
    segs, _ = model(lang).transcribe(audio(src, ss, dur), word_timestamps=True, vad_filter=True, **kw)
    words = [w for s in segs for w in (s.words or [])]
    if not words:
        return None
    t = lambda x: f"0:{int(x // 60):02d}:{x % 60:05.2f}"
    ev, i = [], 0
    while i < len(words):
        ch = words[i:i + 4]
        txt = " ".join(w.word.strip() for w in ch).replace("{", "").replace("}", "")
        end = words[i + 4].start if i + 4 < len(words) else ch[-1].end + 0.3
        ev.append(f"Dialogue: 0,{t(ch[0].start)},{t(max(end, ch[0].start + 0.3))},Sub,,0,0,0,,{txt}")
        i += 4
    Path(path).write_text("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat ExtraBold,62,&H0000F0FF,&H0000F0FF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,190,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n", encoding="utf-8")
    return path


def cortar(camp, fuente, ini, fin, texto, caption):
    est = json.loads(EST.read_text())
    C = est["campañas"][camp]
    d = src_dir(camp, C)
    f = next(p for p in d.rglob(fuente))
    ini, fin = float(ini), float(fin)
    dur = fin - ini
    existing = [c["id"] for c in est["cola"] if c["campaña"] == camp]
    nums = [int(x.split("-")[-1]) for x in existing if x.split("-")[-1].isdigit()]
    cid = f"{camp}-{max(nums + [0]) + 1:02d}"
    out = ROOT / "clips" / f"{cid}.mp4"
    s = subs(f, ini, dur, out.with_suffix(".subs.ass"), C.get("idioma", "en"))
    M = C.get("marca") or {}
    render(f, out, ini, dur, text=texto or None, seed=len(existing) + 1, text_y=C.get("texto_y", 300), subs_ass=s,
           watermark=(ROOT / M["archivo"]) if M else None, wm_opacity=M.get("opacidad", 0.10),
           wm_w=M.get("ancho", 300), wm_xy=M.get("pos", "40:60"), text_secs=C.get("texto_seg"))
    if s:
        Path(s).unlink(missing_ok=True)
    est["cola"].append({"id": cid, "campaña": camp, "archivo": f"clips/{cid}.mp4", "texto": caption,
                        "estado": "en_stock", "fuente": f.name, "escena": [ini, fin], "duracion": round(dur, 1),
                        "texto_pantalla": texto})
    est["campañas"][camp].setdefault("escenas_usadas", []).append([f.name, ini, fin])
    EST.write_text(json.dumps(est, ensure_ascii=False, indent=1))
    print("ok", cid, f.name, ini, fin)


if __name__ == "__main__":
    if sys.argv[1] == "transcribir":
        transcribir(sys.argv[2], sys.argv[3:])
    elif sys.argv[1] == "cortar":
        cortar(*sys.argv[2:8])
