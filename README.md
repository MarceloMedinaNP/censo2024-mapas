# Mapas y Censo 2024 · Bolivia

Convertir el Censo de Población y Vivienda 2024 en herramientas para decidir: dónde abrir un negocio, dónde encontrar uno y qué necesita cada barrio o calle.

Actualizado: 28 de octubre de 2026 · Responsable: Marcelo (ThinkingIA)

## Lo que ya existe

| Pieza | Estado | Dónde está |
| --- | --- | --- |
| Mapa "Oportunidades Cochabamba": 47 municipios del departamento, por zona, tramo de calle y manzano | Versión 1 | https://claude.ai/artifact/Bj2BxLaru6nDurqkJc6FUa |
| Mapa "Dónde abrir en Cochabamba" (solo municipio de Cochabamba, primera versión) | Versión 5 | https://claude.ai/artifact/5WmMDo4ZkLD6c3tQXSZVfD |
| Prompt maestro para replicarlo en otra ciudad o rubro | Versión 1 | https://claude.ai/artifact/6HULaFQTyjyxaC6fvrasit (copia en `prompt-maestro.md`) |
| Repositorio con código, datos procesados y mapa | Al día | https://github.com/MarceloMedinaNP/censo2024-mapas |
| Metodología y fuentes | Documentadas | `metodologia.md`, `fuentes-de-datos.md` |

## Departamento de Cochabamba en cifras

- 1.602.131 personas en 41.016 manzanos de 47 municipios.
- 27.668 tramos de calle con ficha propia (de 34.765 tramos con nombre en OpenStreetMap), en 5.001 calles.
- El 70% de la población del departamento vive frente a una calle con nombre: 86% en el municipio de Cochabamba, alrededor de 65% en Sacaba y Quillacollo, y entre 15% y 30% en municipios como Sipe Sipe, Puerto Villarroel o Arbieto, donde OpenStreetMap tiene menos calles nombradas.
- Negocios registrados en OpenStreetMap: 447 farmacias, 303 ferreterías, 252 peluquerías, 136 librerías, 80 guarderías, 67 gimnasios y 56 lavanderías.

## Cómo reconstruir

1. `git clone https://github.com/mauforonda/atlasurbano ~/atlasurbano` (censo por manzano).
2. `pip install pandas pyarrow geopandas shapely numpy`
3. Desde la carpeta del repositorio:
   - `python codigo/dep_1_censo.py Cochabamba` → indicadores por manzano, zona y municipio.
   - `python codigo/dep_2_calles.py Cochabamba` → ficha por tramo de calle (necesita `datos_osm/cochabamba/osm_cochabamba.json`).
   - `python codigo/dep_3_preparar_web.py Cochabamba` → página y datos en `salida/cochabamba/web/`.

Para otro departamento hace falta su extracto de OpenStreetMap: se genera en el navegador integrado de la app (consultas en `fuentes-de-datos.md`), se descarga y se adjunta al chat. Es el único paso manual.

## Hacia dónde va: tres aplicaciones

| App | Para quién | Qué responde | Estado |
| --- | --- | --- | --- |
| Localizador de oportunidades | Empresas que abren sucursales | ¿Dónde abro mi próximo local? | Departamento de Cochabamba a nivel de calle, publicado |
| Atlas municipal | Alcaldías, gobernaciones, ONG | ¿Cómo vive la gente en cada municipio, zona y calle? ¿Dónde están las brechas? | Los datos ya están listos; falta la vista propia |
| Buscador cercano | Personas en la calle | ¿Qué negocio de lo que busco tengo cerca? | Pendiente: las páginas publicadas no leen el GPS; requiere marcar la ubicación en el mapa o una app aparte |

## Decisiones tomadas

- Datos pesados y código: repositorio de GitHub. Google Drive: resúmenes livianos e informes. Proyecto de Claude: documentación.
- Primer departamento: Cochabamba. Primera app: el localizador a nivel de calle.

## Estructura del repositorio

| Carpeta | Contenido |
| --- | --- |
| `codigo/` | `dep_1_censo.py`, `dep_2_calles.py`, `dep_3_preparar_web.py` y la plantilla del mapa departamental; los pasos `1_` a `3_` son la primera versión, solo para el municipio de Cochabamba |
| `datos/cochabamba/` | Conteos por manzano (`conteos_manzano.parquet`), resumen por municipio y por calles |
| `datos_osm/` | Extractos de OpenStreetMap (departamento y primera versión municipal) |
| `web/cochabamba/` | El mapa publicado: `index.html` y un juego de archivos por municipio (`*.mun.json`, `*.calles.json`, `*.osm.json`) |
| `docs/` | Metodología, fuentes de datos y prompt maestro |

Datos del censo por manzano: [atlasurbano](https://github.com/mauforonda/atlasurbano) (INE, Censo 2024). OpenStreetMap: © colaboradores de OpenStreetMap, licencia ODbL.
