"""Paso 3: agrega la competencia (negocios de OpenStreetMap) y arma la página final del mapa.

Uso, desde la carpeta del proyecto:
    python codigo/1_procesar_censo.py        # censo por manzano -> salida/data2.json
    python codigo/2_agregar_nombres_osm.py   # barrios, avenidas y referencias -> salida/data3.json
    python codigo/3_construir_mapa.py        # competencia + plantilla -> salida/mapa.html
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAL = RAIZ / 'salida'


def decode(s):
    """Decodifica una polilínea (precisión 1e-4; '!' reemplaza a la barra invertida)."""
    s = s.replace('!', '\\'); i = 0; lat = lon = 0; out = []
    while i < len(s):
        v = []
        for _ in range(2):
            sh = res = 0
            while True:
                b = ord(s[i]) - 63; i += 1; res |= (b & 0x1f) << sh; sh += 5
                if b < 0x20: break
            v.append(~(res >> 1) if res & 1 else res >> 1)
        lat += v[0]; lon += v[1]; out.append([lat / 1e4, lon / 1e4])
    return out


d = json.load(open(SAL / 'data3.json'))
comp = json.load(open(RAIZ / 'datos_osm' / 'osm_comp.json'))
d['comp'] = {k: decode(s) for k, s in comp.items()}

html = (RAIZ / 'codigo' / 'plantilla_mapa.html').read_text()
html = html.replace('/*LEAFLETCSS*/', (RAIZ / 'codigo' / 'leaflet.css').read_text())
html = html.replace('/*DATA*/', json.dumps(d, separators=(',', ':'), ensure_ascii=False))
(SAL / 'mapa.html').write_text(html)
print('Mapa listo:', SAL / 'mapa.html', f'({len(html) / 1e6:.1f} MB)',
      '| negocios:', {k: len(v) for k, v in d['comp'].items()})
