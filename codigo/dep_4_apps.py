"""Departamento, paso 4: datos y páginas del Atlas municipal y del Buscador cercano.

Requiere los pasos 1 a 3 (usa salida/<dep>/web/datos/). Deja:
  salida/<dep>/web/datos/cerca.json        servicios y negocios de todo el departamento + índice de búsqueda
  salida/<dep>/web/datos/<slug>.vias.json  calles con nombre por municipio (fondo del buscador dentro de Claude)
  salida/<dep>/atlas/index.html            Atlas municipal para Claude      (+ publico/atlas/ para GitHub Pages)
  salida/<dep>/cerca/index.html            Buscador cercano para Claude     (+ publico/cerca/)
Uso: python codigo/dep_4_apps.py Cochabamba
"""
import json, math, sys
from pathlib import Path

DEP = sys.argv[1] if len(sys.argv) > 1 else 'Cochabamba'
RAIZ = Path(__file__).resolve().parent.parent
C = RAIZ / 'codigo'
SAL = RAIZ / 'salida' / DEP.lower()
DAT = SAL / 'web' / 'datos'
osm = json.load(open(RAIZ / 'datos_osm' / DEP.lower() / f'osm_{DEP.lower()}.json'))
dep = json.load(open(SAL / 'municipios.json'))
MUN = dep['municipios']


def dec(s):
    i = 0; la = lo = 0; out = []
    while i < len(s):
        v = []
        for _ in range(2):
            sh = res = 0
            while True:
                b = ord(s[i]) - 63; i += 1; res |= (b & 0x1f) << sh; sh += 5
                if b < 0x20: break
            v.append(~(res >> 1) if res & 1 else res >> 1)
        la += v[0]; lo += v[1]; out.append((la / 1e5, lo / 1e5))
    return out


def inside(lat, lon, b, pad=0):
    return b[1] - pad <= lat <= b[3] + pad and b[0] - pad <= lon <= b[2] + pad


def mun_of(lat, lon):
    """Municipio que contiene el punto (el de centro más cercano si hay varios rectángulos)."""
    cand = [i for i, m in enumerate(MUN) if inside(lat, lon, m['bounds'])] or range(len(MUN))
    return min(cand, key=lambda i: (MUN[i]['centro'][0] - lat) ** 2 + (MUN[i]['centro'][1] - lon) ** 2)


# ---------- Calles con nombre por municipio ----------
T = [(t[0], t[1], t[4], dec(t[4])) for t in osm['t']]
for m in MUN:
    b = m['bounds']; names = []; nid = {}; out = []
    for n, c, enc, pts in T:
        if not any(inside(la, lo, b, .01) for la, lo in pts): continue
        if n not in nid: nid[n] = len(names); names.append(osm['names'][n])
        out.append([nid[n], c, enc])
    (DAT / f"{m['slug']}.vias.json").write_text(json.dumps({'names': names, 't': out}, separators=(',', ':'), ensure_ascii=False))

# ---------- Índice de búsqueda: barrios, localidades y calles ----------
idx = []
for name, kind, la, lo in osm['places']:
    k = 'b' if kind in ('neighbourhood', 'suburb', 'quarter') else 'p'
    idx.append([name, k, round(la, 5), round(lo, 5), mun_of(la, lo)])
