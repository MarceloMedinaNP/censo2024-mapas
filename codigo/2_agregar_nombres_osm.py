"""Agrega nombres de OpenStreetMap (barrios, comunas, avenidas, referencias) a data2.json."""
import json, math
import numpy as np

DIR = str(__import__('pathlib').Path(__file__).resolve().parent.parent / 'salida') + '/'
d = json.load(open(DIR + 'data2.json'))
roads = json.load(open(DIR + '../datos_osm/osm_roads.json'))
places = json.load(open(DIR + '../datos_osm/osm_places.json'))
lms = json.load(open(DIR + '../datos_osm/osm_landmarks.json'))

def decode(s):
    s = s.replace('!', '\\'); i = 0; lat = lon = 0; out = []
    while i < len(s):
        vals = []
        for _ in range(2):
            sh = res = 0
            while True:
                b = ord(s[i]) - 63; i += 1; res |= (b & 0x1f) << sh; sh += 5
                if b < 0x20: break
            vals.append(~(res >> 1) if res & 1 else res >> 1)
        lat += vals[0]; lon += vals[1]; out.append([lat / 1e4, lon / 1e4])
    return out

R = [[n, c, [decode(s) for s in segs]] for n, c, segs in roads]
allp = [p for _, _, ss in R for s in ss for p in s]
la = [p[0] for p in allp]; lo = [p[1] for p in allp]
print('vías', len(R), 'puntos', len(allp), 'lat', min(la), max(la), 'lon', min(lo), max(lo))

kx, ky = 111320 * math.cos(math.radians(17.4)), 110574
bar = [(n, a / 1e4, b / 1e4) for n, t, a, b in places if t == 'n']
com = [(n, a / 1e4, b / 1e4) for n, t, a, b in places if t == 's']
BX = np.array([[b[2] * kx, b[1] * ky] for b in bar]); CX = np.array([[c[2] * kx, c[1] * ky] for c in com])
names = []; nidx = {}
def nid(n):
    if n not in nidx: nidx[n] = len(names); names.append(n)
    return nidx[n]

def label(lat, lon):
    p = np.array([lon * kx, lat * ky])
    db = np.hypot(*(BX - p).T); i = int(db.argmin())
    dc = np.hypot(*(CX - p).T); j = int(dc.argmin())
    # barrio más cercano, distancia en metros, comuna (referencial) más cercana
    return [nid(bar[i][0]), int(db[i]), nid(com[j][0])]

def centroid(ring):
    return sum(p[1] for p in ring) / len(ring), sum(p[0] for p in ring) / len(ring)

for h in d['hex']:
    lat, lon = centroid(h['g']); h['n'] = label(lat, lon)
for b in d['blocks']:
    lat, lon = centroid(b['g'][0]); b['n'] = label(lat, lon)

# Barrios para el buscador y para etiquetas (sin duplicar nombre+posición)
d['names'] = names
d['barrios'] = [[nid(n), round(a, 5), round(b, 5)] for n, a, b in bar]
d['comunas'] = [[nid(n), round(a, 5), round(b, 5)] for n, a, b in com]
d['roads'] = [[n, c, [[[round(p[0], 4), round(p[1], 4)] for p in s] for s in ss]] for n, c, ss in R]
d['lm'] = [[n, t, a / 1e4, b / 1e4] for n, t, a, b in lms]
json.dump(d, open(DIR + 'data3.json', 'w'), separators=(',', ':'), ensure_ascii=False)
far = sum(1 for h in d['hex'] if h['n'][1] > 1200)
print('nombres', len(names), 'zonas lejos de un barrio (>1.2 km):', far, 'de', len(d['hex']))
from collections import Counter
print(Counter(names[h['n'][2]] for h in d['hex']))
