# Mapas y Censo 2024 · Bolivia

Convertir el Censo de Población y Vivienda 2024 en herramientas para decidir: dónde abrir un negocio, dónde encontrar uno y qué necesita cada barrio o calle.

Actualizado: 28 de octubre de 2026 · Responsable: Marcelo (ThinkingIA)

## Lo que ya existe

| Pieza | Estado | Dónde está |
| --- | --- | --- |
| Mapa "Dónde abrir en Cochabamba" (municipio de Cochabamba) | Versión 5, funcionando | https://claude.ai/artifact/5WmMDo4ZkLD6c3tQXSZVfD |
| Prompt maestro para replicarlo en otra ciudad o rubro | Versión 1 | https://claude.ai/artifact/6HULaFQTyjyxaC6fvrasit (copia en `prompt-maestro.md`) |
| Código del flujo de datos (3 pasos) | Probado: reconstruye el mapa idéntico | carpeta `codigo/` |
| Datos de OpenStreetMap ya descargados (barrios, avenidas, referencias, competencia) | Cochabamba, octubre 2026 | carpeta `datos_osm/` |
| Metodología y fuentes | Documentadas | `metodologia.md`, `fuentes-de-datos.md` |

El mapa cubre 665.482 personas en 12.477 manzanos (95,4% con ficha completa), agrupados en 646 zonas de unas 23 hectáreas. Para 7 rubros calcula demanda, competencia en 800 m y oportunidad, con nombres de 557 barrios, 121 avenidas y 46 lugares de referencia.

## Cómo reconstruir el mapa

1. Clonar los datos del censo por manzano en la carpeta de inicio: `git clone https://github.com/mauforonda/atlasurbano ~/atlasurbano`
2. Instalar dependencias: `pip install pandas pyarrow geopandas shapely numpy`
3. Desde la carpeta del proyecto, con una subcarpeta `salida/` creada:
   - `python codigo/1_procesar_censo.py` → indicadores por manzano y por zona
   - `python codigo/2_agregar_nombres_osm.py` → barrios, avenidas y referencias
   - `python codigo/3_construir_mapa.py` → competencia y página final `salida/mapa.html`

Para otro municipio se cambia el filtro `m.municipio == 'Cochabamba'` del paso 1 y se descargan sus datos de OpenStreetMap (consultas en `fuentes-de-datos.md`).

## Hacia dónde va: tres aplicaciones

| App | Para quién | Qué responde | Base que ya tenemos |
| --- | --- | --- | --- |
| Localizador de oportunidades | Empresas que abren sucursales | ¿Dónde abro mi próximo local? | El mapa actual, ampliado a todo el departamento y a nivel de calle |
| Buscador cercano | Personas en la calle | ¿Qué negocio de lo que busco tengo cerca? | Negocios de OpenStreetMap; falta la ubicación del usuario y más negocios |
| Atlas municipal | Alcaldías, gobernaciones, ONG | ¿Cómo vive la gente en cada municipio, zona y calle? ¿Dónde están las brechas? | Todos los indicadores del censo por manzano |

## Nivel de calle: es posible, con un matiz

El dato más fino que publica el INE es el manzano. Una calle se arma sumando los manzanos que dan a ella: cada tramo de calle (entre dos esquinas) toma los manzanos de ambos lados que están a menos de ~15 m. Así se obtiene una ficha por tramo, del tipo "Av. Ayacucho entre Heroínas y Colombia: N personas, X% mayores de 60" (ejemplo ilustrativo, aún sin calcular). Las calles con nombre salen de OpenStreetMap; no hace falta Google Street View.

## Decisiones pendientes

- Dónde guardar los datos pesados (el proyecto admite 2 MB en total; los datos del censo por manzano de todo el país ya pesan unos 60 MB y las calles de un departamento sumarán decenas de MB más).
- Con qué departamento seguir después de Cochabamba.
- Si el buscador cercano usará Google Places (más completo, con costo por consulta y condiciones de uso) u OpenStreetMap más un registro propio de negocios.

## Estructura del repositorio

| Carpeta | Contenido |
| --- | --- |
| `codigo/` | Pasos 1–3 del mapa municipal; `dep_1_censo.py` y `dep_2_calles.py` para un departamento completo |
| `datos/cochabamba/` | Censo procesado del departamento: un archivo por municipio (`mun_*.json`), resumen municipal y conteos por manzano |
| `datos_osm/` | Extractos de OpenStreetMap ya comprimidos |
| `docs/` | Metodología, fuentes de datos y prompt maestro |

Los datos del censo por manzano vienen de [atlasurbano](https://github.com/mauforonda/atlasurbano) (INE, Censo 2024). Los de OpenStreetMap se distribuyen bajo licencia ODbL.
