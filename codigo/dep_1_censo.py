"""Departamento, paso 1: censo por manzano para todos los municipios de un departamento.

Genera en salida/<departamento>/:
  - mun_<slug>.json  : manzanos (geometría + datos), zonas hexagonales y promedio municipal
  - municipios.json  : resumen de cada municipio (indicadores, centro, límites del mapa)
  - municipios_resumen.csv : la misma tabla, para planillas
Uso: python codigo/dep_1_censo.py Cochabamba
"""
import json, math, sys, unicodedata, re
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import Polygon

DEP = sys.argv[1] if len(sys.argv) > 1 else 'Cochabamba'
D = Path.home() / 'atlasurbano' / 'datos'
SAL = Path(__file__).resolve().parent.parent / 'salida' / DEP.lower()
SAL.mkdir(parents=True, exist_ok=True)
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()).strip('-')

m = gpd.read_parquet(D / 'manzanos.parquet')
m = m[m.departamento == DEP].copy()
p = pd.read_parquet(D / 'poblacion.parquet')
f = pd.read_parquet(D / 'fichas.parquet')
m = m.merge(p, on='codigo', how='left').merge(f, on='codigo', how='left').reset_index(drop=True)
m['personas'] = m.personas.fillna(0); m['viviendas'] = m.viviendas.fillna(0)


def cols(prefix, names=None):
    c = [x for x in f.columns if x.startswith(prefix)]
    return [x for x in c if any(n in x for n in names)] if names else c
def S(prefix, names=None): return m[cols(prefix, names)].sum(axis=1, min_count=1).fillna(0)

# ---------- Conteos sumables por manzano ----------
C = {}
for e in ['0a19', '20a39', '40a59', '60omas']:
    for sx in ['hombre', 'mujer']: C[f'e{e}_{sx[0]}'] = S(f'edad_{e}_{sx}')
C['pers_f'] = S('edad_')
for k, n in [('ninguno', 'ninguno'), ('prim', 'primaria'), ('sec', 'secundaria'), ('sup', 'superior')]:
    C['edu_' + k] = S('educacion_', [n])
C['edu_tot'] = S('educacion_')
C['afi_sus'] = S('saludafiliacion_', ['_sus_']); C['afi_cp'] = S('saludafiliacion_', ['cajadesalud', 'seguroprivado'])
C['afi_nin'] = S('saludafiliacion_', ['ninguno']); C['afi_tot'] = S('saludafiliacion_')
C['farm'] = S('salud_farmaciasinreceta')
C['hog'] = S('hacinamiento_'); C['hac_alto'] = S('hacinamiento_alto')
C['inet'] = m.tics_internet.fillna(0); C['celu'] = m.tics_celular.fillna(0)
C['piso_tot'] = S('material_piso_'); C['piso_b'] = S('material_piso_', ['ceramica', 'flotante', 'machimbre', 'mosaico'])
C['rev_tot'] = S('material_revoque_'); C['rev_sin'] = S('material_revoque_sin')
C['agua_tot'] = S('agua_'); C['agua_c'] = S('agua_cañería')
C['des_tot'] = S('desague_'); C['des_alc'] = S('desague_alcantarillado')
C['com_tot'] = S('combustible_'); C['gas_c'] = S('combustible_gascañería')
C['ele_tot'] = S('energiaelectrica_'); C['ele_pub'] = S('energiaelectrica_serviciopublico')
C['ten_tot'] = S('viviendatenencia_'); C['ten_prop'] = S('viviendatenencia_propia'); C['ten_alq'] = S('viviendatenencia_', ['alquilada', 'anticretico'])
C['ocu_tot'] = S('ocupacion_'); C['ocu_emp'] = S('ocupacion_empleado'); C['ocu_cp'] = S('ocupacion_cuentapropia')
C['act_tot'] = S('actividad_')
for k in ['comercio', 'enseñanza', 'construccion', 'agricultura', 'transporte']: C['act_' + k[:4]] = S('actividad_' + k)
C['hog_tot'] = S('hogar_'); C['hog_unip'] = S('hogar_unipersonal'); C['hog_fam'] = S('hogar_', ['nuclearcompleto', 'monoparental'])
C['nac_tot'] = S('nacimiento_'); C['nac_otro'] = S('nacimiento_', ['otromunicipio', 'otropais'])
C['personas'] = m.personas; C['viviendas'] = m.viviendas
cnt = pd.DataFrame(C); cnt['ficha'] = (cnt.pers_f > 0).astype(int)

