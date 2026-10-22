import pandas as pd

# RUTA DEL ARCHIVO #

archivo_entrada = "data/BDD_Dashboard.xlsx"

# LECTURA DE LA BASE DE DATOS #

df = pd.read_excel(archivo_entrada)

# REVISION INICIAL #

print("Base cargada correctamente.")
print(f"Filas: {df.shape[0]}")
print(f"Columnas: {df.shape[1]}")

print("\nColumnas encontradas:")

for columna in df.columns:
    print(columna)

# RENOMBRADO DE COLUMNAS #

renombrar_columnas = {
    "NOM_ENT": "NOM_ENT",
    "ID_ENT": "ID_ENT",

    "DES_PEND_TIT": "DES_PEND_TIT",
    "DES_PEND_CS": "DES_PEND_CS",
    "DES_PEND_CPC": "DES_PEND_CPC",
    "DES_PEND_CC": "DES_PEND_CC",
    "DES_PEND_CRSF": "DES_PEND_CRSF",

    "DES_VIG_TIT": "DES_VIG_TIT",
    "DES_VIG_CS": "DES_VIG_CS",
    "DES_VIG_CPC": "DES_VIG_CPC",
    "DES_VIG_CC": "DES_VIG_CC",
    "DES_VIG_CRSF": "DES_VIG_CRSF",

    "ANIO": "ANIO",
    "TRIMESTRE": "TRIMESTRE",

    "GRADO_CONS_TOTAL": "GRADO_CONS_TOTAL",
    "GRADO_CONS_IMPLEM_NUM": "GRADO_CONS_IMPLEM_NUM",
    "GRADO_CONS_INIDC_NUM": "GRADO_CONS_INDIC_NUM",
    "GRADO_CONS_SYE_NUM": "GRADO_CONS_SYE_NUM",

    "S1 Declaraciones patrimoniales TOTAL": "S1_TOTAL",
    "S2 Servidores en Contrataciones TOTAL": "S2_TOTAL",
    "S3 Servidores sancionados (OIC + TJA) TOTAL": "S3_TOTAL",
    "S6 Contrataciones Públicas TOTAL": "S6_TOTAL",

    "S1 Declaraciones patrimoniales ENTES": "S1_ENTES",
    "S2 Servidores en Contrataciones ENTES": "S2_ENTES",
    "S3 Servidores sancionados (OIC + TJA) ENTES": "S3_ENTES",
    "S6 Contrataciones Públicas ENTES": "S6_ENTES",

    "% CUMLPLIMIENTO S1": "CUMPLIMIENTO_S1",
    "% CUMLPLIMIENTO S2": "CUMPLIMIENTO_S2",
    "% CUMLPLIMIENTO S3": "CUMPLIMIENTO_S3",
    "% CUMLPLIMIENTO S6": "CUMPLIMIENTO_S6",

    "CAP_SERV_PUB": "CAP_SERV_PUB",
    "PAA_JUDICATURA": "PAA_JUDICATURA",
    "PAA_CONTRALORIA": "PAA_CONTRALORIA",
    "PAA_CPC": "PAA_CPC",
    "PAA_FECC": "PAA_FECC",
    "PAA_OSF": "PAA_OSF",
    "PAA_SESEA": "PAA_SESEA",
    "PAA_SESNA": "PAA_SESNA",
    "PAA_TDF": "PAA_TDF",
    "PAA_TJA": "PAA_TJA",
    "PJ": "PJ",
    "SH": "SH",
    "TDJ": "TDJ",

    "FECHA_APROBACION_PEA": "FECHA_APROBACION_PEA",
    "FECHA_APROBACION_PIPEA": "FECHA_APROBACION_PIPEA",
    "FECHA_EJECUCIÓN_PIPEA": "FECHA_EJECUCION_PIPEA",
    "FECHA_APROBACION_SYE": "FECHA_APROBACION_SYE",
    "FECHA_EVALUACION": "FECHA_EVALUACION",

    "LINK_PEA": "LINK_PEA",
    "LINK_PIPEA": "LINK_PIPEA",
    "LINK_SISE": "LINK_SISE",

    "TEXT_APROB_PEA": "TEXT_APROB_PEA",
    "TEXT_APROB_PIPEA": "TEXT_APROB_PIPEA",
    "TEXT_EJEC_PIPEA": "TEXT_EJEC_PIPEA",
    "TEXT_METODOLOGIA_SISE": "TEXT_METODOLOGIA_SISE",
    "TEXT_EVALUA_POLITICA": "TEXT_EVALUA_POLITICA"

}

