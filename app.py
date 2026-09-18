import os
import re
import json
import base64
import html


import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from dotenv import load_dotenv
from supabase import create_client


# --------------------------------------------------
# 1. CONFIGURACION GENERAL
# --------------------------------------------------

st.set_page_config(
    page_title="Informe Trimestral SESEA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# 2. IDENTIDAD INSTITUCIONAL
# --------------------------------------------------

# Paleta institucional
VINO = "#9b2247"
VINO_OSCURO = "#611232"
ORO = "#a57f2c"
ORO_CLARO = "#e6d194"
GRIS = "#98989A"
TINTA = "#161a1d"

# Paleta complementaria para tarjetas
COLORES_TARJETAS = [
    "#4F7187",
    "#397D86",
    "#6F8F82",
    "#7D8790",
    "#82758F"
]

# Escala del mapa (claro = bajo, oscuro = alto)
ESCALA_MAPA = [
    [0.00, "#f7f0e2"],
    [0.35, ORO_CLARO],
    [0.70, VINO],
    [1.00, VINO_OSCURO]
]

GRADIENTE_LEYENDA = (
    f"linear-gradient(90deg, #f7f0e2 0%, {ORO_CLARO} 35%, "
    f"{VINO} 70%, {VINO_OSCURO} 100%)"
)


def aclarar(color, proporcion):
    """Mezcla un color con blanco y devuelve el hexadecimal."""

    color = color.lstrip("#")

    canales = [
        int(color[posicion:posicion + 2], 16)
        for posicion in (0, 2, 4)
    ]

    canales = [
        round(canal * proporcion + 255 * (1 - proporcion))
        for canal in canales
    ]

    return "#{:02x}{:02x}{:02x}".format(*canales)

# Etiqueta de la vista agregada
NACIONAL = "Nacional"


# --------------------------------------------------
# 3. ICONOS
# --------------------------------------------------

CARPETA_ICONOS = "assets/icons"

ARCHIVOS_ICONOS = {
    "persona": "person_100dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.svg",
    "grupo": "groups_100dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.svg",
    "check": "check_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
    "lista": "list_alt_check_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
    "grading": "grading_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
    "play": "play_arrow_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
    "grafica": "graph_2_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
    "red": "network_node_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
    "finanzas": "finance_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
    "link": "link_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
}


@st.cache_data(show_spinner=False)
def icono(nombre, color="#ffffff", tamano=24):
    """Devuelve el icono como imagen lista para insertarse en HTML.

    Se entrega como data URI porque Streamlit no conserva el
    SVG en línea dentro del HTML de los componentes.
    """

    ruta = os.path.join(
        CARPETA_ICONOS,
        ARCHIVOS_ICONOS[nombre]
    )

    if not os.path.exists(ruta):
        return ""

    with open(ruta, "r", encoding="utf-8") as archivo:
        svg = archivo.read()

    # El color se define al momento de usar el icono
    svg = re.sub(
        r'fill="#[0-9A-Fa-f]{3,8}"',
        f'fill="{color}"',
        svg
    )

    codificado = base64.b64encode(
        svg.encode("utf-8")
    ).decode("ascii")

    return (
        f'<img src="data:image/svg+xml;base64,{codificado}" '
        f'width="{tamano}" height="{tamano}" alt="">'
    )


# --------------------------------------------------
# 4. CARGA DE ESTILOS
# --------------------------------------------------

def cargar_css(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        css = archivo.read()

    st.html(
        f"""
        <style>
        {css}
        </style>
        """
    )


cargar_css("css/styles.css")


# --------------------------------------------------
# 5. CREDENCIALES Y DATOS
# --------------------------------------------------

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SECRET_KEY")

if not supabase_url or not supabase_key:
    st.error("No se encontraron las credenciales de Supabase.")
    st.stop()


supabase = create_client(
    supabase_url,
    supabase_key
)


@st.cache_data(show_spinner="Cargando información...")
def cargar_datos():

    respuesta = (
        supabase
        .table("dashboard_sesea")
        .select("*")
        .execute()
    )

    return pd.DataFrame(respuesta.data)


@st.cache_data(show_spinner=False)
def cargar_geojson():

    with open(
        "assets/estados_mexico.json",
        "r",
        encoding="utf-8"
    ) as archivo:
        return json.load(archivo)

@st.cache_data(show_spinner=False)
def cargar_fichas_especiales():

    with open(
        "assets/fichas_especiales.json",
        "r",
        encoding="utf-8"
    ) as archivo:
        return json.load(archivo)

datos = cargar_datos()
geojson_mexico = cargar_geojson()
fichas_especiales = cargar_fichas_especiales()

# --------------------------------------------------
# 6. UTILIDADES DE FORMATO
# --------------------------------------------------

def formato(valor, decimales=0, sufijo=""):
    """Formatea un número o devuelve s/d cuando no hay dato."""

    if valor is None or pd.isna(valor):
        return "s/d"

    return f"{valor:,.{decimales}f}{sufijo}"


def texto_trimestre(numero):

    return f"{int(numero)}° Trimestre"


# --------------------------------------------------
# 7. BARRA SUPERIOR CON FILTROS
# --------------------------------------------------

with st.container(key="barra_superior"):

    col_titulo, col_anio, col_trimestre, col_entidad = st.columns(
        [3.4, 1, 1.2, 1.6],
        vertical_alignment="center"
    )

    with col_titulo:

        st.html(
            """
            <div class="titulo-barra">Informe Trimestral SESEA</div>
            <div class="subtitulo-barra">
                Secretarías Ejecutivas de los Sistemas Estatales Anticorrupción
            </div>
            """
        )

    with col_anio:

        anio = st.selectbox(
            "Año",
            sorted(datos["anio"].unique(), reverse=True)
        )

    with col_trimestre:

        trimestres_disponibles = sorted(
            datos.loc[datos["anio"] == anio, "trimestre"].unique()
        )

        trimestre = st.selectbox(
            "Trimestre",
            trimestres_disponibles,
            format_func=texto_trimestre
        )

    # Datos del periodo seleccionado
    datos_periodo = datos[
        (datos["anio"] == anio)
        & (datos["trimestre"] == trimestre)
    ].copy()

    entidades = [NACIONAL] + sorted(
        datos_periodo["nom_ent"].tolist()
    )

    # Entidad activa (se sincroniza con el clic en el mapa
    # y con la entidad indicada en la URL)
    if "entidad_activa" not in st.session_state:

        entidad_url = st.query_params.get("entidad")

        st.session_state["entidad_activa"] = (
            entidad_url
            if entidad_url in entidades
            else NACIONAL
        )

    if st.session_state["entidad_activa"] not in entidades:
        st.session_state["entidad_activa"] = NACIONAL

    if (
        "selector_entidad" not in st.session_state
        or st.session_state["selector_entidad"]
        != st.session_state["entidad_activa"]
    ):
        st.session_state["selector_entidad"] = (
            st.session_state["entidad_activa"]
        )

    def actualizar_desde_selector():

        st.session_state["entidad_activa"] = (
            st.session_state["selector_entidad"]
        )

    with col_entidad:

        st.selectbox(
            "Entidad",
            entidades,
            key="selector_entidad",
            on_change=actualizar_desde_selector
        )


entidad_seleccionada = st.session_state["entidad_activa"]
es_nacional = entidad_seleccionada == NACIONAL
es_ficha_especial = entidad_seleccionada in fichas_especiales


# La entidad se refleja en la URL para poder compartir la vista
if es_nacional:
    if "entidad" in st.query_params:
        del st.query_params["entidad"]
elif st.query_params.get("entidad") != entidad_seleccionada:
    st.query_params["entidad"] = entidad_seleccionada


# --------------------------------------------------
# 7.1 FICHAS INSTITUCIONALES ESPECIALES
# --------------------------------------------------

if es_ficha_especial:

    ficha = fichas_especiales[entidad_seleccionada]

    # Botón para regresar a la vista nacional
    if st.button(
        "← Regresar a la vista nacional",
        key="boton_nacional_ficha"
    ):
        st.session_state["entidad_activa"] = NACIONAL
        st.rerun()

       # ---------- Preparación de hechos relevantes ----------

    hechos_html = ""

    for hecho in ficha["hechos_relevantes"]:

        hechos_html += f"""
            <div class="ficha-hecho">
                <span class="ficha-vineta">•</span>
                <span>{hecho}</span>
            </div>
        """


    # ---------- Preparación de línea de tiempo ----------

    eventos_timeline_html = ""

    for evento in ficha["linea_tiempo"]:

        puntos_html = "".join(
            f"<li>{punto}</li>"
            for punto in evento["eventos"]
        )

        eventos_timeline_html += f"""
            <div class="ficha-evento">

                <div class="ficha-evento-punto"></div>

                <div class="ficha-evento-fecha">
                    {evento["fecha"]}
                </div>

                <ul class="ficha-evento-textos">
                    {puntos_html}
                </ul>

            </div>
        """


    # ---------- Ficha completa ----------

    st.html(
        f"""
        <div class="ficha-especial">

            <div class="ficha-encabezado">

                <div class="ficha-etiqueta">
                    Situación institucional especial
                </div>

                <div class="ficha-entidad">
                    {entidad_seleccionada}
                </div>

                <div class="ficha-situacion">
                    {ficha["situacion_actual"]}
                </div>

                <div class="ficha-nota">
                    Información de carácter institucional no sujeta
                    a actualización trimestral
                </div>

            </div>


            <div class="ficha-contenido">

                <div class="ficha-columna-situacion">

                    <div class="ficha-titulo-seccion">
                        Situación actual
                    </div>

                    <div class="ficha-texto">
                        {ficha["situacion_institucional"]}
                    </div>

                </div>


                <div class="ficha-columna-hechos">

                    <div class="ficha-titulo-seccion">
                        Hechos relevantes
                    </div>

                    <div class="ficha-hechos">
                        {hechos_html}
                    </div>

                </div>

            </div>


            <div class="ficha-linea-bloque">

                <div class="ficha-titulo-seccion">
                    Línea de tiempo
                </div>

                <div class="ficha-timeline">
                    {eventos_timeline_html}
                </div>

            </div>

        </div>
        """
    )

    st.stop()

# --------------------------------------------------
# 8. CONFIGURACION DE INDICADORES
# --------------------------------------------------

DESIGNACIONES = [
    {
        "clave": "tit",
        "titulo": "Titular SESEA",
        "icono": "persona"
    },
    {
        "clave": "cs",
        "titulo": "Comité de Selección",
        "icono": "grupo"
    },
    {
        "clave": "cpc",
        "titulo": "Comité de Participación Ciudadana",
        "icono": "grupo"
    },
    {
        "clave": "cc",
        "titulo": "Comité Coordinador",
        "icono": "grupo"
    },
    {
        "clave": "crsf",
        "titulo": "Comité Rector del Sistema de Fiscalización",
        "icono": "grupo"
    }
]

SISTEMAS_PDN = [
    {
        "clave": "s1",
        "titulo": "S1",
        "descripcion": "Declaraciones patrimoniales y de intereses"
    },
    {
        "clave": "s2",
        "titulo": "S2",
        "descripcion": "Servidores públicos en contrataciones"
    },
    {
        "clave": "s3",
        "titulo": "S3",
        "descripcion": "Servidores públicos y particulares sancionados"
    },
    {
        "clave": "s6",
        "titulo": "S6",
        "descripcion": "Información pública de contrataciones"
    }
]

ETAPAS = [
    {
        "nombre": "Aprobación PEA",
        "columna": "fecha_aprobacion_pea",
        "icono": "lista",
        "columna_link": "link_pea",
        "columna_texto": "text_aprob_pea"
    },
    {
        "nombre": "Aprobación del PI-PEA",
        "columna": "fecha_aprobacion_pipea",
        "icono": "grading",
        "columna_link": "link_pipea",
        "columna_texto": "text_aprob_pipea"
    },
    {
        "nombre": "Ejecución del PI-PEA",
        "columna": "fecha_ejecucion_pipea",
        "icono": "play",
        "columna_link": None,
        "columna_texto": "text_ejec_pipea"
    },
    {
        "nombre": "Metodología de seguimiento y evaluación",
        "columna": "fecha_aprobacion_sye",
        "icono": "grafica",
        "columna_link": "link_sise",
        "columna_texto": "text_metodologia_sise"
    },
    {
        "nombre": "Evaluación de la política",
        "columna": "fecha_evaluacion",
        "icono": "check",
        "columna_link": None,
        "columna_texto": "text_evalua_politica"
    }
]

# Cada componente aporta puntos al grado de consolidación.
# Los tres suman los 100 puntos del índice.
COMPONENTES_GRADO = [
    ("Implementación", "grado_cons_implem_num", 67.5),
    ("Indicadores", "grado_cons_indic_num", 7.5),
    ("Seguimiento y evaluación", "grado_cons_sye_num", 25.0)
]

# Etiqueta corta para la gráfica y nombre completo para el detalle
ETIQUETAS_PAA = {
    "paa_osf": (
        "Auditoría Superior",
        "Auditoría Superior"
    ),
    "paa_sesea": (
        "SESEA",
        "Secretaría Ejecutiva del Sistema Estatal Anticorrupción"
    ),
    "paa_fecc": (
        "Fiscalía Anticorrupción",
        "Fiscalía Especializada Contra la Corrupción"
    ),
    "paa_contraloria": (
        "Función Pública / SABG",
        "Secretaría Anticorrupción y Buen Gobierno / Función Pública"
    ),
    "paa_cpc": (
        "Participación Ciudadana",
        "Comité de Participación Ciudadana"
    ),
    "paa_judicatura": (
        "Judicatura",
        "Consejo de la Judicatura"
    ),
    "paa_tja": (
        "Justicia Administrativa",
        "Tribunal de Justicia Administrativa"
    ),
    "paa_tdf": (
        "Coord. de Vigilancia",
        "Coordinación de Vigilancia"
    ),
    "paa_sesna": (
        "SESNA",
        "Secretaría Ejecutiva del Sistema Nacional Anticorrupción"
    )
}


# --------------------------------------------------
# 9. CALCULO DE INDICADORES
# --------------------------------------------------

def calcular_indicadores(datos_periodo, entidad):
    """Calcula todos los indicadores de la vista seleccionada.

    Se trabaja siempre con un DataFrame base: todas las
    entidades con información (vista nacional) o la fila de
    la entidad seleccionada.
    """

    nacional = entidad == NACIONAL

    if nacional:
        base = datos_periodo[
            datos_periodo["tiene_informacion"] == 1
        ].copy()
    else:
        base = datos_periodo[
            (datos_periodo["nom_ent"] == entidad)
            & (datos_periodo["tiene_informacion"] == 1)
        ].copy()

    indicadores = {
        "nacional": nacional,
        "hay_informacion": not base.empty,
        "entidades": int(len(base))
    }

    # ---------- Grado de consolidación ----------

    indicadores["grado_total"] = (
        None if base.empty else base["grado_cons_total"].mean()
    )

    indicadores["componentes"] = [
        {
            "nombre": nombre,
            "puntos": (
                None
                if base.empty
                else base[columna].mean() * 100
            ),
            "maximo": maximo
        }
        for nombre, columna, maximo in COMPONENTES_GRADO
    ]

    # ---------- Designaciones ----------

    designaciones = []

    for posicion, config in enumerate(DESIGNACIONES):

        # Excepción nacional para Titular SESEA
        if nacional and config["clave"] == "tit":

            base_titular = datos_periodo[
                datos_periodo["nom_ent"] != "Oaxaca"
            ].copy()

            vigentes = int(
                pd.to_numeric(
                    base_titular["des_vig_tit"],
                    errors="coerce"
                )
                .fillna(0)
                .sum()
            )

            total = 31

        elif base.empty:

            vigentes = 0
            total = 0

        else:

            vigentes = int(
                base[f"des_vig_{config['clave']}"].sum()
            )

            pendientes = int(
                base[f"des_pend_{config['clave']}"].sum()
            )

            total = vigentes + pendientes

        designaciones.append(
            {
                **config,
                "color": COLORES_TARJETAS[posicion],
                "vigentes": vigentes,
                "total": total
            }
        )

    indicadores["designaciones"] = designaciones

    indicadores["designaciones_vigentes"] = sum(
        item["vigentes"] for item in designaciones
    )

    indicadores["designaciones_total"] = sum(
        item["total"] for item in designaciones
    )

    # ---------- Entes interconectados a la PDN ----------

    sistemas = []

    for config in SISTEMAS_PDN:

        clave = config["clave"]

        if base.empty:
            entes = 0
            total = 0
            porcentaje = 0.0
        else:
            entes = int(base[f"{clave}_entes"].sum())
            total = int(base[f"{clave}_total"].sum())

            if nacional:
                # A nivel nacional se calcula sobre los totales
                porcentaje = (entes / total * 100) if total else 0.0
            else:
                # A nivel estatal se respeta el dato reportado
                porcentaje = float(
                    base[f"cumplimiento_{clave}"].iloc[0]
                ) * 100

        sistemas.append(
            {
                **config,
                "entes": entes,
                "total": total,
                "porcentaje": porcentaje
            }
        )

    indicadores["sistemas"] = sistemas

    indicadores["pdn_entes"] = sum(
        item["entes"] for item in sistemas
    )

    indicadores["pdn_total"] = sum(
        item["total"] for item in sistemas
    )

    indicadores["pdn_porcentaje"] = (
        indicadores["pdn_entes"] / indicadores["pdn_total"] * 100
        if indicadores["pdn_total"]
        else 0.0
    )

    # ---------- Avances de la implementación ----------

    etapas = []

    for config in ETAPAS:

        # Sin información
        if base.empty:

            etapas.append(
                {
                    **config,
                    "valor": "Sin información",
                    "activa": False,
                    "link": None,
                    "texto": None
                }
            )

            continue

        # Fecha correspondiente a la etapa
        fechas = pd.to_datetime(
            base[config["columna"]],
            errors="coerce"
        )

        # ------------------------------------------
        # VISTA NACIONAL
        # ------------------------------------------

        if nacional:

            conteo = int(fechas.notna().sum())

            etapas.append(
                {
                    **config,
                    "valor": f"{conteo} de {len(base)}",
                    "activa": conteo > 0,
                    "link": None,
                    "texto": None
                }
            )

        # ------------------------------------------
        # VISTA ESTATAL
        # ------------------------------------------

        else:

            fecha = fechas.iloc[0]

            activa = pd.notna(fecha)

            # ---------- Link ----------

            link = None

            columna_link = config.get("columna_link")

            if columna_link:

                valor_link = base[columna_link].iloc[0]

                if pd.notna(valor_link):

                    valor_link = str(valor_link).strip()

                    if valor_link.startswith(
                        ("http://", "https://")
                    ):
                        link = valor_link

            # ---------- Texto ----------

            texto = None

            columna_texto = config.get("columna_texto")

            if columna_texto:

                valor_texto = base[columna_texto].iloc[0]

                if pd.notna(valor_texto):

                    valor_texto = str(valor_texto).strip()

                    if valor_texto:
                        texto = valor_texto

            # ---------- Guardar etapa ----------

            etapas.append(
                {
                    **config,
                    "valor": (
                        fecha.strftime("%d/%m/%Y")
                        if activa
                        else "Sin fecha"
                    ),
                    "activa": activa,
                    "link": link,
                    "texto": texto
                }
            )


    indicadores["etapas"] = etapas


    # ---------- Profesionalización ----------

    if base.empty:
        indicadores["capacitadas"] = None
        indicadores["paa"] = pd.DataFrame()
    else:
        indicadores["capacitadas"] = int(
            pd.to_numeric(base["cap_serv_pub"], errors="coerce")
            .fillna(0)
            .sum()
        )

        filas_paa = []

        for columna, (corta, larga) in ETIQUETAS_PAA.items():

            valor = int(
                pd.to_numeric(base[columna], errors="coerce")
                .fillna(0)
                .sum()
            )

            if valor > 0:
                filas_paa.append(
                    {
                        "institucion": corta,
                        "institucion_completa": larga,
                        "personas": valor
                    }
                )

        df_paa = pd.DataFrame(filas_paa)

        # Para que la gráfica sea legible se muestran las
        # instituciones con más personas capacitadas y el
        # resto se agrupa.
        if len(df_paa) > 7:

            df_paa = df_paa.sort_values("personas", ascending=False)

            principales = df_paa.head(6)
            restantes = df_paa.tail(len(df_paa) - 6)

            df_paa = pd.concat([
                principales,
                pd.DataFrame([{
                    "institucion": f"Otras {len(restantes)} instituciones",
                    "institucion_completa": " · ".join(
                        restantes["institucion_completa"]
                    ),
                    "personas": int(restantes["personas"].sum())
                }])
            ])

        indicadores["paa"] = df_paa

    return indicadores


indicadores = calcular_indicadores(
    datos_periodo,
    entidad_seleccionada
)


# --------------------------------------------------
# 10. DISTRIBUCION DE LA PANTALLA
# --------------------------------------------------

col_izquierda, col_derecha = st.columns([1, 1.28], gap="medium")


# --------------------------------------------------
# 11. GRADO DE CONSOLIDACION Y MAPA
# --------------------------------------------------

with col_izquierda:

    with st.container(key="tarjeta_mapa"):

        st.html('<div class="titulo-seccion">Grado de consolidación</div>')

        if es_nacional:
            nota_mapa = (
                f"Promedio de {indicadores['entidades']} entidades "
                "con información. Haz clic en un estado para filtrar."
            )
        else:
            nota_mapa = "Haz clic en el mapa para cambiar de entidad."

        st.html(f'<div class="nota-seccion">{nota_mapa}</div>')

        # Aviso cuando la entidad no reporta información
        if not indicadores["hay_informacion"]:

            st.html(
                f"""
                <div class="aviso-sin-informacion">
                    {entidad_seleccionada} no cuenta con información
                    disponible para el
                    {texto_trimestre(trimestre).lower()} de {anio}.
                </div>
                """
            )

        # ---------- Resumen del grado ----------

        filas_componentes = ""

        for componente in indicadores["componentes"]:

            puntos = componente["puntos"]
            maximo = componente["maximo"]

            if puntos is None or pd.isna(puntos):
                ancho = 0
            else:
                ancho = max(0, min(100, puntos / maximo * 100))

            filas_componentes += f"""
                <div class="cons-fila"
                     title="Aporta hasta {maximo:g} de los 100 puntos
                            del grado de consolidación">
                    <div>{componente['nombre']}</div>
                    <div class="cons-pista">
                        <span class="cons-relleno"
                              style="width: {ancho:.1f}%"></span>
                    </div>
                    <div class="cons-porcentaje">
                        {formato(puntos, 1)}
                        <span>/ {maximo:g}</span>
                    </div>
                </div>
            """

        st.html(
            f"""
            <div class="cons-encabezado">
                <div>
                    <div class="cons-entidad">{entidad_seleccionada}</div>
                    <div class="cons-valor">
                        {formato(indicadores["grado_total"], 1)}
                        <span>/ 100</span>
                    </div>
                </div>
                <div class="cons-componentes">
                    {filas_componentes}
                </div>
            </div>
            """
        )

        if not es_nacional:

            if st.button(
                "← Regresar a la vista nacional",
                key="boton_nacional"
            ):
                st.session_state["entidad_activa"] = NACIONAL
                st.rerun()

        # ---------- Preparación del mapa ----------

        mapa_datos = datos_periodo[
            ["nom_ent", "grado_cons_total", "tiene_informacion"]
        ].copy()

        # El GeoJSON nombra "México" al Estado de México
        equivalencias_mapa = {"Estado de México": "México"}

        mapa_datos["nombre_mapa"] = (
            mapa_datos["nom_ent"].replace(equivalencias_mapa)
        )

        mapa_datos["estado_informacion"] = mapa_datos.apply(
            lambda fila:
            (
                "Información de carácter institucional <br>"
                "no sujeta a actualización trimestral"
            )
                if fila["tiene_informacion"] == 0
                else f'{fila["grado_cons_total"]:.1f} / 100',
            axis=1
        )

        mapa_con_info = mapa_datos[
            mapa_datos["tiene_informacion"] == 1
        ]

        mapa_sin_info = mapa_datos[
            mapa_datos["tiene_informacion"] == 0
        ]

        fig_mapa = px.choropleth(
            mapa_con_info,
            geojson=geojson_mexico,
            locations="nombre_mapa",
            featureidkey="properties.name",
            color="grado_cons_total",
            hover_name="nom_ent",
            custom_data=["estado_informacion"],
            hover_data={
                "nombre_mapa": False,
                "grado_cons_total": False,
                "tiene_informacion": False,
                "estado_informacion": True
            },
            range_color=(0, 100),
            color_continuous_scale=ESCALA_MAPA,
            projection="mercator"
        )

        fig_mapa.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br><br>"
        "Grado de consolidación: %{customdata[0]}"
        "<extra></extra>"
    )
)

        fig_sin_info = px.choropleth(
            mapa_sin_info,
            geojson=geojson_mexico,
            locations="nombre_mapa",
            featureidkey="properties.name",
            hover_name="nom_ent",
            custom_data=["estado_informacion"],
            color_discrete_sequence=["#D9D9D9"],
            projection="mercator"
        )

        fig_sin_info.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br><br>"
                "%{customdata[0]}"
                "<extra></extra>"
            )
        )

        for trace in fig_sin_info.data:
            fig_mapa.add_trace(trace)

        for trace in fig_mapa.data:

            if trace.name == "":
                trace.hovertemplate = (
                    "<b>%{hovertext}</b><br><br>"
                    "%{customdata[0]}"
                    "<extra></extra>"
        )

        fig_mapa.update_traces(
            marker_line_color="#ffffff",
            marker_line_width=0.6,
            selector=dict(type="choropleth")
        )

        # Resaltar la entidad seleccionada
        if not es_nacional:

            nombre_mapa_activo = equivalencias_mapa.get(
                entidad_seleccionada,
                entidad_seleccionada
            )

            fig_mapa.add_trace(
                go.Choropleth(
                    geojson=geojson_mexico,
                    locations=[nombre_mapa_activo],
                    featureidkey="properties.name",
                    z=[1],
                    colorscale=[
                        [0, "rgba(0,0,0,0)"],
                        [1, "rgba(0,0,0,0)"]
                    ],
                    showscale=False,
                    marker_line_color=TINTA,
                    marker_line_width=2.5,
                    hoverinfo="skip"
                )
            )

        # Encuadre fijo del país: aprovecha mejor el espacio
        # de la tarjeta que el ajuste automático de Plotly.
        fig_mapa.update_geos(
            visible=False,
            bgcolor="rgba(0,0,0,0)",
            lonaxis_range=[-119.0, -85.8],
            lataxis_range=[14.1, 33.4]
        )

        fig_mapa.update_layout(
            coloraxis_showscale=False,
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            dragmode=False,
            hoverlabel=dict(
                bgcolor="#ffffff",
                bordercolor=VINO,
                font=dict(color=TINTA, size=12)
            )
        )

        # La clave incluye la entidad activa para que la selección
        # previa del mapa no vuelva a aplicarse cuando el cambio
        # se hace desde el selector.
        evento_mapa = st.plotly_chart(
            fig_mapa,
            width="stretch",
            key=f"mapa_{entidad_seleccionada}",
            on_select="rerun",
            selection_mode="points",
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "responsive": True
            }
        )

        st.html(
            """
            <div class="leyenda-mapa">
                <span>Bajo 0</span>
                <span class="leyenda-barra"></span>
                <span>100 Alto</span>
                <span style="margin-left:12px">
                    <span class="leyenda-sin-dato"></span>Sin información
                </span>
            </div>
            """
        )

        # ---------- Contexto del grado de consolidación ----------

        ranking = (
            datos_periodo[datos_periodo["tiene_informacion"] == 1]
            .sort_values("grado_cons_total", ascending=False)
            .reset_index(drop=True)
        )

        if not ranking.empty:

            promedio_nacional = ranking["grado_cons_total"].mean()

            if es_nacional:

                mayores = " · ".join(
                    f"{fila.nom_ent} <b>{fila.grado_cons_total:.1f}</b>"
                    for fila in ranking.head(3).itertuples()
                )

                menores = " · ".join(
                    f"{fila.nom_ent} <b>{fila.grado_cons_total:.1f}</b>"
                    for fila in ranking.tail(3)[::-1].itertuples()
                )

                st.html(
                    f"""
                    <div class="resumen-mapa">
                        <div>
                            <span class="resumen-etiqueta">Mayor grado</span>
                            {mayores}
                        </div>
                        <div>
                            <span class="resumen-etiqueta">Menor grado</span>
                            {menores}
                        </div>
                    </div>
                    """
                )

            else:

                posiciones = ranking.index[
                    ranking["nom_ent"] == entidad_seleccionada
                ]

                if len(posiciones) and indicadores["grado_total"] is not None:

                    posicion = (
                        f"<b>{int(posiciones[0]) + 1} de {len(ranking)}</b> "
                        "entidades"
                    )

                    diferencia = (
                        indicadores["grado_total"] - promedio_nacional
                    )

                    comparacion = (
                        f"<b>{diferencia:+.1f}</b> puntos"
                    )

                else:
                    posicion = "Sin información"
                    comparacion = "Sin información"

                st.html(
                    f"""
                    <div class="resumen-mapa">
                        <div>
                            <span class="resumen-etiqueta">
                                Posición nacional
                            </span>
                            {posicion}
                        </div>
                        <div>
                            <span class="resumen-etiqueta">
                                Respecto del promedio nacional
                                ({promedio_nacional:.1f})
                            </span>
                            {comparacion}
                        </div>
                    </div>
                    """
                )

        # ---------- Clic sobre el mapa ----------

        if evento_mapa.selection.points:

            punto = evento_mapa.selection.points[0]

            if "location" in punto:

                equivalencias_inversas = {"México": "Estado de México"}

                entidad_clic = equivalencias_inversas.get(
                    punto["location"],
                    punto["location"]
                )

                if entidad_clic != st.session_state["entidad_activa"]:

                    st.session_state["entidad_activa"] = entidad_clic
                    st.rerun()


    # ----------------------------------------------
    # 13. AVANCES DE LA IMPLEMENTACION
    # ----------------------------------------------

    with st.container(key="tarjeta_avances"):

        st.html(
            '<div class="titulo-seccion">'
            'Avances de la implementación</div>'
        )

        if es_nacional:
            nota_avances = (
                "Entidades que han concluido cada etapa "
                "de la política estatal."
            )
        else:
            nota_avances = (
                "Fechas registradas para cada etapa "
                "de la política estatal."
            )

        st.html(f'<div class="nota-seccion">{nota_avances}</div>')

        etapas_activas = [
            posicion
            for posicion, etapa in enumerate(indicadores["etapas"])
            if etapa["activa"]
        ]

        ultima_activa = max(etapas_activas) if etapas_activas else 0
        ancho_progreso = ultima_activa * 20
        etapas_html = ""

        for etapa in indicadores["etapas"]:

            clase = "" if etapa["activa"] else " inactiva"

            if not es_nacional and etapa.get("link"):
                link_seguro = html.escape(etapa["link"], quote=True)
                link_html = f"""
                    <a class="avance-link"
                       href="{link_seguro}"
                       target="_blank"
                       rel="noopener noreferrer"
                       title="Consultar documento">
                        {icono("link", VINO, 16)}
                    </a>
                """
            else:
                link_html = ""

            if not es_nacional and etapa.get("texto"):
                texto_seguro = html.escape(etapa["texto"])
                circulo_html = f"""
                    <details class="avance-info-etapa">
                        <summary class="avance-circulo"
                                 title="Ver información de la etapa">
                            {icono(
                                etapa["icono"],
                                VINO if etapa["activa"] else "#c3bdbf",
                                24
                            )}
                        </summary>
                        <div class="avance-info-contenido">
                            {texto_seguro}
                        </div>
                    </details>
                """
            else:
                circulo_html = f"""
                    <div class="avance-circulo">
                        {icono(
                            etapa["icono"],
                            VINO if etapa["activa"] else "#c3bdbf",
                            24
                        )}
                    </div>
                """

            etapas_html += f"""
                <div class="avance-etapa{clase}">
                    {circulo_html}

                    <div class="avance-nombre">
                        {etapa['nombre']}
                    </div>

                    <div class="avance-documento">
                        {link_html}
                    </div>

                    <div class="avance-valor">
                        {etapa['valor']}
                    </div>
                </div>
            """

        st.html(
            f"""
            <div class="avances-fila">
                <div class="avances-linea"></div>
                <div class="avances-progreso"
                     style="width: {ancho_progreso}%"></div>
                {etapas_html}
            </div>
            """
        )