IND = {
 'sh0_19': (['e0a19_h', 'e0a19_m'], 'pers_f'), 'sh20_39': (['e20a39_h', 'e20a39_m'], 'pers_f'),
 'sh40_59': (['e40a59_h', 'e40a59_m'], 'pers_f'), 'sh60': (['e60omas_h', 'e60omas_m'], 'pers_f'),
 'sh_sup': (['edu_sup'], 'edu_tot'), 'sh_int': (['inet'], 'hog'), 'sh_piso': (['piso_b'], 'piso_tot'),
 'sh_sinrev': (['rev_sin'], 'rev_tot'), 'sh_haca': (['hac_alto'], 'hog'), 'sh_agua': (['agua_c'], 'agua_tot'),
 'sh_alc': (['des_alc'], 'des_tot'), 'sh_gas': (['gas_c'], 'com_tot'), 'sh_ele': (['ele_pub'], 'ele_tot'),
 'sh_prop': (['ten_prop'], 'ten_tot'), 'sh_alq': (['ten_alq'], 'ten_tot'), 'sh_afil': (['afi_cp'], 'afi_tot'),
 'sh_sinseg': (['afi_nin'], 'afi_tot'), 'sh_farm': (['farm'], 'pers_f'), 'sh_emp': (['ocu_emp'], 'ocu_tot'),
 'sh_cp': (['ocu_cp'], 'ocu_tot'), 'sh_com': (['act_come'], 'act_tot'), 'sh_ens': (['act_ense'], 'act_tot'),
 'sh_cons': (['act_cons'], 'act_tot'), 'sh_agri': (['act_agri'], 'act_tot'), 'sh_trans': (['act_tran'], 'act_tot'), 'sh_unip': (['hog_unip'], 'hog_tot'),
 'sh_fam': (['hog_fam'], 'hog_tot'), 'sh_migr': (['nac_otro'], 'nac_tot'),
}
def shares(df):
    out = {}
    for k, (num, den) in IND.items():
        d = df[den]; out[k] = np.where(d > 0, df[num].sum(axis=1) / d.where(d > 0, 1) * 100, np.nan)
    d = df['hog']; out['sh_celnoint'] = np.where(d > 0, (df.celu - df.inet).clip(lower=0) / d.where(d > 0, 1) * 100, np.nan)
    return pd.DataFrame(out, index=df.index)

AGE = ['e0a19_h', 'e20a39_h', 'e40a59_h', 'e60omas_h', 'e0a19_m', 'e20a39_m', 'e40a59_m', 'e60omas_m']
EDU = ['edu_ninguno', 'edu_prim', 'edu_sec', 'edu_sup']
AFI = ['afi_sus', 'afi_cp', 'afi_nin']
COUNTS = ['personas', 'viviendas', 'farm'] + AGE + EDU + AFI
SH = list(IND) + ['sh_celnoint']
KEYS = COUNTS + SH
SUM = [c for c in cnt.columns if c != 'ficha']
def row_arr(c, s):
    return [int(round(c[k])) for k in COUNTS] + [None if pd.isna(s[k]) else round(float(s[k]), 1) for k in SH]

# ---------- Por municipio ----------
R = 300
def hex_id(x, y):
    q = (math.sqrt(3) / 3 * x - y / 3) / R; r = (2 / 3 * y) / R; s_ = -q - r
    rq, rr, rs = round(q), round(r), round(s_)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s_)
    if dq > dr and dq > ds: rq = -rr - rs
    elif dr > ds: rr = -rq - rs
    return int(rq), int(rr)
def hex_poly(q, r):
    cx = R * math.sqrt(3) * (q + r / 2); cy = R * 1.5 * r
    return Polygon([(cx + R * math.cos(math.radians(60 * i - 30)), cy + R * math.sin(math.radians(60 * i - 30))) for i in range(6)])