df = df.rename(columns=renombrar_columnas)

# VARIABLES DE LINKS Y TEXTOS DE IMPLEMENTACIÓN #

columnas_links_textos = [
    "LINK_PEA",
    "LINK_PIPEA",
    "LINK_SISE",
    "TEXT_APROB_PEA",
    "TEXT_APROB_PIPEA",
    "TEXT_EJEC_PIPEA",
    "TEXT_METODOLOGIA_SISE",
    "TEXT_EVALUA_POLITICA"
]

for columna in columnas_links_textos:
    if columna in df.columns:
        df[columna] = df[columna].astype("string")

# VARIABLES DE PROFESIONALIZACIÓN #

columnas_profesionalizacion = [
    "CAP_SERV_PUB",
    "PAA_JUDICATURA",
    "PAA_CONTRALORIA",
    "PAA_CPC",
    "PAA_FECC",
    "PAA_OSF",
    "PAA_SESEA",
    "PAA_SESNA",
    "PAA_TDF",
    "PAA_TJA",
    "PJ",
    "SH",
    "TDJ"
]

for columna in columnas_profesionalizacion:
    df[columna] = pd.to_numeric(
        df[columna],
        errors="coerce"
    ). fillna(0).astype(int)


# DISPONIBILIDAD DE INFORMACION #

entidades_sin_informacion = [
    "Ciudad de México",
    "Oaxaca"
]

# CREAR UNA SOLA COLUMNA #

df["TIENE_INFORMACION"] = 1

df.loc[
    df["NOM_ENT"].isin(entidades_sin_informacion),
    "TIENE_INFORMACION"
] = 0

# VARIABLES SIN INFORMACION PARA CDMX Y OAXACA #

columnas_sin_dato = [
    "GRADO_CONS_TOTAL",
    "GRADO_CONS_IMPLEM_NUM",
    "GRADO_CONS_INDIC_NUM",
    "GRADO_CONS_SYE_NUM",

    "S1_TOTAL",
    "S2_TOTAL",
    "S3_TOTAL",
    "S6_TOTAL",

    "S1_ENTES",
    "S2_ENTES",
    "S3_ENTES",
    "S6_ENTES",

    "CUMPLIMIENTO_S1",
    "CUMPLIMIENTO_S2",
    "CUMPLIMIENTO_S3",
    "CUMPLIMIENTO_S6",

    "LINK_PEA",
    "LINK_PIPEA",
    "LINK_SISE",
    "TEXT_APROB_PEA",
    "TEXT_APROB_PIPEA",
    "TEXT_EJEC_PIPEA",
    "TEXT_METODOLOGIA_SISE",
    "TEXT_EVALUA_POLITICA"
]

df.loc[
    df["NOM_ENT"].isin(entidades_sin_informacion),
    columnas_sin_dato
] = pd.NA



# REVISION DESPUÉS DEL RENOMBRADO #

print("Base cargada y columnas etiquetadas correctamente.")
print(f"Filas: {df.shape[0]}")
print(f"Columnas: {df.shape[1]}")

print("\nColumnas encontradas:")

for columna in df.columns:
    print(columna)


# EXPORTACION DE LA BASE LIMPIA #

archivo_salida = "data/BDD_Dashboard_Limpia.xlsx"

df.to_excel(
    archivo_salida,
     index=False
     )

print("\nArchivo exportado correctamente:")
print(archivo_salida)


# CREACION DE DICCIONARIO DE DATOS #

