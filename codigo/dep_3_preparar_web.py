"""Departamento, paso 3: prepara los archivos del mapa web.

Para cada municipio deja en salida/<dep>/web/datos/:
  <slug>.mun.json    zonas y manzanos (paso 1) con el nombre del barrio o localidad más cercano
  <slug>.calles.json tramos de calle (paso 2)
  <slug>.osm.json    barrios, negocios por rubro y lugares de referencia de OpenStreetMap
y salida/<dep>/web/index.html con la lista de municipios.
Uso: python codigo/dep_3_preparar_web.py Cochabamba
"""
import json, math, shutil, sys
from pathlib import Path
import numpy as np

DEP = sys.argv[1] if len(sys.argv) > 1 else 'Cochabamba'
RAIZ = Path(__file__).resolve().parent.parent
SAL = RAIZ / 'salida' / DEP.lower()
WEB = SAL / 'web'; DAT = WEB / 'datos'
DAT.mkdir(parents=True, exist_ok=True)
osm = json.load(open(RAIZ / 'datos_osm' / DEP.lower() / f'osm_{DEP.lower()}.json'))
dep = json.load(open(SAL / 'municipios.json'))

KX, KY = 111320 * math.cos(math.radians(17.4)), 110574
BARRIO = {'neighbourhood', 'suburb', 'quarter'}
PUEBLO = {'village', 'town', 'city', 'hamlet'}


def inside(lat, lon, b, pad):
    return b[1] - pad <= lat <= b[3] + pad and b[0] - pad <= lon <= b[2] + pad


for r in dep['municipios']:
    s, b = r['slug'], r['bounds']
    mun = json.load(open(SAL / f'mun_{s}.json'))
    places = [p for p in osm['places'] if inside(p[2], p[3], b, .03)]
    names = []; nidx = {}
    def nid(n):
        if n not in nidx: nidx[n] = len(names); names.append(n)
        return nidx[n]
    BA = [p for p in places if p[1] in BARRIO]; PU = [p for p in places if p[1] in PUEBLO]
    BX = np.array([[p[3] * KX, p[2] * KY] for p in BA]) if BA else None
    PX = np.array([[p[3] * KX, p[2] * KY] for p in PU]) if PU else None

    def label(lat, lon):
        """Barrio a menos de 600 m; si no, la localidad más cercana; distancia en metros."""
        q = np.array([lon * KX, lat * KY]); best = None
        if BX is not None:
            d = np.hypot(*(BX - q).T); i = int(d.argmin())
            if d[i] <= 600: return [nid(BA[i][0]), int(d[i])]
            best = (d[i], BA[i][0])
        if PX is not None:
            d = np.hypot(*(PX - q).T); i = int(d.argmin())
            if d[i] <= 3000 and (best is None or d[i] < best[0] + 400): return [nid(PU[i][0]), int(d[i])]
        return [nid(best[1]), int(best[0])] if best else None

    for h in mun['hex']:
        h['n'] = label(sum(p[1] for p in h['g']) / len(h['g']), sum(p[0] for p in h['g']) / len(h['g']))
    for bl in mun['blocks']:
        ring = bl['g'][0]; bl['n'] = label(sum(p[1] for p in ring) / len(ring), sum(p[0] for p in ring) / len(ring))
    mun['names'] = names
    json.dump(mun, open(DAT / f'{s}.mun.json', 'w'), separators=(',', ':'), ensure_ascii=False)

    sub = {'barrios': [[p[0], p[2], p[3]] for p in BA if inside(p[2], p[3], b, .005)],
           'pueblos': [[p[0], p[2], p[3]] for p in PU if inside(p[2], p[3], b, .005)],
           'comp': {k: [[p[0], p[1], p[2]] for p in v if inside(p[0], p[1], b, .01)] for k, v in osm['comp'].items()},
           'lm': {k: [[p[0], p[1], p[2]] for p in v if inside(p[1], p[2], b, .002)] for k, v in osm['lm'].items()}}
    json.dump(sub, open(DAT / f'{s}.osm.json', 'w'), separators=(',', ':'), ensure_ascii=False)
    src = SAL / f'calles_{s}.json'
    if src.exists(): shutil.copy(src, DAT / f'{s}.calles.json')
    print(f"{r['municipio']:24s} barrios {len(sub['barrios']):4d}  negocios {sum(len(v) for v in sub['comp'].values()):4d}  referencias {sum(len(v) for v in sub['lm'].values()):4d}")

