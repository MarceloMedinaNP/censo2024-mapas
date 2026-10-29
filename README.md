# Mapas y Censo 2024 · Bolivia

Convertir el Censo de Población y Vivienda 2024 en herramientas para decidir: dónde abrir un negocio, dónde encontrar uno y qué necesita cada barrio o calle.

Actualizado: 28 de octubre de 2026 · Responsable: Marcelo (ThinkingIA)

## Lo que ya existe

| Pieza | Estado | Dónde está |
| --- | --- | --- |
| Mapa "Oportunidades Cochabamba": 47 municipios, por zona, tramo de calle y manzano; 10 rubros; recorrido guiado y chat "Pregúntale al mapa" | Versión 5 | https://claude.ai/artifact/Bj2BxLaru6nDurqkJc6FUa |
| Versión pública del mapa (sin chat, con mapa base) | Lista en `docs/` del repositorio; falta activar GitHub Pages | https://marcelomedinanp.github.io/censo2024-mapas/ (ver `documentacion/guia-de-uso.md`) |
| Mapa "Dónde abrir en Cochabamba" (solo municipio de Cochabamba, primera versión) | Versión 5 | https://claude.ai/artifact/5WmMDo4ZkLD6c3tQXSZVfD |
| Prompt maestro para replicarlo en otra ciudad o rubro | Versión 1 | https://claude.ai/artifact/6HULaFQTyjyxaC6fvrasit (copia en `documentacion/prompt-maestro.md`) |
| Repositorio con código, datos procesados y mapa | Al día | https://github.com/MarceloMedinaNP/censo2024-mapas |
| Resumen por municipio (planilla) | 47 municipios × 26 indicadores | Google Drive, carpeta "Censo 2024 · Mapas": https://docs.google.com/spreadsheets/d/1nJWreXXSkp6L7vaoYTnUeuV42D1NIOrzZFxv7le6Tk0 |
| Metodología y fuentes | Documentadas | `documentacion/metodologia.md`, `documentacion/fuentes-de-datos.md` |
| Guía de uso y guion de demostración | Lista | `documentacion/guia-de-uso.md` |

## Departamento de Cochabamba en cifras

- 1.602.131 personas en 41.016 manzanos de 47 municipios.
- 27.668 tramos de calle con ficha propia (de 34.765 tramos con nombre en OpenStreetMap), en 5.001 calles.
- El 70% de la población del departamento vive frente a una calle con nombre: 86% en el municipio de Cochabamba, alrededor de 65% en Sacaba y Quillacollo, y entre 15% y 30% en municipios como Sipe Sipe, Puerto Villarroel o Arbieto, donde OpenStreetMap tiene menos calles nombradas.
- Negocios registrados en OpenStreetMap: 517 talleres mecánicos y repuestos, 447 farmacias, 303 ferreterías, 252 peluquerías, 136 librerías, 127 consultorios dentales, 88 veterinarias, 80 guarderías, 67 gimnasios y 56 lavanderías (diez rubros).

## Cómo reconstruir

1. `git clone https://github.com/mauforonda/atlasurbano ~/atlasurbano` (censo por manzano).
2. `pip install pandas pyarrow geopandas shapely numpy`
3. Desde la carpeta del repositorio:
   - `python codigo/dep_1_censo.py Cochabamba` → indicadores por manzano, zona y municipio.
   - `python codigo/dep_2_calles.py Cochabamba` → ficha por tramo de calle (necesita `datos_osm/cochabamba/osm_cochabamba.json`).
   - `python codigo/construir_plantilla.py` → arma la plantilla del mapa.
   - `python codigo/dep_3_preparar_web.py Cochabamba` → versión para Claude en `salida/cochabamba/web/` y versión pública en `salida/cochabamba/publico/`.

Para otro departamento hace falta su extracto de OpenStreetMap: se genera en el navegador integrado de la app (consultas en `fuentes-de-datos.md`), se descarga y se adjunta al chat. Es el único paso manual.

## Hacia dónde va: tres aplicaciones

| App | Para quién | Qué responde | Estado |
| --- | --- | --- | --- |
| Localizador de oportunidades | Empresas que abren sucursales | ¿Dónde abro mi próximo local? | Departamento de Cochabamba a nivel de calle, publicado |
| Atlas municipal | Alcaldías, gobernaciones, ONG | ¿Cómo vive la gente en cada municipio, zona y calle? ¿Dónde están las brechas? | Los datos ya están listos; falta la vista propia |
| Buscador cercano | Personas en la calle | ¿Qué negocio de lo que busco tengo cerca? | Pendiente. La versión pública en GitHub Pages sí podría usar el GPS del celular |

## Decisiones tomadas

- Datos pesados y código: repositorio de GitHub. Google Drive: resúmenes livianos e informes. Proyecto de Claude: documentación.
- Primer departamento: Cochabamba. Primera app: el localizador a nivel de calle.

## Estructura del repositorio

| Carpeta | Contenido |
| --- | --- |
| `docs/` | **La página pública** (GitHub Pages sirve esta carpeta): `index.html` y un juego de archivos por municipio en `docs/datos/` |
| `web/cochabamba/` | La versión del mapa que se publica dentro de Claude (con chat); usa los mismos datos de `docs/datos/` |
| `codigo/` | `dep_1_censo.py`, `dep_2_calles.py`, `construir_plantilla.py`, `dep_3_preparar_web.py` y la plantilla del mapa; los pasos `1_` a `3_` son la primera versión, solo para el municipio de Cochabamba |
| `datos/cochabamba/` | Conteos por manzano, resumen por municipio y por calles |
| `datos_osm/` | Extractos de OpenStreetMap |
| `documentacion/` | Guía de uso, metodología, fuentes de datos y prompt maestro |

Datos del censo por manzano: [atlasurbano](https://github.com/mauforonda/atlasurbano) (INE, Censo 2024). OpenStreetMap: © colaboradores de OpenStreetMap, licencia ODbL. Mapa base de la versión pública: © CARTO.