# --------------------------------------------------
# 12. DESIGNACIONES VIGENTES
# --------------------------------------------------

with col_derecha:

    with st.container(key="tarjeta_designaciones"):

        st.html('<div class="titulo-seccion">Designaciones vigentes</div>')

        st.html(
            '<div class="nota-seccion">'
            'Integrantes designados respecto de las posiciones '
            'que corresponden.</div>'
        )

        tarjetas_html = ""
        hay_informacion = indicadores["hay_informacion"]

        for item in indicadores["designaciones"]:

            if item["clave"] == "tit" and not es_nacional:
                valor_tarjeta = "Sí" if item["vigentes"] == 1 else "No"
                meta_tarjeta = ""
            else:
                valor_tarjeta = (
                    item["vigentes"] if hay_informacion else "s/d"
                )
                meta_tarjeta = (
                    f"de {item['total']}"
                    if hay_informacion
                    else "Sin información"
                )

            tarjetas_html += f"""
                <div class="des-tarjeta"
                     style="--color: {item['color']};
                            --tinte: {aclarar(item['color'], 0.20)};
                            --borde: {aclarar(item['color'], 0.28)}"
                     title="{item['titulo']}">
                    <div class="des-icono">
                        {icono(item["icono"], "#ffffff", 20)}
                    </div>
                    <div class="des-titulo">{item['titulo']}</div>
                    <div class="des-valor">{valor_tarjeta}</div>
                    <div class="des-meta">{meta_tarjeta}</div>
                </div>
            """

        if hay_informacion:
            resumen_designaciones = (
                "<span>Total de designaciones vigentes</span>"
                f"<b>{indicadores['designaciones_vigentes']}</b>"
                f"<span>de {indicadores['designaciones_total']}</span>"
            )
        else:
            resumen_designaciones = (
                "<span>Sin información disponible "
                "para el periodo seleccionado</span>"
            )

        st.html(
            f"""
            <div class="grid-designaciones">{tarjetas_html}</div>
            <div class="des-resumen">{resumen_designaciones}</div>
            """
        )


    # ----------------------------------------------
    # 14. PDN Y PROFESIONALIZACION (ultima fila)
    # ----------------------------------------------

    col_pdn, col_profesionalizacion = st.columns(
        [1.15, 1],
        gap="small"
    )

    with col_pdn, st.container(key="tarjeta_pdn"):

        st.html(
            '<div class="titulo-seccion">'
            'Entes interconectados a la PDN</div>'
        )

        st.html(
            '<div class="nota-seccion">'
            'Entes públicos que reportan información en cada sistema '
            'de la Plataforma Digital Nacional.</div>'
        )

        sistemas_html = ""

        for sistema in indicadores["sistemas"]:

            porcentaje = (
                max(0, min(100, sistema["porcentaje"]))
                if indicadores["hay_informacion"]
                else 0
            )

            if indicadores["hay_informacion"]:
                valor_sistema = (
                    f"{sistema['entes']} "
                    f"<span>de {sistema['total']}</span>"
                )
                porcentaje_sistema = formato(
                    sistema["porcentaje"], 1, "%"
                )
            else:
                valor_sistema = "<span>Sin información</span>"
                porcentaje_sistema = ""

            sistemas_html += f"""
                <div class="pdn-sistema" title="{sistema['descripcion']}">
                    <div class="pdn-anillo"
                         style="--pct: {porcentaje:.1f}">
                        <div class="pdn-anillo-centro">
                            {sistema['titulo']}
                        </div>
                    </div>
                    <div class="pdn-valor">{valor_sistema}</div>
                    <div class="pdn-porcentaje">
                        {porcentaje_sistema}
                    </div>
                    <div class="pdn-descripcion">
                        {sistema['descripcion']}
                    </div>
                </div>
            """

        st.html(
            f"""
            <div class="pdn-contenido">

                <div class="grid-pdn">{sistemas_html}</div>

                <div class="pdn-separador"></div>

                <div class="pdn-total">
                    {icono("red", VINO, 32)}
                    <div class="pdn-total-titulo">
                        Total de interconexiones
                    </div>
                    <div class="pdn-total-valor">
                        {
                            f'{indicadores["pdn_entes"]:,}'
                            if indicadores["hay_informacion"]
                            else "s/d"
                        }
                        <span>
                            {
                                f'de {indicadores["pdn_total"]:,}'
                                if indicadores["hay_informacion"]
                                else ""
                            }
                        </span>
                    </div>
                    <div class="pdn-porcentaje">
                        {
                            formato(indicadores["pdn_porcentaje"], 1, "%")
                            if indicadores["hay_informacion"]
                            else ""
                        }
                    </div>
                </div>

            </div>
            """
        )


    # ----------------------------------------------
    # 15. PROFESIONALIZACION
    # ----------------------------------------------

    with col_profesionalizacion, st.container(
        key="tarjeta_profesionalizacion"
    ):

        st.html(
    f"""
    <div class="titulo-seccion">Profesionalización</div>

    <div class="prof-encabezado">
        <div class="prof-icono">{icono("finanzas", VINO, 26)}</div>

        <div class="prof-numero">
            {formato(indicadores["capacitadas"])}
        </div>

        <div class="prof-texto">
            Personas servidoras públicas<br>
            capacitadas por las SESEA
        </div>
    </div>

    <div class="prof-separador"></div>

    <div class="prof-subtitulo">
        Personas servidoras públicas capacitadas por la PAA
    </div>
    """
)

        df_paa = indicadores["paa"]

        if not df_paa.empty:

            df_paa = df_paa.sort_values(
                "personas",
                ascending=True
            )

            fig_paa = px.bar(
                df_paa,
                x="personas",
                y="institucion",
                orientation="h",
                text="personas",
                custom_data=["institucion_completa"]
            )

            fig_paa.update_traces(
                marker_color=VINO,
                texttemplate="%{text:,.0f}",
                textposition="outside",
                textfont=dict(size=9.5, color=TINTA),
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "%{x:,.0f} personas<extra></extra>"
                )
            )

            fig_paa.update_layout(
                autosize=True,
                margin=dict(l=0, r=46, t=0, b=0),
                bargroupgap=0,
                xaxis_title=None,
                yaxis_title=None,
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=9.5, color=TINTA),
                bargap=0.35
            )

            fig_paa.update_xaxes(
                visible=False,
                rangemode="tozero"
            )

            fig_paa.update_yaxes(
                showgrid=False,
                ticksuffix=" "
            )

            st.plotly_chart(
                fig_paa,
                width="stretch",
                config={
                    "displayModeBar": False,
                    "responsive": True
                }
            )

        else:

            st.html(
                '<div class="sin-dato">Sin registros de la Plataforma '
                'de Aprendizaje Anticorrupción en el periodo.</div>'
            )