by = {}
for n, c, enc, pts in T:
    la, lo = pts[len(pts) // 2] if len(pts) > 2 else ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
    by.setdefault((n, mun_of(la, lo)), []).append((la, lo))
for (n, mi), ps in by.items():
    ps.sort(); la, lo = ps[len(ps) // 2]
    idx.append([osm['names'][n], 'c', round(la, 5), round(lo, 5), mi])

# ---------- Servicios y negocios de todo el departamento ----------
cats = {}
for k, v in osm['comp'].items():
    cats[k] = [[round(p[0], 5), round(p[1], 5), p[2] if len(p) > 2 else ''] for p in v]
for k, v in osm['lm'].items():
    cats[k] = [[round(p[1], 5), round(p[2], 5), p[0]] for p in v]
cerca = {'departamento': DEP, 'fecha_osm': osm.get('fecha', ''),
         'municipios': [{'m': m['municipio'], 'slug': m['slug'], 'b': m['bounds'], 'c': m['centro'], 'calles': (SAL / f"calles_{m['slug']}.json").exists()} for m in MUN],
         'cats': cats, 'idx': idx}
(DAT / 'cerca.json').write_text(json.dumps(cerca, separators=(',', ':'), ensure_ascii=False))
print(f"cerca.json: {sum(len(v) for v in cats.values())} lugares en {len(cats)} categorías, {len(idx)} nombres buscables, {(DAT / 'cerca.json').stat().st_size / 1e6:.2f} MB")

# ---------- Promedios del departamento, incluidos los derivados de conteos ----------
tot = None; keys = None
for m in MUN:
    mj = json.load(open(SAL / f"mun_{m['slug']}.json")); keys = mj['keys']
    v = mj['city']
    tot = [ (a or 0) + (b or 0) for a, b in zip(tot, v)] if tot else [x or 0 for x in v]
cnt = dict(zip(keys, tot))
deprom = dict(dep['promedio'])
edu = sum(cnt[k] for k in ['edu_ninguno', 'edu_prim', 'edu_sec', 'edu_sup']); afi = sum(cnt[k] for k in ['afi_sus', 'afi_cp', 'afi_nin'])
deprom.update({'sh_ning': cnt['edu_ninguno'] / edu * 100, 'sh_prim': cnt['edu_prim'] / edu * 100, 'sh_sec': cnt['edu_sec'] / edu * 100,
               'sh_sus': cnt['afi_sus'] / afi * 100})
deprom = {k: round(v, 1) for k, v in deprom.items()}

# ---------- Páginas ----------
css_base = (C / '_css_base.txt').read_text()
leaflet_css = (C / 'leaflet.css').read_text()
COMUN = """
*,*::before,*::after{box-sizing:border-box}
.hbtns{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.btn{font:inherit;font-size:13px;font-weight:600;padding:7px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--fg);cursor:pointer}
.btn:hover{border-color:var(--accent)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:var(--panel)}
.btn:disabled{opacity:.5;cursor:default}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.base-dark .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.85) contrast(.9) saturate(.6)}
.leaflet-tile-pane{opacity:.85}
.lbl-w{font-family:var(--f-body);font-style:italic;font-size:11.5px;color:var(--river);letter-spacing:.03em}
.lbl-peak small{font-weight:400;color:var(--muted)}
.tabs{display:flex;border:1px solid var(--line);border-radius:6px;overflow:hidden}
.tabs button{font:inherit;font-size:12px;padding:4px 10px;border:0;background:var(--panel);color:var(--fg);cursor:pointer}
.tabs button+button{border-left:1px solid var(--line)}
.tabs button[aria-pressed="true"]{background:var(--accent-soft);color:var(--accent);font-weight:600}
.tabs button:disabled{color:var(--muted);cursor:not-allowed}
"""


def page(title, extra_css, body_file, indice, standalone, desc):
    body = (C / body_file).read_text().replace('/*INDICE*/', json.dumps(indice, separators=(',', ':'), ensure_ascii=False))
    style = css_base.replace('/*LEAFLETCSS*/', leaflet_css).replace('</style>', COMUN + extra_css + '</style>')
    head = (f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">\n')
    if not standalone:
        return head + style + '\n' + body
    return ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<meta name="description" content="{desc}">\n'
            '<style>body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:14px}[hidden]{display:none!important}</style>\n'
            + head + style + '\n</head>\n<body>\n' + body.replace('/*STANDALONE*/false', 'true') + '\n</body>\n</html>\n')


lista = [{k: r[k] for k in ['municipio', 'slug', 'personas', 'manzanos', 'zonas', 'cobertura', 'centro', 'bounds']} |
         {'calles': (SAL / f"calles_{r['slug']}.json").exists()} for r in MUN]
APPS = [
    ('atlas', 'Atlas Censo Cochabamba', '_css_atlas.txt', '_cuerpo_atlas.html',
     {'departamento': DEP, 'personas': dep['personas'], 'manzanos': dep['manzanos'], 'municipios': lista, 'dep': deprom},
     f'Atlas del Censo 2024 para los municipios de {DEP}: población, educación, salud, vivienda y servicios básicos por barrio, zona, calle y manzano.'),
    ('cerca', 'Qué hay cerca', '_css_cerca.txt', '_cuerpo_cerca.html',
     {'departamento': DEP},
     f'Encuentra la farmacia, el taller, la veterinaria o el centro de salud más cercano en {DEP}, con datos de OpenStreetMap.'),
]
for slug, title, css_f, body_f, indice, desc in APPS:
    if not (C / body_f).exists(): continue
    extra = (C / css_f).read_text() if (C / css_f).exists() else ''
    d = SAL / slug; d.mkdir(exist_ok=True)
    (d / 'index.html').write_text(page(title, extra, body_f, indice, False, desc))
    if not (d / 'datos').exists(): (d / 'datos').symlink_to(DAT)
    p = SAL / 'publico' / slug; p.mkdir(parents=True, exist_ok=True)
    pub = page(title, extra, body_f, indice, True, desc).replace('fetch(`datos/', 'fetch(`../datos/').replace("fetch('datos/", "fetch('../datos/")
    assert 'const STANDALONE = true' in pub
    (p / 'index.html').write_text(pub)
    print(f'{slug}: {d / "index.html"} y {p / "index.html"}')
