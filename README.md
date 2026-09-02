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