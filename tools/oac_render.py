#!/usr/bin/env python3
"""Ojo al Clip - renderizador genérico de clips 9:16 con audio propio.

Uso (desde Python):
    render(src, out, ss, dur, text="lowercase line", watermark=None, wm_opacity=0.1,
           subs_ass=None, seed=0)

- Mantiene el audio original (normalizado a -14 LUFS).
- Si la fuente es horizontal: la encaja entera sobre una copia difuminada (fit-on-blur).
- Si es vertical: la encuadra a pantalla completa con un leve movimiento.
- Texto en pantalla fijo arriba durante todo el clip (requisito de muchas campañas).
- Marca de agua opcional arriba a la izquierda con la opacidad indicada.
- Subtítulos ASS opcionales (centrados en el tercio inferior).
"""
import json
import random
import subprocess
from pathlib import Path

FONT = "Montserrat ExtraBold"


def probe(src):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:stream_side_data=rotation:format=duration", "-of", "json", str(src)],
                       capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    st = j["streams"][0]
    w, h = st["width"], st["height"]
    rot = 0
    for sd in st.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", 0) or 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    return w, h, float(j["format"]["duration"])


def cropdetect(src, ss, dur):
    r = subprocess.run(["ffmpeg", "-v", "info", "-ss", f"{ss + min(2, dur / 3):.2f}", "-t", "4", "-i", str(src),
                        "-vf", "cropdetect=24:2:0", "-f", "null", "-"], capture_output=True, text=True)
    lines = [l for l in r.stderr.splitlines() if "crop=" in l]
    if not lines:
        return None
    c = lines[-1].split("crop=")[-1].strip()
    cw, ch, cx, cy = map(int, c.split(":"))
    w, h, _ = probe(src)
    if cw >= w - 8 and ch >= h - 8:
        return None
    if cw < w * 0.5 or ch < h * 0.4:
        return None
    return c


def text_ass(path, line, total, y=300, secs=None):
    words = line.split()
    # parte la frase en 2 líneas si es larga
    if len(line) > 26 and len(words) > 3:
        mid = len(line) // 2
        best, acc = 0, 0
        for i, wd in enumerate(words):
            acc += len(wd) + 1
            if acc >= mid:
                best = i + 1
                break
        line = " ".join(words[:best]) + "\\N" + " ".join(words[best:])
    end = min(total + 1, secs) if secs else total + 1
    ev = (f"Dialogue: 0,0:00:00.00,0:{int(end // 60):02d}:{end % 60:05.2f},Top,,0,0,0,,"
          f"{{\\pos(540,{y})}}{line}")
    Path(path).write_text("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Top,%s,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,3,8,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % FONT + ev + "\n", encoding="utf-8")


def ffesc(p):
    return str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def render(src, out, ss, dur, text=None, watermark=None, wm_opacity=0.10, subs_ass=None, seed=0,
           text_y=300, crf=22, wm_w=300, wm_xy="40:60", text_secs=None):
    src, out = Path(src), Path(out)
    rng = random.Random(seed)
    w, h, _ = probe(src)
    cb = cropdetect(src, ss, dur)
    pre = f"crop={cb}," if cb else ""
    cw, ch = (map(int, cb.split(":")[:2]) if cb else (w, h))
    cw, ch = int(cw), int(ch)
    sat = rng.uniform(1.03, 1.12)
    con = rng.uniform(1.02, 1.07)
    grade = f"eq=saturation={sat:.3f}:contrast={con:.3f}"
    if cw / ch > 0.8:  # horizontal o casi cuadrado: fit-on-blur
        g = (f"[0:v]{pre}fps=30,split[a][b];"
             f"[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:2,eq=brightness=-0.18[bg];"
             f"[b]scale=1080:-2,{grade}[fg];[bg][fg]overlay=0:(H-h)/2,setsar=1[v0]")
    else:
        z = rng.uniform(1.04, 1.09)
        W, H = int(1080 * z) // 2 * 2, int(1920 * z) // 2 * 2
        dx = rng.choice([-1, 1]) * rng.randint(8, (W - 1080) // 2 - 2)
        dy = rng.choice([-1, 1]) * rng.randint(8, (H - 1920) // 2 - 2)
        g = (f"[0:v]{pre}fps=30,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
             f"crop=1080:1920:x='(iw-1080)/2+{dx}*t/{dur:.2f}':y='(ih-1920)/2+{dy}*t/{dur:.2f}',{grade},setsar=1[v0]")
    last = "[v0]"
    inputs = ["-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", str(src)]
    if watermark:
        inputs += ["-i", str(watermark)]
        g += (f";[1:v]scale={wm_w}:-1,format=rgba,colorchannelmixer=aa={wm_opacity:.2f}[wm];"
              f"{last}[wm]overlay={wm_xy}[v1]")
        last = "[v1]"
    tmp_ass = None
    if text:
        tmp_ass = out.with_suffix(".top.ass")
        text_ass(tmp_ass, text, dur, y=text_y, secs=text_secs)
        g += f";{last}subtitles=filename='{ffesc(tmp_ass)}'[v2]"
        last = "[v2]"
    if subs_ass:
        g += f";{last}subtitles=filename='{ffesc(subs_ass)}'[v3]"
        last = "[v3]"
    g += f";[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", g, "-map", last, "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-maxrate", "6M", "-bufsize", "12M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)
    if tmp_ass:
        tmp_ass.unlink(missing_ok=True)
    return out
