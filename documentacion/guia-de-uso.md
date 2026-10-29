# Guía de uso y guion de demostración

Cómo usar el mapa "Oportunidades Cochabamba" y cómo mostrarlo en una reunión en unos 5 minutos. Actualizado: 29 de octubre de 2026.

## Dónde abrirlo

| Versión | Para quién | Qué tiene | Enlace |
| --- | --- | --- | --- |
| Dentro de Claude | Tú y quienes compartas desde el menú Compartir | Todo, incluido el chat "Pregúntale al mapa" | https://claude.ai/artifact/Bj2BxLaru6nDurqkJc6FUa |
| Pública (GitHub Pages) | Cualquiera con el enlace, sin cuenta | Todo menos el chat; agrega mapa base con calles | https://marcelomedinanp.github.io/censo2024-mapas/ (después de activarla, ver abajo) |

El enlace guarda el municipio: `…#sacaba`, `…#quillacollo`, etc.

## Las otras dos versiones

| Versión | Para quién | Dentro de Claude | Pública |
| --- | --- | --- | --- |
| Atlas municipal | Alcaldías, gobernación, ONG | https://claude.ai/artifact/GdZiYtT57Y9XVEPuZuQ8ZX | https://marcelomedinanp.github.io/censo2024-mapas/atlas/ |
| Buscador cercano | Público en general | https://claude.ai/artifact/5MZ3pJeBmExrn1kHrif1QB | https://marcelomedinanp.github.io/censo2024-mapas/cerca/ |

**Atlas municipal (demostración de 3 minutos).** Elegir el tema Servicios y el indicador agua por cañería: el mapa pinta la brecha, más oscuro es peor. El ranking "Dónde está la mayor brecha" lista los barrios con más personas sin agua (o, con el botón %, los de mayor porcentaje). Tocar el primero: la ficha compara 30 indicadores con el municipio y el departamento (▼ marca 10 puntos o más peor) y, abajo, cuenta la población, las personas sin agua o sin seguro, y los centros de salud, escuelas y mercados en un radio de 500 m, 1 km o 2 km. "Descargar ficha (CSV)" baja todo para un informe. Acercándose, cada manzano se pinta por separado.

**Buscador cercano.** Elegir qué se busca (farmacia, centro de salud, dentista, veterinaria, taller, mercado, banco y otros 11), y luego "Mi ubicación", escribir un barrio o calle, o tocar el mapa; el punto azul se puede arrastrar. La lista muestra los 10 más cercanos con distancia, tiempo aproximado y "Cómo llegar" (abre la ruta en Google Maps). El GPS del celular funciona en la versión pública; dentro de Claude no hay acceso a la ubicación. El enlace guarda la búsqueda: `…/cerca/#farmacia/-17.39350,-66.15700`.

## El recorrido guiado

El botón **Recorrido guiado** recorre 14 pasos y en cada uno hace la acción en el mapa. Se avanza con "Siguiente" o con las flechas del teclado; Esc lo cierra. Es la forma más rápida de mostrar la herramienta a alguien.

## Guion de demostración (5 minutos)

1. **El problema** (30 s). "Una cadena quiere abrir su próxima farmacia. ¿Dónde? Este mapa cruza el Censo 2024 manzano por manzano con los negocios que ya existen."
2. **Vista general** (30 s). Municipio Cochabamba, rubro Farmacia, vista Oportunidad. Verde oscuro = mucha demanda y poca competencia. Puntos rojos = farmacias existentes.
3. **Las mejores zonas** (45 s). Tocar la primera del ranking. Mostrar la ficha: pirámide de edad, educación, servicios, ▲▼ frente al promedio, competencia a 800 m y habitantes por farmacia.
4. **Bajar a la calle** (45 s). Buscar "Ayacucho". La avenida completa queda en azul y el mejor tramo en oscuro. "Ver toda la calle". Cambiar el ranking a **Calles**.
5. **Otro negocio** (30 s). Cambiar a Ferretería o Taller mecánico: el mapa se recalcula y la oportunidad se mueve a otras zonas.
6. **Ajustar el criterio** (30 s). Subir el peso de la competencia. "Si usted conoce su negocio, ajusta los pesos y el mapa le responde."
7. **El censo completo** (30 s). Vista Indicador → % de 60 años o más; luego % con agua por cañería. "Lo mismo sirve para una alcaldía: dónde faltan servicios."
8. **Preguntarle al mapa** (60 s, solo dentro de Claude). Abrir el chat y preguntar en voz alta, por ejemplo:
   - "¿Cuáles son los barrios con más mayores de 60 años?"
   - "¿Dónde abro un gimnasio en Sacaba? Muéstramelo en el mapa."
   - "Compara Recoleta con el promedio del municipio."
   - "¿Qué zonas tienen menos acceso a agua por cañería?"
   Claude consulta los datos del mapa, responde con cifras y mueve el mapa al lugar. Cada pregunta usa la cuenta de Claude de quien la hace; la primera vez pide permiso.

## Qué decir sobre los límites

- El censo mide dónde vive la gente, no dónde trabaja ni por dónde pasa.
- No mide ingresos; el poder adquisitivo se aproxima con educación, internet, piso y seguro de salud.
- OpenStreetMap no tiene todos los negocios ni todos los barrios. Para un cliente se carga su lista de sucursales y competidores.

## Activar la versión pública en GitHub Pages

El repositorio ya tiene la página en la carpeta `docs/`. Falta hacer dos cambios en GitHub (solo los puede hacer el dueño):

1. **Hacer público el repositorio.** Settings → General → Danger Zone → Change repository visibility → Public. El código y los datos quedan visibles para todos; son datos públicos del INE y de OpenStreetMap, con sus créditos.
2. **Activar Pages.** Settings → Pages → Build and deployment → Source: "Deploy from a branch" → Branch: `main`, carpeta `/docs` → Save.

En uno o dos minutos la página queda en https://marcelomedinanp.github.io/censo2024-mapas/. Cada vez que se actualiza la carpeta `docs/`, la página se actualiza sola.

Si prefieres mantener el repositorio privado: GitHub Pages en repositorios privados requiere GitHub Pro, o se puede conectar el repositorio a Netlify o Cloudflare Pages, que publican desde repositorios privados en su plan gratuito.
