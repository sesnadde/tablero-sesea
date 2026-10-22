import os
import pandas as pd

from dotenv import load_dotenv
from supabase import create_client


# --------------------------------------------------
# 1. CARGAR CREDENCIALES
# --------------------------------------------------

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_secret_key = os.getenv("SUPABASE_SECRET_KEY")

if not supabase_url or not supabase_secret_key:
    raise ValueError(
        "No se encontraron SUPABASE_URL o SUPABASE_SECRET_KEY en .env"
    )


# --------------------------------------------------
# 2. CREAR CLIENTE ADMINISTRATIVO
# --------------------------------------------------

supabase = create_client(
    supabase_url,
    supabase_secret_key
)


# --------------------------------------------------
# 3. LEER BASE LIMPIA
# --------------------------------------------------

archivo = "data/BDD_Dashboard_Limpia.xlsx"

df = pd.read_excel(archivo)

print(f"Filas encontradas: {df.shape[0]}")
print(f"Columnas encontradas: {df.shape[1]}")


# --------------------------------------------------
# 4. CONVERTIR COLUMNAS A ENTERAS 
# --------------------------------------------------

df.columns = df.columns.str.lower()

print("\nCOLUMNAS REALES DE LA BASE:")
for columna in df.columns:
    print(repr(columna))

columnas_enteras = [
    "id_ent",

    "des_pend_tit",
    "des_pend_cs",
    "des_pend_cpc",
    "des_pend_cc",
    "des_pend_crsf",

    "des_vig_tit",
    "des_vig_cs",
    "des_vig_cpc",
    "des_vig_cc",
    "des_vig_crsf",

    "anio",
    "trimestre",

    "tiene_informacion",

# PROFESIONALIZACION #

    "cap_serv_pub",
    "paa_judicatura",
    "paa_contraloria",
    "paa_cpc",
    "paa_fecc",
    "paa_osf",
    "paa_sesea",
    "paa_sesna",
    "paa_tdf",
    "paa_tja",
    "pj",
    "sh",
    "tdj"

]

print("\nCOLUMNAS QUE NO SE ENCUENTRAN:")

for columna in columnas_enteras:
    if columna not in df.columns:
        print(f"FALTA: {columna}")

for columna in columnas_enteras:
    df[columna] = pd.to_numeric(
        df[columna],
        errors="coerce"
    ).astype(int)

# ENTEROS QUE PUEDEN CONTENER NULL #

columnas_enteras_nullable = [

    "s1_total",
    "s2_total",
    "s3_total",
    "s6_total",

    "s1_entes",
    "s2_entes",
    "s3_entes",
    "s6_entes"
]

for columna in columnas_enteras_nullable:
    df[columna] = pd.to_numeric(
        df[columna],
        errors="coerce"
    ).astype("Int64")
       
# --------------------------------------------------
# 5. PREPARAR FECHAS
# --------------------------------------------------

columnas_fecha = [
    "fecha_aprobacion_pea",
    "fecha_aprobacion_pipea",
    "fecha_ejecucion_pipea",
    "fecha_aprobacion_sye",
    "fecha_evaluacion"
]

for columna in columnas_fecha:

    df[columna] = pd.to_datetime(
        df[columna],
        errors="coerce"
    )

    df[columna] = df[columna].apply(
        lambda x: x.strftime("%Y-%m-%d")
        if pd.notna(x)
        else None
    )

# --------------------------------------------------
# 6. PREPARAR LINKS Y TEXTOS
# --------------------------------------------------

columnas_texto = [
    "link_pea",
    "link_pipea",
    "link_sise",
    "text_aprob_pea",
    "text_aprob_pipea",
    "text_ejec_pipea",
    "text_metodologia_sise",
    "text_evalua_politica"
]

for columna in columnas_texto:
    if columna in df.columns:
        df[columna] = df[columna].astype("string")

# --------------------------------------------------
# 7. CONVERTIR VALORES VACIOS A NULL 
# --------------------------------------------------

df = df.astype(object).where(
    pd.notna(df),
    None
)

# --------------------------------------------------
# 8. CONVERTIR VALORES VACIOS A NULL 
# --------------------------------------------------

registros = df.to_dict(orient="records")


# --------------------------------------------------
# 9. INSERTAR EN SUPABASE
# --------------------------------------------------

respuesta = (
    supabase
    .table("dashboard_sesea")
    .upsert(
        registros,
        on_conflict="id_ent,anio,trimestre"
    )
    .execute()
)


# --------------------------------------------------
# 10. RESULTADO
# --------------------------------------------------

print("\nSincronización realizada correctamente.")
print(f"Registros enviados: {len(registros)}")
print(
    f"Registros actualizados/insertados: " 
    f"{len(respuesta.data)}"
    )