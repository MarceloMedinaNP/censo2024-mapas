"""Departamento, paso 0 (opcional): capas de servicios desde el extracto de Geofabrik.

Overpass rechaza a menudo las consultas (errores 406 y 504 desde junio de 2026). Este paso lee el
extracto diario de Bolivia de Geofabrik (bolivia-latest.osm.pbf, ~170 MB) y agrega al extracto
departamental datos_osm/<dep>/osm_<dep>.json:

  comp: los 10 rubros de negocios (farmacia ... taller) y cajero, gasolinera, gomeria, restaurante,
        hotel, hospital_clinica, centro_salud, posta
  lm:   referencias del mapa: mercado, hospital (todos los establecimientos de salud), universidad,
        terminal, plaza, escuela, banco, supermercado

Solo guarda los puntos que caen dentro del rectángulo de algún municipio del departamento.
Uso: python codigo/dep_0_capas_pbf.py Cochabamba ruta/a/bolivia-latest.osm.pbf
"""
import json, re, sys
from pathlib import Path
import osmium

DEP = sys.argv[1] if len(sys.argv) > 1 else 'Cochabamba'
PBF = sys.argv[2] if len(sys.argv) > 2 else 'bolivia-latest.osm.pbf'
RAIZ = Path(__file__).resolve().parent.parent
F = RAIZ / 'datos_osm' / DEP.lower() / f'osm_{DEP.lower()}.json'
MUNS = json.load(open(RAIZ / 'datos' / DEP.lower() / 'municipios.json'))['municipios']
BOX = [m['bounds'] for m in MUNS]  # oeste, sur, este, norte


def en_dep(lat, lon, pad=.005):
    return any(b[1] - pad <= lat <= b[3] + pad and b[0] - pad <= lon <= b[2] + pad for b in BOX)


GOMERIA = re.compile(r'gomer[ií]a|llanter[ií]a|vulcaniz', re.I)
HOSP = re.compile(r'hospital|cl[ií]nica|policl[ií]nic', re.I)
POSTA = re.compile(r'\bposta\b|puesto de salud|^p\.\s?s\.?\s|^ps\s', re.I)
CSALUD = re.compile(r'centro de salud|^c\.\s?s\.?\s|^cs\s', re.I)
ALOJ = re.compile(r'^(alojamiento|hostal|hotel|residencial|apart ?hotel)\b', re.I)


def clasificar(t):
    """Devuelve (capas de comp, capas de lm) para un objeto con etiquetas t."""
    a, nm = t.get('amenity', ''), t.get('name', '')
    comp, lm = [], []
    sh, le, cr = t.get('shop', ''), t.get('leisure', ''), t.get('craft', '')
    for k, ok in (('farmacia', a == 'pharmacy'), ('gimnasio', le == 'fitness_centre'),
                  ('peluqueria', sh in ('hairdresser', 'beauty')), ('libreria', sh in ('books', 'stationery')),
                  ('guarderia', a in ('kindergarten', 'childcare')), ('ferreteria', sh in ('hardware', 'doityourself')),
                  ('lavanderia', sh in ('laundry', 'dry_cleaning')), ('veterinaria', a == 'veterinary' or sh == 'pet'),
                  ('dentista', a == 'dentist' or t.get('healthcare') == 'dentist'),
                  ('taller', sh in ('car_repair', 'tyres', 'car_parts') or cr == 'mechanic')):
        if ok: comp.append(k)
    if a == 'marketplace': lm.append('mercado')
    if a in ('university', 'college'): lm.append('universidad')
    if a == 'bus_station' or (t.get('public_transport') == 'station' and t.get('railway') is None):
        lm.append('terminal')
    if t.get('place') == 'square' or (nm and re.match(r'plaz(a|uela)\b', nm, re.I) and le == 'park'):
        lm.append('plaza')
    if a == 'bank': lm.append('banco')
    if sh == 'supermarket': lm.append('supermercado')
    if a == 'atm' or (a == 'bank' and t.get('atm') == 'yes'): comp.append('cajero')
    if a == 'fuel': comp.append('gasolinera')
    if t.get('shop') == 'tyres' or t.get('craft') == 'tyre' or (nm and GOMERIA.search(nm)): comp.append('gomeria')
    if a in ('restaurant', 'fast_food'): comp.append('restaurante')
    if t.get('tourism') in ('hotel', 'hostel', 'motel', 'guest_house') or \
            (nm and ALOJ.search(nm) and (t.get('building') or t.get('amenity') or t.get('tourism') or t.get('shop'))):
        if t.get('landuse') is None and t.get('place') is None: comp.append('hotel')
    hc = t.get('healthcare', '')
    salud = a in ('hospital', 'clinic') or hc in ('hospital', 'clinic', 'centre') or (nm and (POSTA.search(nm) or CSALUD.search(nm)) and (a or hc or t.get('building')))
    if salud:
        lm.append('hospital')
        if nm and POSTA.search(nm): comp.append('posta')
        elif nm and CSALUD.search(nm): comp.append('centro_salud')
        elif a == 'hospital' or hc == 'hospital' or (nm and HOSP.search(nm)): comp.append('hospital_clinica')
        else: comp.append('centro_salud')
    if a == 'school': lm.append('escuela')
    return comp, lm


