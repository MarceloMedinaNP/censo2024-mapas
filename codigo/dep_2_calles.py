"""Departamento, paso 2: fichas por tramo de calle.

Una calle no es una unidad del censo: cada tramo (de esquina a esquina, según OpenStreetMap)
suma los manzanos que dan a él, es decir, los que tienen al menos 15 m de su borde a menos
de 25 m del eje de la calle. Un manzano en esquina cuenta para varias calles.

Entrada: datos_osm/<dep>/osm_<dep>.json (calles, barrios, negocios y referencias) y
         salida/<dep>/conteos_manzano.parquet (paso 1).
Salida:  salida/<dep>/calles_<municipio>.json y salida/<dep>/calles_resumen.csv
Uso: python codigo/dep_2_calles.py Cochabamba
"""
import json, sys, unicodedata, re
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import LineString
from shapely import STRtree

DEP = sys.argv[1] if len(sys.argv) > 1 else 'Cochabamba'
RAIZ = Path(__file__).resolve().parent.parent
SAL = RAIZ / 'salida' / DEP.lower()
OSM = json.load(open(RAIZ / 'datos_osm' / DEP.lower() / f'osm_{DEP.lower()}.json'))
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()).strip('-')


def decode(s, prec=1e5):
    i = 0; lat = lon = 0; out = []
    while i < len(s):
        v = []
        for _ in range(2):
            sh = res = 0
            while True:
                b = ord(s[i]) - 63; i += 1; res |= (b & 0x1f) << sh; sh += 5
                if b < 0x20: break
            v.append(~(res >> 1) if res & 1 else res >> 1)
        lat += v[0]; lon += v[1]; out.append((lon / prec, lat / prec))
    return out


cnt = pd.read_parquet(SAL / 'conteos_manzano.parquet')
geo = gpd.read_parquet(Path.home() / 'atlasurbano' / 'datos' / 'manzanos.parquet')
geo = geo[geo.departamento == DEP][['codigo', 'geometry']].merge(cnt, on='codigo')
names = OSM['names']
lines = gpd.GeoDataFrame({'n': [t[0] for t in OSM['t']], 'c': [t[1] for t in OSM['t']],
                          'a': [t[2] for t in OSM['t']], 'b': [t[3] for t in OSM['t']]},
                         geometry=[LineString(decode(t[4])) if len(decode(t[4])) > 1 else None for t in OSM['t']], crs=4326)
lines = lines[lines.geometry.notna()]

# Reutiliza indicadores y formato de salida del paso 1 sin volver a ejecutarlo
src = (Path(__file__).with_name('dep_1_censo.py')).read_text()
ns = {'np': np, 'pd': pd, 'cnt': cnt}
exec(src[src.index('IND = {'):src.index('# ---------- Por municipio')], ns)
IND, shares, KEYS, SH, COUNTS, row_arr = ns['IND'], ns['shares'], ns['KEYS'], ns['SH'], ns['COUNTS'], ns['row_arr']
SUM = [c for c in cnt.columns if c not in ('codigo', 'municipio', 'ficha')]

resumen = []
for mun, gm in geo.groupby('municipio'):
    lon0 = (gm.total_bounds[0] + gm.total_bounds[2]) / 2
    epsg = 32719 if lon0 < -66 else 32720
    bu = gm.to_crs(epsg).reset_index(drop=True)
    w, so, e, n = gm.total_bounds
    ln = lines.cx[w - .002:e + .002, so - .002:n + .002].to_crs(epsg).reset_index(drop=True)
    tree = STRtree(bu.geometry.values)
    rows, gl = [], []
    for i, L in enumerate(ln.geometry):
        if L.length < 10: continue
        cand = tree.query(L.buffer(25))
        mz = [j for j in cand if L.intersection(bu.geometry.iloc[j].buffer(25)).length >= 15]
        if not mz: continue
        agg = bu.iloc[mz][SUM + ['ficha']].sum()
        rows.append((i, mz, agg)); gl.append(i)
    if not rows: continue
    A = pd.DataFrame([r[2] for r in rows])
    Sh = shares(A)
    lw = ln.iloc[gl].to_crs(4326)
    tramos = []
    for k, (i, mz, agg) in enumerate(rows):
        r = ln.iloc[i]; g = lw.geometry.iloc[k]
        tramos.append({'g': [[round(y, 5), round(x, 5)] for x, y in g.coords], 'n': int(r.n), 'a': int(r.a), 'b': int(r.b),
                       'c': r.c, 'mz': len(mz), 'v': row_arr(A.iloc[k], Sh.iloc[k])})
    used = sorted({t['n'] for t in tramos} | {t['a'] for t in tramos if t['a'] >= 0} | {t['b'] for t in tramos if t['b'] >= 0})
    remap = {o: j for j, o in enumerate(used)}
    for t in tramos:
        t['n'] = remap[t['n']]; t['a'] = remap.get(t['a'], -1); t['b'] = remap.get(t['b'], -1)
    s = slug(mun)
    json.dump({'keys': KEYS, 'names': [names[o] for o in used], 'tramos': tramos},
              open(SAL / f'calles_{s}.json', 'w'), separators=(',', ':'), ensure_ascii=False)
    cobert = bu.iloc[sorted({j for _, mz, _ in rows for j in mz})].personas.sum() / max(bu.personas.sum(), 1) * 100
    resumen.append({'municipio': mun, 'tramos': len(tramos), 'calles': len({t['n'] for t in tramos}),
                    'personas_en_manzanos_con_calle': round(cobert, 1)})
    print(f"{mun:24s} {len(tramos):>6,} tramos  {resumen[-1]['calles']:>5,} calles  {cobert:5.1f}% de la población frente a una calle con nombre")

pd.DataFrame(resumen).sort_values('tramos', ascending=False).to_csv(SAL / 'calles_resumen.csv', index=False)
