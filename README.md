# Dashboard Informa Trimestral SESEA #

Dashboard interactivo para la consulta y visualización de indicadores de las Secretarías Estatales Anticorrupción (SEA).

La finalidad del proyecto permite consultar información nacional y por entidad federativa mediante un dashboard interactivo.

# Información que se presenta #

Actualmente el dashboard incluye información sobre:

- Grado de consolidación
- Numero de designaciones vigentes
- Entes interconectados a la Plataforma Digital Nacional (PDN)
- Avances a la implementación de la Política Pública a nivel estatal
- Profesionalización

La informacion se presenta a nivel nacional y se desagrega a nivel estatal

# Insumos utilizados #

- Python
- Streamlit
- Pandas
- Plotly
- Supabase
- Git / GitHub
- Microsoft Office (Excel) como fuente para la actualización periódica de información.

# Estructura del proyecto #

procesar_datos.py (Procesamiento de datos)
cargar_supabase-py (Despliega y actualiza la base en Supabase)
app.py (Ejecuta el dashboard)
requirements.txt
.gitignore
assets/ json estatal/nacional
assets/icons/ iconos institucionales del tablero

# Cómo ejecutar el dashboard #

1. Instalar dependencias:

   pip install -r requirements.txt

2. Crear el archivo .env con las credenciales:

   SUPABASE_URL=...
   SUPABASE_SECRET_KEY=...

3. Ejecutar:

   python -m streamlit run app.py

El tablero queda disponible en http://localhost:8501

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