resumen = []
for mun, idx in m.groupby('municipio').groups.items():
    mm = m.loc[idx]; cc = cnt.loc[idx].copy()
    lon0 = (mm.total_bounds[0] + mm.total_bounds[2]) / 2
    epsg = 32719 if lon0 < -66 else 32720           # zona UTM 19S al oeste de -66°, 20S al este
    mu = mm.to_crs(epsg); cen = mu.geometry.centroid
    cc['hex'] = [hex_id(x, y) for x, y in zip(cen.x, cen.y)]
    hg = cc.groupby('hex')[SUM + ['ficha']].sum(); hg['manzanos'] = cc.groupby('hex').size()
    hg = hg[hg.personas >= 150]
    hs = shares(hg); hexidx = {h: i for i, h in enumerate(hg.index)}
    hgeo = gpd.GeoSeries([hex_poly(*h) for h in hg.index], crs=epsg).to_crs(4326)
    hexes = [{'g': [[round(x, 5), round(y, 5)] for x, y in hgeo.iloc[i].exterior.coords][:-1],
              'v': row_arr(hg.iloc[i], hs.iloc[i]), 'mz': int(hg.iloc[i]['manzanos'])} for i in range(len(hg))]
    ms = shares(cc)
    simp = mu.geometry.simplify(2.5).to_crs(4326)
    blocks = []
    for j, (i, g) in enumerate(zip(idx, simp)):
        polys = [pp for pp in (g.geoms if g.geom_type == 'MultiPolygon' else [g]) if not pp.is_empty]
        if not polys: continue
        full = cc.ficha[i] == 1
        blocks.append({'g': [[[round(x, 5), round(y, 5)] for x, y in pp.exterior.coords][:-1] for pp in polys],
                       'c': mm.codigo[i], 'h': hexidx.get(cc.hex[i], -1),
                       'v': row_arr(cc.loc[i], ms.loc[i]) if full else [int(cc.personas[i]), int(cc.viviendas[i])]})
    tot = cc[SUM].sum(); ts = shares(tot.to_frame().T).iloc[0]
    b = mm.total_bounds
    meta = {'municipio': mun, 'slug': slug(mun), 'epsg': epsg, 'personas': int(tot.personas), 'manzanos': int(len(mm)),
            'zonas': len(hexes), 'cobertura': round(float(cc.loc[cc.ficha == 1, 'personas'].sum() / max(tot.personas, 1) * 100), 1),
            'bounds': [round(float(v), 5) for v in b], 'centro': [round(float((b[1] + b[3]) / 2), 5), round(float((b[0] + b[2]) / 2), 5)]}
    json.dump({'keys': KEYS, 'hex': hexes, 'blocks': blocks, 'city': row_arr(tot, ts), 'meta': meta},
              open(SAL / f"mun_{meta['slug']}.json", 'w'), separators=(',', ':'), ensure_ascii=False)
    resumen.append({**{k: meta[k] for k in ['municipio', 'slug', 'personas', 'manzanos', 'zonas', 'cobertura', 'centro', 'bounds']},
                    'ind': {k: (None if pd.isna(ts[k]) else round(float(ts[k]), 1)) for k in SH}})
    print(f"{mun:24s} {meta['personas']:>8,} personas {meta['manzanos']:>6,} manzanos {len(hexes):>4} zonas  EPSG:{epsg}")

# Conteos por manzano para los pasos siguientes (calles)
cnt.assign(codigo=m.codigo.values, municipio=m.municipio.values).to_parquet(SAL / 'conteos_manzano.parquet')

resumen.sort(key=lambda r: -r['personas'])
tot = cnt[SUM].sum(); ts = shares(tot.to_frame().T).iloc[0]
json.dump({'departamento': DEP, 'keys': KEYS, 'sh': SH, 'municipios': resumen,
           'promedio': {k: round(float(ts[k]), 1) for k in SH}, 'personas': int(tot.personas), 'manzanos': int(len(m))},
          open(SAL / 'municipios.json', 'w'), separators=(',', ':'), ensure_ascii=False)
pd.DataFrame([{**{k: r[k] for k in ['municipio', 'personas', 'manzanos', 'zonas', 'cobertura']}, **r['ind']} for r in resumen]) \
  .to_csv(SAL / 'municipios_resumen.csv', index=False)
print('Departamento:', DEP, int(tot.personas), 'personas en', len(m), 'manzanos y', len(resumen), 'municipios')
