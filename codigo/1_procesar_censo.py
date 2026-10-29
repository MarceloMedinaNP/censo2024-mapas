"""Mapa de localización de negocios, municipio de Cochabamba (Censo 2024 por manzano).
Genera data.json con: hexágonos (~23 ha), manzanos, puntos de calor y promedios municipales."""
import json, math
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import Polygon

D = str(__import__('pathlib').Path.home() / 'atlasurbano' / 'datos') + '/'
OUT = str(__import__('pathlib').Path(__file__).resolve().parent.parent / 'salida') + '/'

m = gpd.read_parquet(D + 'manzanos.parquet')
m = m[m.municipio == 'Cochabamba'].copy()
p = pd.read_parquet(D + 'poblacion.parquet')
f = pd.read_parquet(D + 'fichas.parquet')
m = m.merge(p, on='codigo', how='left').merge(f, on='codigo', how='left').reset_index(drop=True)
m['personas'] = m.personas.fillna(0); m['viviendas'] = m.viviendas.fillna(0)

def cols(prefix, names=None):
    c = [x for x in f.columns if x.startswith(prefix)]
    return [x for x in c if any(n in x for n in names)] if names else c
def S(prefix, names=None): return m[cols(prefix, names)].sum(axis=1, min_count=1).fillna(0)

# Conteos de base (todos sumables)
C = {}
for e in ['0a19', '20a39', '40a59', '60omas']:
    for sx in ['hombre', 'mujer']: C[f'e{e}_{sx[0]}'] = S(f'edad_{e}_{sx}')
C['pers_f'] = S('edad_')                                     # personas con ficha
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
C['ten_tot'] = S('viviendatenencia_'); C['ten_prop'] = S('viviendatenencia_propia'); C['ten_alq'] = S('viviendatenencia_', ['alquilada', 'anticretico'])
C['ocu_tot'] = S('ocupacion_'); C['ocu_emp'] = S('ocupacion_empleado'); C['ocu_cp'] = S('ocupacion_cuentapropia')
C['act_tot'] = S('actividad_')
for k in ['comercio', 'enseñanza', 'construccion', 'saludyasistencia']: C['act_' + k[:4]] = S('actividad_' + k)
C['hog_tot'] = S('hogar_'); C['hog_unip'] = S('hogar_unipersonal'); C['hog_fam'] = S('hogar_', ['nuclearcompleto', 'monoparental'])
C['personas'] = m.personas; C['viviendas'] = m.viviendas
cnt = pd.DataFrame(C)
cnt['ficha'] = (cnt.pers_f > 0).astype(int)

# Indicadores = numerador / denominador (en %)
IND = {
 'sh0_19': (['e0a19_h', 'e0a19_m'], 'pers_f'), 'sh20_39': (['e20a39_h', 'e20a39_m'], 'pers_f'),
 'sh40_59': (['e40a59_h', 'e40a59_m'], 'pers_f'), 'sh60': (['e60omas_h', 'e60omas_m'], 'pers_f'),
 'sh_sup': (['edu_sup'], 'edu_tot'), 'sh_int': (['inet'], 'hog'), 'sh_piso': (['piso_b'], 'piso_tot'),
 'sh_sinrev': (['rev_sin'], 'rev_tot'), 'sh_haca': (['hac_alto'], 'hog'), 'sh_agua': (['agua_c'], 'agua_tot'),
 'sh_alc': (['des_alc'], 'des_tot'), 'sh_gas': (['gas_c'], 'com_tot'), 'sh_prop': (['ten_prop'], 'ten_tot'),
 'sh_alq': (['ten_alq'], 'ten_tot'), 'sh_afil': (['afi_cp'], 'afi_tot'), 'sh_sinseg': (['afi_nin'], 'afi_tot'),
 'sh_farm': (['farm'], 'pers_f'), 'sh_emp': (['ocu_emp'], 'ocu_tot'), 'sh_cp': (['ocu_cp'], 'ocu_tot'),
 'sh_com': (['act_come'], 'act_tot'), 'sh_ens': (['act_ense'], 'act_tot'), 'sh_cons': (['act_cons'], 'act_tot'),
 'sh_unip': (['hog_unip'], 'hog_tot'), 'sh_fam': (['hog_fam'], 'hog_tot'),
}
def shares(df):
    out = {}
    for k, (num, den) in IND.items():
        d = df[den]; out[k] = np.where(d > 0, df[num].sum(axis=1) / d.where(d > 0, 1) * 100, np.nan)
    if 'celu' in df:
        d = df['hog']; out['sh_celnoint'] = np.where(d > 0, (df.celu - df.inet).clip(lower=0) / d.where(d > 0, 1) * 100, np.nan)
    return pd.DataFrame(out, index=df.index)

