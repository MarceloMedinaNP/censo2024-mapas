# Prompt maestro: Localizador de negocios con el Censo 2024

Versión 1, 28 de octubre de 2026. Documento editable con notas de uso: https://claude.ai/artifact/6HULaFQTyjyxaC6fvrasit

Para usarlo, cambia los valores entre corchetes de PARÁMETROS y pégalo en una conversación nueva de este proyecto. El navegador integrado de la app de escritorio debe estar abierto para las consultas a OpenStreetMap.

```text
# LOCALIZADOR DE NEGOCIOS · CENSO 2024 BOLIVIA

## ROL Y OBJETIVO
Actúa como analista geoespacial y de inteligencia de mercado. Construye una herramienta interactiva que le diga a un cliente DÓNDE abrir su próximo local en uno o varios municipios de Bolivia, combinando el Censo de Población y Vivienda 2024 a nivel de manzano con nombres de barrios, avenidas, lugares de referencia y la competencia existente de OpenStreetMap. El resultado debe servir para venderle el análisis a una empresa: claro, ubicable por nombres, justificable y honesto con sus límites.

## PARÁMETROS (edita antes de pegar)
- Municipios: [Cochabamba]
- Rubros: [farmacia, gimnasio, peluquería, librería o papelería, guardería o kínder, ferretería, lavandería]
- Cliente: [demo | nombre del cliente]
- Sucursales existentes del cliente: [ninguna | lista de direcciones o coordenadas]
- Entregables: [mapa interactivo | + informe del top 5 por rubro | + presentación comercial | + 5 hallazgos para publicar en redes]
- Marca: [ThinkingIA | colores del cliente]
- Si un parámetro queda vacío, usa el valor entre corchetes y dilo en una línea al empezar.

## FUENTES DE DATOS
1. Censo 2024 por manzano: repositorio público github.com/mauforonda/atlasurbano (clónalo con git, que sí está permitido).
   - datos/manzanos.parquet: polígono de cada manzano (departamento, municipio, codigo, geometry, WGS84).
   - datos/poblacion.parquet: personas y viviendas por manzano, y si tiene ficha completa (validado).
   - datos/fichas.parquet: ficha completa por manzano con edad por sexo (0–19, 20–39, 40–59, 60+), educación, salud (dónde se atiende, afiliación), lugar de nacimiento y residencia, ocupación, actividad económica, tipo y tenencia de vivienda, servicios (agua, desagüe, energía, combustible, basura), TIC, materiales de la vivienda, hacinamiento y tipo de hogar.
   - Los manzanos con pocas personas no tienen ficha por privacidad: cuentan en la población, pero no en los porcentajes. Reporta la cobertura.
2. OpenStreetMap vía Overpass (overpass-api.de). La terminal de la sesión no puede salir a ese dominio, así que usa el navegador integrado de la app: abre overpass-api.de, ejecuta las consultas con fetch dentro de la página y devuelve resultados compactos.
   - Barrios: place=neighbourhood|quarter|suburb con nombre.
   - Avenidas: highway=trunk|primary|secondary con nombre, unidas por nombre, simplificadas (Douglas-Peucker ~20 m) y codificadas como polilíneas (precisión 1e-4, cambiando la barra invertida por "!").
   - Referencias: plazas, terminal, universidades, hospitales, mercados y parques grandes.
   - Competencia por rubro: farmacia → amenity=pharmacy; gimnasio → leisure=fitness_centre; peluquería → shop=hairdresser|beauty; librería → shop=books|stationery; guardería → amenity=kindergarten|childcare; ferretería → shop=hardware|doityourself; lavandería → shop=laundry|dry_cleaning. Para un rubro nuevo, propón las etiquetas.
   - La cobertura de OSM es incompleta. Muestra cuántos negocios encontraste por rubro y ofrece reemplazarlos por una lista del cliente o de Google Places.

## FLUJO DE TRABAJO (con lista de tareas visible)
1. Confirma parámetros y supuestos en un mensaje corto. Pregunta solo si falta algo que cambie el resultado.
2. Datos censales: filtra los municipios, calcula conteos sumables por manzano (numerador y denominador de cada indicador) y el promedio municipal.
3. Zonas: grilla hexagonal de ~300 m de radio (~23 ha) en la zona UTM correcta (19S EPSG:32719 para La Paz, El Alto y Cochabamba; 20S EPSG:32720 para Santa Cruz). Asigna cada manzano a su hexágono por el centroide y descarta hexágonos con menos de 150 personas.
4. Nombres y competencia desde OSM. Cada zona y manzano toma el nombre del barrio más cercano a su centro; si está a más de 600 m, "cerca de …".
5. Puntajes por rubro, competencia y oportunidad (ver METODOLOGÍA).
6. Muéstrame en el chat el top 5 de cada rubro con nombre de barrio antes de construir la página, para validar que tiene sentido.
7. Construye y publica el mapa como artefacto. Luego los entregables extra.
8. Control de calidad (ver abajo) y cierre en 3 líneas.

## METODOLOGÍA
- Indicadores en %: 0–19, 20–39, 40–59 y 60+ años; educación superior; internet en el hogar; piso de cerámica o parquet; paredes sin revoque; hacinamiento alto; agua por cañería; alcantarillado; gas domiciliario; vivienda propia; alquiler o anticrético; caja de salud o seguro privado; sin seguro; acude a farmacia sin receta; empleados; cuenta propia; trabaja en comercio, enseñanza o construcción; hogares unipersonales; hogares con hijos (nuclear completo y monoparental).
- Poder adquisitivo = promedio de los percentiles de educación superior, internet, piso de calidad y caja o seguro privado. El censo no mide ingresos: dilo.
- Puntaje de demanda por rubro: cada variable se convierte en percentil entre zonas, se pondera con los pesos del perfil (las marcadas "menos es mejor" usan 1 − percentil), y el resultado se vuelve a ordenar de 0 a 100.
- Competencia: negocios del rubro en un radio de 800 m, por cada 10.000 habitantes en ese radio.
- Oportunidad = peso_d × percentil(demanda) + peso_c × (1 − percentil(competencia por habitante)), con peso_c editable (por defecto 35%).
- Si el cliente tiene sucursales, penaliza las zonas a menos de 1 km de ellas (canibalización) y muéstralo.
- Mercado potencial (opcional): personas del segmento objetivo en el radio × tasa de uso × gasto anual. Todo editable y marcado como supuesto.

## PERFILES DE NEGOCIO (pesos de 0 a 50; el usuario los ajusta en vivo)
- Farmacia: población 30, 60+ 25, acude a farmacia sin receta 15, poder adquisitivo 30.
- Gimnasio: 20–39 años 30, % 20–39 15, hogares unipersonales 15, poder adquisitivo 30, población 10.
- Peluquería: población 40, 20–39 años 20, hogares con hijos 15, poder adquisitivo 25.
- Librería o papelería: 0–19 años 40, % 0–19 15, trabaja en enseñanza 15, poder adquisitivo 15, población 15.
- Guardería o kínder: 0–19 años 25, hogares con hijos 25, empleados 20, poder adquisitivo 20, población 10.
- Ferretería: paredes sin revoque 30, trabaja en construcción 20, vivienda propia 20, población 20, poder adquisitivo 10 (menos es mejor).
- Lavandería: hogares unipersonales 30, alquiler 30, 20–39 años 20, población 20.
- Rubro nuevo: propone un perfil con 4 a 6 variables, explica cada peso en una línea y espera mi visto bueno.

## INTERFAZ DEL MAPA
- Panel lateral: buscador de barrios con autocompletado y sin acentos; selector de rubro; pesos con controles deslizantes y "Restablecer"; vistas Oportunidad / Demanda / Competencia / Indicador / Calor; leyenda; top 10 con nombre de barrio y los dos factores que más pesan; nota de método y fuentes.
- Mapa: manzanos como base, hexágonos coloreados, avenidas dibujadas, puntos de competencia con ícono por rubro, sucursales del cliente destacadas, etiquetas que aparecen por nivel de zoom (referencias principales desde el inicio, avenidas desde el zoom 14, barrios desde el 15,5).
- Al pasar el mouse: nombre del barrio junto al cursor y ficha a la derecha con población, viviendas, pirámide de edad por sexo, nivel educativo, salud, vivienda y servicios, trabajo y hogares, cada dato con ▲▼ frente al promedio municipal, y el puntaje de la zona para todos los rubros. Clic para fijarla, con contorno resaltado. Desde el zoom 15, ficha por manzano.
- Frase automática por zona con sus 2 o 3 rasgos más atípicos, por ejemplo "zona de inquilinos asalariados con servicios completos".
- Simulador "¿Y si abro aquí?": clic en un punto, radio de 500 o 1.000 m; muestra personas y segmento objetivo, competidores y el más cercano, sucursales propias cercanas y mercado potencial.
- Comparador: hasta 3 zonas fijadas, lado a lado.
- Enlace compartible: la zona fijada va en el hash de la URL (#z-123).
- Selector de municipio si hay más de uno.
- Funciona en celular: mapa arriba, ficha y panel abajo. Tema claro y oscuro.

## RESTRICCIONES TÉCNICAS DEL ARTEFACTO
- Leaflet 1.9.4 desde cdnjs y leaflet.heat 0.2.0 desde jsdelivr. El CSS de Leaflet va en línea, sin imágenes externas.
- Sin teselas de mapa de fondo: el bloqueo de contenido externo las impide. Los manzanos, las avenidas y las etiquetas cumplen esa función.
- Datos embebidos en la página, compactos (arreglos con un orden de claves, coordenadas a 5 decimales), con un total por debajo de 16 MB.
- Dibujo en canvas. La interactividad de hexágonos y manzanos se alterna según el zoom.
- Archivos descargados en carpetas propias; Python con -I.

## CONTROL DE CALIDAD (antes de entregar)
- La población total y los manzanos cuadran con el INE; la cobertura de fichas queda reportada.
- Los promedios municipales son razonables (internet, agua, edad).
- Cada perfil da un top distinto y defendible (la ferretería no debe salir en el centro).
- Prueba en código de la función de puntaje y verificación de sintaxis de la página.
- Las coordenadas de OSM caen dentro del municipio.

## ENTREGA
- Mapa publicado como artefacto, con una línea de resumen.
- Si se pidió: informe en documento con el top 5 por rubro, ficha y mapa de cada zona, método y límites; presentación de 8 a 10 diapositivas para vender el servicio; 5 hallazgos atípicos redactados para LinkedIn y Dato Crudo.
- Límites a decir siempre: el censo mide dónde vive la gente, no dónde trabaja ni por dónde pasa; no mide ingresos; las edades vienen en tramos de 20 años; OSM puede tener barrios y negocios incompletos.
```
