# Dashboard Informe Trimestral SESEA #

Dashboard interactivo para la consulta y visualización de indicadores de las Secretarías Estatales Anticorrupción (SEA).

La finalidad del proyecto permite consultar información nacional y por entidad federativa mediante un dashboard interactivo.

# Información que se presenta #

Actualmente el dashboard incluye información sobre:

- Grado de consolidación
- Numero de designaciones vigentes
- Entes interconectados a la Plataforma Digital Nacional (PDN)
- Avances a la implementación de la Política Pública a nivel estatal
- Profesionalización

La informacion se presenta a nivel nacional y se desagrega a nivel estatal.

También incluye un botón de descarga (ícono de base de datos en la
barra superior) que entrega un ZIP con los informes del trimestre y
un CSV con la base de datos completa.

# Insumos utilizados #

- Next.js (App Router) / React / TypeScript
- Plotly.js (mapa y gráficas)
- Supabase (base de datos y storage)
- Git / GitHub
- Python (solo para los scripts de carga de datos, ver abajo)

# Estructura del proyecto #

```
app/                    Páginas y rutas (Next.js App Router)
  page.tsx                Carga los datos de Supabase y arma el tablero
  layout.tsx               Metadatos y estilos globales
  globals.css               Estilos del tablero
  api/descargar/route.ts     Genera el ZIP de descarga
components/             Componentes de React del tablero
lib/                    Lógica compartida (cálculo de indicadores,
                        cliente de Supabase, iconos, formato, CSV)
content/                fichasEspeciales.json (situaciones institucionales
                        especiales, ej. CDMX y Oaxaca)
public/                 GeoJSON de los estados y los iconos (SVG)
types/                  Declaraciones de TypeScript para react-plotly.js

procesar_datos.py       Procesa el Excel fuente (script de mantenimiento)
cargar_supabase.py      Sube el Excel procesado a la tabla dashboard_sesea
probar_supabase.py      Prueba de conexión de solo lectura a Supabase
```

Los tres scripts de Python (`procesar_datos.py`, `cargar_supabase.py`,
`probar_supabase.py`) son herramientas independientes de carga y
mantenimiento de datos; no forman parte del tablero web.

# Cómo ejecutar el tablero #

1. Instalar dependencias:

   ```
   npm install
   ```

2. Crear el archivo `.env.local` (o `.env`) con las credenciales:

   ```
   SUPABASE_URL=...
   SUPABASE_SECRET_KEY=...
   ```

3. Ejecutar en modo desarrollo:

   ```
   npm run dev
   ```

   El tablero queda disponible en http://localhost:3000

4. Para producción:

   ```
   npm run build
   npm run start
   ```

# Cómo actualizar los datos #

1. Colocar el Excel fuente en `data/BDD_Dashboard.xlsx` (carpeta
   ignorada por git).
2. `python procesar_datos.py` para limpiar y preparar la base.
3. `python cargar_supabase.py` para subir los datos a la tabla
   `dashboard_sesea` en Supabase (requiere `SUPABASE_URL` y
   `SUPABASE_SECRET_KEY` en `.env`).

# Diseño #

El tablero está diseñado para verse completo en una sola
pantalla, sin necesidad de desplazarse. El mapa, la gráfica y
las tarjetas se ajustan a la altura de la ventana; en pantallas
de menor altura se omiten los textos descriptivos y los
elementos se compactan de forma automática.

# Navegación #

- El periodo se elige con los selectores de Año y Trimestre.
- La entidad se puede cambiar desde el selector o dando clic
  sobre el mapa; el botón "Regresar a la vista nacional"
  devuelve la vista agregada.
- La entidad seleccionada queda registrada en la dirección
  (por ejemplo ?entidad=Jalisco), por lo que la vista puede
  compartirse mediante el enlace.