class H(osmium.SimpleHandler):
    def __init__(self):
        super().__init__(); self.comp = {}; self.lm = {}; self.vistos = set()

    def add(self, oid, lat, lon, t):
        if not en_dep(lat, lon): return
        comp, lm = clasificar(t)
        nm = t.get('name', '') or t.get('brand', '') or t.get('operator', '') if comp else t.get('name', '')
        for k in comp:
            if (k, oid) in self.vistos: continue
            self.vistos.add((k, oid)); self.comp.setdefault(k, []).append([round(lat, 5), round(lon, 5), nm])
        for k in lm:
            if (k, oid) in self.vistos: continue
            self.vistos.add((k, oid))
            self.lm.setdefault(k, []).append([t.get('name', ''), round(lat, 5), round(lon, 5)])

    def node(self, n):
        if not n.tags or not n.location.valid(): return
        t = dict(n.tags)
        if any(clasificar(t)): self.add('n' + str(n.id), n.location.lat, n.location.lon, t)

    def way(self, w):
        if not w.tags: return
        t = dict(w.tags)
        if 'highway' in t or not any(clasificar(t)): return
        pts = [(nd.lat, nd.lon) for nd in w.nodes if nd.location.valid()]
        if pts: self.add('w' + str(w.id), sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts), t)

    def area(self, ar):
        if ar.from_way() or not ar.tags: return  # las vías cerradas ya se cuentan en way()
        t = dict(ar.tags)
        if not any(clasificar(t)): return
        pts = [(n.lat, n.lon) for ring in ar.outer_rings() for n in ring if n.location.valid()]
        if pts: self.add('r' + str(ar.orig_id()), sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts), t)


h = H()
h.apply_file(PBF, locations=True)
osm = json.load(open(F))
for k, v in sorted(h.comp.items()):
    osm['comp'][k] = v
    print(f'comp {k:18s} {len(v):5d}')
for k in ('mercado', 'hospital', 'universidad', 'terminal', 'plaza', 'escuela', 'banco', 'supermercado'):
    v = [p for p in h.lm.get(k, []) if p[0]]  # las referencias del mapa necesitan nombre
    print(f'lm   {k:18s} {len(osm["lm"].get(k, [])):5d} -> {len(v):5d}')
    osm['lm'][k] = v
osm['fecha_capas_pbf'] = re.search(r'(\d{6})', Path(PBF).name).group(1) if re.search(r'(\d{6})', Path(PBF).name) else ''
json.dump(osm, open(F, 'w'), separators=(',', ':'), ensure_ascii=False)
print(f'Guardado {F}')
