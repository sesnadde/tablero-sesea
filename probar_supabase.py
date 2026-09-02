import os

from dotenv import load_dotenv
from supabase import create_client


# --------------------------------------------------
# 1. CARGAR VARIABLES DEL ARCHIVO .env
# --------------------------------------------------

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")


# --------------------------------------------------
# 2. COMPROBAR QUE LAS VARIABLES EXISTEN
# --------------------------------------------------

if not supabase_url or not supabase_key:
    raise ValueError(
        "No se encontraron SUPABASE_URL o SUPABASE_KEY en el archivo .env"
    )


# --------------------------------------------------
# 3. CREAR CONEXION CON SUPABASE
# --------------------------------------------------

supabase = create_client(
    supabase_url,
    supabase_key
)


# --------------------------------------------------
# 4. CONSULTAR NUESTRA TABLA
# --------------------------------------------------

respuesta = (
    supabase
    .table("dashboard_sesea")
    .select("*")
    .execute()
)


# --------------------------------------------------
# 5. MOSTRAR RESULTADO
# --------------------------------------------------

print("Conexion con Supabase realizada correctamente.")
print(f"Registros encontrados: {len(respuesta.data)}")
print(respuesta.data)