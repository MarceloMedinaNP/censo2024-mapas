# Metodología del mapa de oportunidades

Cómo pasa el mapa de manzanos del censo a un puntaje de oportunidad por zona y por rubro. Versión aplicada en el mapa del municipio de Cochabamba (v5) y en el mapa departamental "Oportunidades Cochabamba" (octubre 2026).

## 1. Unidad de análisis

- **Manzano**: unidad más fina del Censo 2024 publicada por el INE. Los manzanos con pocas personas no tienen ficha completa por privacidad: suman a la población, pero no a los porcentajes. En Cochabamba la cobertura es 95,4% de la población.
- **Zona**: grilla hexagonal de 300 m de radio (~23 ha) en coordenadas UTM. Cada manzano va a la zona donde cae su centroide. Se descartan zonas con menos de 150 personas. Zona UTM: 19S (EPSG:32719) para La Paz, El Alto y Cochabamba; 20S (EPSG:32720) para Santa Cruz.
- **Nombre**: cada zona y manzano toma el barrio de OpenStreetMap más cercano a su centro; a más de 600 m se muestra "cerca de …".

- **Tramo de calle** (mapa departamental): cada calle con nombre de OpenStreetMap se corta en tramos de esquina a esquina. Un tramo suma los manzanos que le dan frente: al menos 15 m del borde del manzano a menos de 25 m del eje de la calle. Un manzano en esquina cuenta para varias calles, así que los tramos no se suman entre sí. Los tramos sin manzanos de frente no tienen ficha.
- **Municipio**: en el mapa departamental, los percentiles y los promedios de comparación (▲▼) se calculan dentro de cada municipio, no del departamento.

## 2. Indicadores

Todos se calculan como numerador / denominador sumados, de modo que se pueden agregar a cualquier escala (manzano, zona, calle, municipio).

| Indicador | Numerador | Denominador |
| --- | --- | --- |
| % 0–19, 20–39, 40–59, 60+ años | personas del tramo | personas con ficha |
| % educación superior | personas con nivel superior | personas con nivel declarado |
| % hogares con internet | hogares con internet | hogares |
| % piso de cerámica, parquet o flotante | viviendas | viviendas con piso declarado |
| % paredes sin revoque | viviendas | viviendas con revoque declarado |
| % hacinamiento alto | hogares | hogares |
| % agua por cañería, alcantarillado, gas domiciliario | viviendas | viviendas con dato |
| % vivienda propia; % alquiler o anticrético | viviendas | viviendas con tenencia declarada |
| % caja de salud o seguro privado; % sin seguro | personas | personas con afiliación declarada |
| % acude a farmacia sin receta | personas | personas con ficha |
| % empleados; % cuenta propia | ocupados | ocupados |
| % comercio, enseñanza, construcción | ocupados en la actividad | ocupados con actividad |
| % hogares unipersonales; % con hijos (nuclear completo y monoparental) | hogares | hogares |

**Poder adquisitivo** = promedio de los percentiles de educación superior, internet, piso de calidad y caja o seguro privado. El censo no pregunta ingresos; es una aproximación.

## 3. Puntajes

1. **Demanda por rubro**: cada variable del perfil se convierte en percentil entre las zonas. Se pondera con los pesos del perfil (las marcadas "menos es mejor" usan 1 − percentil) y el resultado se vuelve a ordenar de 0 a 100.
2. **Competencia**: negocios del rubro a 800 m del centro de la zona, por cada 10.000 habitantes dentro de ese radio.
3. **Oportunidad** = (1 − p) × percentil(demanda) + p × (1 − percentil(competencia por habitante)), con p = 35% por defecto y editable en el mapa. El resultado se reordena de 0 a 100.
4. **Oportunidad de un tramo de calle**: la demanda del tramo se ordena contra los demás tramos del municipio, y la competencia es la de la zona donde cae el punto medio del tramo.

Un puntaje de 90 significa que la zona supera al 90% de las demás para ese rubro.

## 4. Perfiles de rubro (pesos de 0 a 50)

| Rubro | Variables y pesos |
| --- | --- |
| Farmacia | población 30, 60+ 25, acude a farmacia sin receta 15, poder adquisitivo 30 |
| Gimnasio | 20–39 años 30, % 20–39 15, hogares unipersonales 15, poder adquisitivo 30, población 10 |
| Peluquería | población 40, 20–39 años 20, hogares con hijos 15, poder adquisitivo 25 |
| Librería o papelería | 0–19 años 40, % 0–19 15, trabaja en enseñanza 15, poder adquisitivo 15, población 15 |
| Guardería o kínder | 0–19 años 25, hogares con hijos 25, empleados 20, poder adquisitivo 20, población 10 |
| Ferretería | paredes sin revoque 30, trabaja en construcción 20, vivienda propia 20, población 20, poder adquisitivo 10 (menos es mejor) |
| Lavandería | hogares unipersonales 30, alquiler o anticrético 30, 20–39 años 20, población 20 |
| Veterinaria | población 25, vivienda propia 25, hogares con hijos 20, poder adquisitivo 30 (el censo no pregunta por mascotas: casas propias y familias con hijos son la aproximación) |
| Consultorio dental | población 30, poder adquisitivo 30, caja de salud o seguro privado 15, 0–19 años 10, 40 años o más 15 |

## 5. Límites que hay que decir siempre

- El censo dice dónde vive la gente, no dónde trabaja ni por dónde pasa.
- No mide ingresos; las edades vienen en tramos de 20 años.
- OpenStreetMap no tiene todos los barrios ni todos los negocios. En Cochabamba registra 405 farmacias, 258 ferreterías, 244 peluquerías, 121 librerías, 73 guarderías, 63 gimnasios y 54 lavanderías; la cifra real es mayor.
- Los nombres de barrio son de OpenStreetMap, no los oficiales de la Alcaldía.
