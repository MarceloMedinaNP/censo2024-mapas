# Fuentes de datos

Qué datos usa el proyecto, de dónde salen y cómo se descargan. Revisado el 28 de octubre de 2026.

## Censo 2024 (INE)

| Fuente | Nivel | Qué trae | Acceso |
| --- | --- | --- | --- |
| atlasurbano (M. Foronda), github.com/mauforonda/atlasurbano | Manzano, todo el país | `manzanos.parquet` (247.429 polígonos), `poblacion.parquet` (personas y viviendas), `fichas.parquet` (131.801 fichas completas con 171 campos) | `git clone`; funciona desde la terminal de la sesión |
| Geoportal del INE, idg.ine.gob.bo | Manzano | Ficha oficial por manzano (origen de atlasurbano) | Consulta manzano por manzano |
| Base de datos del Censo 2024, censo.ine.gob.bo (Descargas) | Microdatos | CSV de 413 MB y bases Redatam; metadatos en anda.ine.gob.bo/index.php/catalog/132 | Descarga directa; sirve para indicadores municipales completos, incluido el área rural dispersa sin manzanos |

Las fichas por manzano cubren el 89,5% de la población nacional. El área rural dispersa no tiene manzanos: para ella se usarán los microdatos a nivel municipal.

## OpenStreetMap (Overpass API)

La terminal de la sesión no puede conectarse a overpass-api.de. Las consultas se ejecutan desde el navegador integrado de la app de escritorio: se abre overpass-api.de y se lanza `fetch('/api/interpreter', {method:'POST', body:'data='+encodeURIComponent(q)})` dentro de la página. Los resultados se comprimen antes de traerlos (polilíneas con precisión 1e-4, donde "!" reemplaza a la barra invertida).

Caja usada para el municipio de Cochabamba (sur, oeste, norte, este): `-17.53,-66.29,-17.32,-66.07`.

| Archivo en `datos_osm/` | Consulta Overpass | Resultado en Cochabamba |
| --- | --- | --- |
| `osm_places.json` | `node["place"~"suburb\|neighbourhood\|quarter"]["name"]` | 568 barrios y 8 zonas grandes |
| `osm_roads.json` | `way["highway"~"^(trunk\|primary\|secondary)$"]["name"]`, unidas por nombre y simplificadas a 20 m | 121 avenidas |
| `osm_landmarks.json` | plazas, terminal, universidades, hospitales, mercados y parques grandes (selección manual de 46) | 46 referencias |
| `osm_comp.json` | negocios por rubro, ver tabla siguiente | 1.218 negocios |

| Rubro | Etiquetas OSM |
| --- | --- |
| Farmacia | `amenity=pharmacy` |
| Gimnasio | `leisure=fitness_centre` |
| Peluquería | `shop=hairdresser\|beauty` |
| Librería o papelería | `shop=books\|stationery` |
| Guardería o kínder | `amenity=kindergarten\|childcare` |
| Ferretería | `shop=hardware\|doityourself` |
| Lavandería | `shop=laundry\|dry_cleaning` |
| Veterinaria | `amenity=veterinary`, `shop=pet` (88 en el departamento) |
| Consultorio dental | `amenity=dentist`, `healthcare=dentist` (127 en el departamento) |
| Taller mecánico | `shop=car_repair\|tyres\|car_parts`, `craft=mechanic` (517 en el departamento) |

### Extracto departamental (Cochabamba, 28 de octubre de 2026)

`datos_osm/cochabamba/osm_cochabamba.json` (2,1 MB) se generó en el navegador integrado con una consulta por cada uno de los 47 rectángulos que cubren los manzanos de cada municipio:

- Calles: `way["highway"]["name"]`, excepto senderos, escaleras, ciclovías y vías en construcción. Se cortan en tramos en los nodos que comparten dos o más calles, se simplifican a 3 m y se codifican como polilíneas con precisión 1e-5. Resultado: 34.765 tramos de 5.151 calles.
- Lugares: `place` = suburb, neighbourhood, quarter, village, town, city, hamlet (3.287).
- Negocios por rubro, con las etiquetas de la tabla anterior.
- Referencias: mercados, hospitales y clínicas, universidades, terminales, plazas, escuelas, bancos y supermercados.

El archivo se descarga desde el navegador y se adjunta al chat: es la única forma de pasarlo al espacio de trabajo, porque la terminal no llega a Overpass. El servidor público suele estar saturado; el script reintenta con espera creciente.

### Mapa base dibujado (Cochabamba, 29 de octubre de 2026)

`datos_osm/cochabamba/osm_base_cochabamba.json` (3,3 MB). Dentro de Claude el mapa no puede cargar teselas externas, así que el fondo se dibuja con datos de OpenStreetMap: 15.462 cuerpos de agua, 14.252 ríos, canales y torrenteras (204 con nombre), 6.619 áreas verdes, 960 bosques, 6.358 parcelas de cultivo, 42.827 calles sin nombre, 392 tramos de vía férrea, 6 aeródromos y 118 cerros con altura.

Se descargó con una consulta por municipio (las 28 más pequeñas agrupadas de a 6). En los municipios de más de 0,04 grados² se omitieron bosques, cultivos y arroyos para no superar los límites del servidor. Simplificación: 3 m en calles, 5 m en agua y ríos, 12 m en bosques y cultivos; se descartan áreas verdes de menos de 300 m² y bosques o cultivos de menos de 3.000 m². El paso `dep_3_preparar_web.py` lo recorta por municipio (`*.base.json`). La versión pública usa teselas de OpenStreetMap en su lugar.

## Alternativas para negocios

- **Google Places API**: mucho más completa que OSM, pero cobra por consulta y sus condiciones limitan guardar los datos.
- **Lista del cliente**: sucursales propias y competidores que el cliente ya conoce.
- **Registro propio**: que los negocios se den de alta en la app (útil para el buscador cercano).
