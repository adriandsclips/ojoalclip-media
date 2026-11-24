#!/usr/bin/env python3
"""Fabrica clips nuevos para una campaña y los añade a la cola de tools/estado.json.

Uso:  python3 tools/make_stock.py <Campaña> <n>
  - Descarga la carpeta de material de la campaña (Dropbox ?dl=1 -> zip, o Google Drive con gdown)
    en /tmp/oac_src/<Campaña> (una vez por sesión).
  - Elige archivos de vídeo que no estén en estado["campañas"][c]["usados"].
  - Recorta la ventana de más energía (15 s) o el vídeo entero si es corto, lo pasa a 9:16,
    mantiene el audio original y pone un texto en pantalla del banco de la campaña.
  - Escribe clips/<Campaña>-NN.mp4 y añade la entrada a la cola con estado "en_stock".
No hace commit: eso lo hace quien lo llame.
"""
import json, random, subprocess, sys, zipfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from oac_render import render, probe  # noqa: E402

EST = ROOT / "tools" / "estado.json"
VID = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def fetch_source(camp, url):
    d = Path("/tmp/oac_src") / camp
    if d.exists() and any(d.rglob("*")):
        return d
    d.mkdir(parents=True, exist_ok=True)
    if "dropbox.com" in url:
        z = d / "src.zip"
        subprocess.run(["curl", "-sL", "--max-time", "1800", "-o", str(z), url], check=True)
        with zipfile.ZipFile(z) as zz:
            for m in zz.infolist():
                if Path(m.filename).suffix.lower() in VID:
                    zz.extract(m, d)
        z.unlink()
    else:
        import gdown, warnings
        warnings.filterwarnings("ignore")
        fid = url.split("/folders/")[1].split("?")[0]
        try:
            gdown.download_folder(id=fid, output=str(d), quiet=True)
        except Exception as e:  # gdown corta en carpetas grandes; seguimos con lo descargado
            print("aviso gdown:", str(e)[:200])
    return d


def best_window(src, total, win):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                       capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32)
    hop = 4000
    if len(a) < hop * (win * 2 + 2):
        return 0.0
    e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    c = np.convolve(e, np.ones(int(win * 2)), "valid")
    return max(0.0, min(float(np.argmax(c)) / 2, total - win - 0.1))


def main(camp, n):
    est = json.loads(EST.read_text())
    C = est["campañas"][camp]
    used = set(C.setdefault("usados", []))
    src_dir = fetch_source(camp, C["fuente"])
    files = sorted(p for p in src_dir.rglob("*") if p.suffix.lower() in VID and p.name not in used)
    random.shuffle(files)
    existing = [c["id"] for c in est["cola"] if c["campaña"] == camp] + [h.get("id", "") for h in est["historial"]]
    nums = [int(x.split("-")[-1]) for x in existing if x.startswith(camp + "-") and x.split("-")[-1].isdigit()]
    k = max(nums + [0])
    made = 0
    for f in files:
        if made >= n:
            break
        try:
            w, h, d = probe(f)
        except Exception:
            continue
        if d < 9:
            continue
        win = C.get("duracion", 15)
        ss, dur = (0.0, min(d, 30.0)) if d <= win + 3 else (best_window(f, d, win), win)
        k += 1
        cid = f"{camp}-{k:02d}"
        out = ROOT / "clips" / f"{cid}.mp4"
        texts = C.get("textos") or [""]
        caps = C["captions"] if isinstance(C["captions"], list) else list(C["captions"].values())
        render(f, out, ss, dur, text=random.choice(texts) or None, seed=k, text_y=C.get("texto_y", 300))
        est["cola"].append({"id": cid, "campaña": camp, "archivo": f"clips/{cid}.mp4",
                            "texto": random.choice(caps), "estado": "en_stock", "fuente": f.name})
        C["usados"].append(f.name)
        made += 1
        print("ok", cid, f.name, flush=True)
    EST.write_text(json.dumps(est, ensure_ascii=False, indent=1))
    print("hechos", made, "de", n)
    if made < n:
        print("MATERIAL_AGOTADO", camp)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