# Mapa base dibujado (agua, ríos, áreas verdes, cultivos, calles sin nombre, tren, aeropuerto, cerros), recortado por municipio
BASE_F = RAIZ / 'datos_osm' / DEP.lower() / f'osm_base_{DEP.lower()}.json'
if BASE_F.exists():
    base = json.load(open(BASE_F))

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
    BOX = {}
    for k in ['agua', 'rio', 'verde', 'bosque', 'agro', 'calle', 'tren', 'aero', 'pista']:
        for e in base.get(k, []):
            s = e[0] if isinstance(e, list) else e
            p = dec(s); BOX[s] = (min(x[0] for x in p), max(x[0] for x in p), min(x[1] for x in p), max(x[1] for x in p))
    tot = 0
    for r in dep['municipios']:
        w, so, e_, n = r['bounds']; pad = .01
        hit = lambda s: not (BOX[s][1] < so - pad or BOX[s][0] > n + pad or BOX[s][3] < w - pad or BOX[s][2] > e_ + pad)
        sub = {k: [x for x in base.get(k, []) if hit(x[0] if isinstance(x, list) else x)] for k in ['agua', 'rio', 'verde', 'bosque', 'agro', 'calle', 'tren', 'aero', 'pista']}
        for k in ['cerro', 'rio_nombres', 'aero_nombres']:
            sub[k] = [x for x in base.get(k, []) if so - pad <= x[1] <= n + pad and w - pad <= x[2] <= e_ + pad]
        f = DAT / f"{r['slug']}.base.json"
        f.write_text(json.dumps(sub, separators=(',', ':'), ensure_ascii=False)); tot += f.stat().st_size
    print(f'Mapa base: {tot / 1e6:.1f} MB repartidos en {len(dep["municipios"])} municipios')

lista = [{k: r[k] for k in ['municipio', 'slug', 'personas', 'manzanos', 'zonas', 'cobertura', 'centro', 'bounds']} |
         {'calles': (SAL / f"calles_{r['slug']}.json").exists()} for r in dep['municipios']]
indice = {'departamento': DEP, 'personas': dep['personas'], 'manzanos': dep['manzanos'], 'municipios': lista,
          'fuente_osm': osm.get('fecha', '')}
html = (RAIZ / 'codigo' / 'plantilla_departamento.html').read_text()
html = html.replace('/*LEAFLETCSS*/', (RAIZ / 'codigo' / 'leaflet.css').read_text())
html = html.replace('/*INDICE*/', json.dumps(indice, separators=(',', ':'), ensure_ascii=False))
(WEB / 'index.html').write_text(html)

# Versión pública (GitHub Pages u otro hosting): documento completo, mapa base de CARTO/OpenStreetMap y sin chat
i = html.index('</style>') + len('</style>')
pub = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       f'<meta name="description" content="Mapa de oportunidades para abrir negocios en los municipios de {DEP}, por zona, calle y manzano, con el Censo 2024 de Bolivia.">\n'
       '<style>body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:14px}img{max-width:100%}[hidden]{display:none!important}'
       ':root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n'
       + html[:i] + '\n</head>\n<body>\n' + html[i:].replace('/*STANDALONE*/false', 'true') + '\n</body>\n</html>\n')
assert 'const STANDALONE = true' in pub
PUB = SAL / 'publico'; PUB.mkdir(exist_ok=True)
(PUB / 'index.html').write_text(pub)
(PUB / '.nojekyll').write_text('')
if not (PUB / 'datos').exists(): (PUB / 'datos').symlink_to(DAT)
tot = sum(f.stat().st_size for f in DAT.iterdir())
print(f'Web lista: {WEB} · {len(list(DAT.iterdir()))} archivos de datos, {tot / 1e6:.1f} MB')