diccionario = pd.DataFrame([
    ["NOM_ENT", "Nombre de la entidad federativa", "Identificacion", "text", "No", ""],
    ["ID_ENT", "Identificador numerico de la entidad", "Identificacion", "integer", "No", "Valores de 1 a 32"],

    ["DES_PEND_TIT", "Designacion pendiente de Titular SESEA", "Designaciones", "integer", "No", ""],
    ["DES_PEND_CS", "Designaciones pendientes del Comite de Seleccion", "Designaciones", "integer", "No", ""],
    ["DES_PEND_CPC", "Designaciones pendientes del CPC", "Designaciones", "integer", "No", ""],
    ["DES_PEND_CC", "Designaciones pendientes del Comite Coordinador", "Designaciones", "integer", "No", ""],
    ["DES_PEND_CRSF", "Designaciones pendientes del Comite Rector del Sistema de Fiscalizacion", "Designaciones", "integer", "No", ""],

    ["DES_VIG_TIT", "Titular SESEA vigente", "Designaciones", "integer", "No", "1 = Si; 0 = No"],
    ["DES_VIG_CS", "Designaciones vigentes del Comite de Seleccion", "Designaciones", "integer", "No", ""],
    ["DES_VIG_CPC", "Designaciones vigentes del CPC", "Designaciones", "integer", "No", ""],
    ["DES_VIG_CC", "Designaciones vigentes del Comite Coordinador", "Designaciones", "integer", "No", ""],
    ["DES_VIG_CRSF", "Designaciones vigentes del Comite Rector del Sistema de Fiscalizacion", "Designaciones", "integer", "No", ""],

    ["ANIO", "Anio de referencia de la informacion", "Identificacion", "integer", "No", ""],
    ["TRIMESTRE", "Trimestre de referencia", "Identificacion", "integer", "No", "Valores de 1 a 4"],

    ["GRADO_CONS_TOTAL", "Grado total de consolidacion", "Consolidacion", "numeric", "Si", "Escala de 0 a 100"],
    ["GRADO_CONS_IMPLEM_NUM", "Componente de implementacion del grado de consolidacion", "Consolidacion", "numeric", "Si", ""],
    ["GRADO_CONS_INDIC_NUM", "Componente de indicadores del grado de consolidacion", "Consolidacion", "numeric", "Si", ""],
    ["GRADO_CONS_SYE_NUM", "Componente de seguimiento y evaluacion del grado de consolidacion", "Consolidacion", "numeric", "Si", ""],

    ["S1_TOTAL", "Total de entes considerados para el Sistema 1", "PDN", "integer", "Si", ""],
    ["S2_TOTAL", "Total de entes considerados para el Sistema 2", "PDN", "integer", "Si", ""],
    ["S3_TOTAL", "Total de entes considerados para el Sistema 3", "PDN", "integer", "Si", ""],
    ["S6_TOTAL", "Total de entes considerados para el Sistema 6", "PDN", "integer", "Si", ""],

    ["S1_ENTES", "Entes interconectados al Sistema 1", "PDN", "integer", "Si", ""],
    ["S2_ENTES", "Entes interconectados al Sistema 2", "PDN", "integer", "Si", ""],
    ["S3_ENTES", "Entes interconectados al Sistema 3", "PDN", "integer", "Si", ""],
    ["S6_ENTES", "Entes interconectados al Sistema 6", "PDN", "integer", "Si", ""],

    ["CUMPLIMIENTO_S1", "Cumplimiento del Sistema 1", "PDN", "numeric", "Si",
     "Proporcion entre 0 y 1; se visualiza como porcentaje; no se recalcula"],

    ["CUMPLIMIENTO_S2", "Cumplimiento del Sistema 2", "PDN", "numeric", "Si",
     "Proporcion entre 0 y 1; se visualiza como porcentaje; no se recalcula"],

    ["CUMPLIMIENTO_S3", "Cumplimiento del Sistema 3", "PDN", "numeric", "Si",
     "Proporcion entre 0 y 1; se visualiza como porcentaje; no se recalcula"],

    ["CUMPLIMIENTO_S6", "Cumplimiento del Sistema 6", "PDN", "numeric", "Si",
     "Proporcion entre 0 y 1; se visualiza como porcentaje; no se recalcula"],

    ["CAP_SERV_PUB", " Total de personas capacitadas por la SESEA", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_JUDICATURA", "Personas capacitadas por el Consejo de la Judicatura en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_CONTRALORIA", "Personas capacitadas por Secretaría Anticorrupción y Buen Gobierno Estatal / Secretaría de la Función Pública en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_CPC", "Personas capacitadas por el Comité de Participación Ciudadana en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_FECC", "Personas capacitadas por la Fiscalía Especializada Contra la Corrupción de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_OSF", "Personas capacitadas por la Auditoría Superior en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_SESEA", "Personas capacitadas por la Secretaría Estatal Anticorrupción en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_SESNA", "Personas capacitadas por la Secretaria Ejecutiva del Sistema Nacional Anticorrupción en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_TDF", "Personas capacitadas por la Coordinación de Vigilancia en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PAA_TJA", "Personas capacitadas por el Tribunal de Justica Administrativa en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["PJ", "Personas capacitadas por el Poder Judicial en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["SH", "Personas capacitadas por la Secretaría de Hacienda en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],
    ["TDJ", "Personas capacitadas por el Tribunal de Disciplina Judicial en la Plataforma de Aprendizaje Anticorrupción", "Profesionalización", "integer", "No", "Conteo de personas"],


    ["FECHA_APROBACION_PEA", "Fecha de aprobacion de la PEA", "Implementacion", "date", "Si", ""],
    ["FECHA_APROBACION_PIPEA", "Fecha de aprobacion del PI-PEA", "Implementacion", "date", "Si", ""],
    ["FECHA_EJECUCION_PIPEA", "Fecha de ejecucion del PI-PEA", "Implementacion", "date", "Si", ""],
    ["FECHA_APROBACION_SYE", "Fecha de aprobacion del mecanismo de seguimiento y evaluacion", "Implementacion", "date", "Si", ""],
    ["FECHA_EVALUACION", "Fecha de evaluacion correspondiente", "Implementacion", "date", "Si", ""],
    ["TIENE_INFORMACION", "Indica si la entidad cuenta con informacion disponible para el dashboard", "Control", "integer", "No", "1 = informacion disponible; 0 = sin informacion disponible"],

    ["LINK_PEA", "Liga al documento formal de aprobación de la PEA", "Implementacion", "text", "Si", "URL del documento; no aplica para entidades sin informacion"],
    ["LINK_PIPEA", "Liga al documento formal de aprobación del PI-PEA", "Implementacion", "text", "Si", "URL del documento; no aplica para entidades sin informacion"],
    ["LINK_SISE", "Liga al documento formal de la metodología de seguimiento y evaluacion", "Implementacion", "text", "Si", "URL del documento; no aplica para entidades sin informacion"],
    ["TEXT_APROB_PEA", "Texto descriptivo de la etapa de aprobación de la PEA", "Implementacion", "text", "Si", "Contenido desplegable del visual de Avances de la Implementación"],
    ["TEXT_APROB_PIPEA", "Texto descriptivo de la etapa de aprobación del PI-PEA", "text", "Si", "Contenido desplegable del visual de Avances de la Implementación"],
    ["TEXT_EJEC_PIPEA", "Texto descriptivo de la etapa de ejecución deL PI-PEA", "text", "Si", "Contenido desplegable del visual de Avances de la Implementación"],
    ["TEXT_METODOLOGIA_SISE", "Texto descriptivo de la metodología de seguimiento y evaluacion", "Implementacion", "text", "Si", "Contenido desplegable del visual de Avances de la Implementación"],
    ["TEXT_EVALUA_POLITICA", "Texto descriptivo de la etapa de aprobación de la PEA", "Implementacion", "text", "Si", "Contenido desplegable del visual de Avances de la Implementación"]
],

columns=[
    "VARIABLE",
    "DESCRIPCION",
    "BLOQUE",
    "TIPO_DATO",
    "ADMITE_NULL",
    "OBSERVACIONES"
])

# EXPORTACION DEL DICCIONARIO DE DATOS #

archivo_diccionario = "data/Diccionario_BDD_Dashboard.xlsx"

diccionario.to_excel(
    archivo_diccionario,
     index=False,
     sheet_name="DICCIONARIO"
     )

print("\nArchivo de datos exportado correctamente:")
print(archivo_diccionario)