AGE = ['e0a19_h', 'e20a39_h', 'e40a59_h', 'e60omas_h', 'e0a19_m', 'e20a39_m', 'e40a59_m', 'e60omas_m']
EDU = ['edu_ninguno', 'edu_prim', 'edu_sec', 'edu_sup']
AFI = ['afi_sus', 'afi_cp', 'afi_nin']
COUNTS = ['personas', 'viviendas', 'farm'] + AGE + EDU + AFI
SH = list(IND) + ['sh_celnoint']
KEYS = COUNTS + SH   # orden de los arreglos en el JSON

# Hexágonos (~300 m de radio)
mu = m.to_crs(32719); cen = mu.geometry.centroid
R = 300
def hex_id(x, y):
    q = (math.sqrt(3) / 3 * x - y / 3) / R; r = (2 / 3 * y) / R; s_ = -q - r
    rq, rr, rs = round(q), round(r), round(s_)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s_)
    if dq > dr and dq > ds: rq = -rr - rs
    elif dr > ds: rr = -rq - rs
    return int(rq), int(rr)
cnt['hex'] = [hex_id(x, y) for x, y in zip(cen.x, cen.y)]
num = cnt.drop(columns='hex').columns
hg = cnt.groupby('hex')[list(num)].sum()
hg['manzanos'] = cnt.groupby('hex').size()
hg = hg[hg.personas >= 150]
hs = shares(hg)
hexidx = {h: i for i, h in enumerate(hg.index)}

def hex_poly(q, r):
    cx = R * math.sqrt(3) * (q + r / 2); cy = R * 1.5 * r
    return Polygon([(cx + R * math.cos(math.radians(60 * i - 30)), cy + R * math.sin(math.radians(60 * i - 30))) for i in range(6)])
hgeo = gpd.GeoSeries([hex_poly(*h) for h in hg.index], crs=32719).to_crs(4326)

def row_arr(cnts, shs):
    a = [int(round(cnts[k])) for k in COUNTS]
    a += [None if pd.isna(shs[k]) else round(float(shs[k]), 1) for k in SH]
    return a

hexes = []
for i, h in enumerate(hg.index):
    g = hgeo.iloc[i]
    hexes.append({'g': [[round(x, 5), round(y, 5)] for x, y in g.exterior.coords][:-1],
                  'v': row_arr(hg.iloc[i], hs.iloc[i]), 'mz': int(hg.iloc[i]['manzanos'])})

# Manzanos (geometría simplificada + datos)
ms = shares(cnt)
mw = mu.copy(); mw['geometry'] = mw.geometry.simplify(2.5); mw = mw.to_crs(4326)
blocks = []
for i, g in enumerate(mw.geometry):
    polys = [pp for pp in (g.geoms if g.geom_type == 'MultiPolygon' else [g]) if not pp.is_empty]
    if not polys: continue
    has = cnt.ficha[i] == 1
    blocks.append({'g': [[[round(x, 5), round(y, 5)] for x, y in pp.exterior.coords][:-1] for pp in polys],
                   'c': m.codigo[i], 'h': hexidx.get(cnt.hex[i], -1),
                   'v': row_arr(cnt.loc[i], ms.loc[i]) if has else [int(cnt.personas[i]), int(cnt.viviendas[i])]})

# Puntos de calor: lat, lon, personas, 60+, farmacia, 0-19, 20-39
cw = mu.to_crs(4326).geometry.centroid
pts = [[round(y, 5), round(x, 5), int(r.personas), int(r.e60omas_h + r.e60omas_m), int(r.farm),
        int(r.e0a19_h + r.e0a19_m), int(r.e20a39_h + r.e20a39_m)]
       for x, y, (_, r) in zip(cw.x, cw.y, cnt.iterrows()) if r.personas > 0]

tot = cnt.drop(columns='hex').sum()
ts = shares(tot.to_frame().T).iloc[0]
city = row_arr(tot, ts)
meta = {'personas': int(tot.personas), 'manzanos': int(len(m)), 'hexagonos': len(hexes),
        'cobertura': round(float(cnt.loc[cnt.ficha == 1, 'personas'].sum() / tot.personas * 100), 1)}
json.dump({'keys': KEYS, 'hex': hexes, 'blocks': blocks, 'pts': pts, 'city': city, 'meta': meta},
          open(OUT + 'data2.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print(meta, len(blocks), len(pts))
print(dict(zip(SH, [round(float(x), 1) for x in ts[SH]])))
