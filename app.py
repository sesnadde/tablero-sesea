import os
import pandas as pd
import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go

from dotenv import load_dotenv
from supabase import create_client


# --------------------------------------------------
# 1. CONFIGURACION GENERAL
# --------------------------------------------------

st.set_page_config(
    page_title="Dashboard SESEA",
    page_icon="📊",
    layout="wide"
)

st.title("Informe Trimestral SESEA")
st.caption("Sistema Nacional Anticorrupción")


# --------------------------------------------------
# 2. CARGAR CREDENCIALES
# --------------------------------------------------

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SECRET_KEY")

if not supabase_url or not supabase_key:
    st.error("No se encontraron las credenciales de Supabase.")
    st.stop()


# --------------------------------------------------
# 3. CONECTAR CON SUPABASE
# --------------------------------------------------

supabase = create_client(
    supabase_url,
    supabase_key
)


# --------------------------------------------------
# 4. CARGAR DATOS
# --------------------------------------------------

@st.cache_data
def cargar_datos():

    respuesta = (
        supabase
        .table("dashboard_sesea")
        .select("*")
        .execute()
    )

    return pd.DataFrame(respuesta.data)


datos = cargar_datos()


# --------------------------------------------------
# 5. FILTROS DE PERIODO
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    anio = st.selectbox(
        "Año",
        sorted(datos["anio"].unique(), reverse=True)
    )

with col2:
    trimestres_disponibles = sorted(
        datos.loc[
            datos["anio"] == anio,
            "trimestre"
        ].unique()
    )

    trimestre = st.selectbox(
        "Trimestre",
        trimestres_disponibles
    )


# --------------------------------------------------
# 6. FILTRAR PERIODO
# --------------------------------------------------

datos_periodo = datos[
    (datos["anio"] == anio) &
    (datos["trimestre"] == trimestre)
].copy()


# --------------------------------------------------
# 7. SELECTOR DE ENTIDAD
# --------------------------------------------------

entidades = ["México"] + sorted(
    datos_periodo["nom_ent"].tolist()
)

# Inicializar entidad activa
if "entidad_activa" not in st.session_state:
    st.session_state["entidad_activa"] = "México"

# Sincronizar selector antes de crear el widget
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


st.selectbox(
    "Entidad",
    entidades,
    key="selector_entidad",
    on_change=actualizar_desde_selector
)

entidad_seleccionada = st.session_state["entidad_activa"]

# VISUAL MAPA DE MEXICO #

with open(
    "assets/estados_mexico.json",
    "r",
    encoding="utf-8"
) as archivo:
    geojson_mexico = json.load(archivo)

# --------------------------------------------------
# PREPARAR DATOS DEL MAPA
# --------------------------------------------------

mapa_datos = datos_periodo[
    [
        "nom_ent",
        "grado_cons_total",
        "tiene_informacion"
    ]
].copy()


# Ajuste de nombres entre Supabase y GeoJSON
equivalencias_mapa = {
    "Estado de México": "México"
}

mapa_datos["nombre_mapa"] = (
    mapa_datos["nom_ent"]
    .replace(equivalencias_mapa)
)


# --------------------------------------------------
# TEXTO PARA TOOLTIP
# --------------------------------------------------

mapa_datos["estado_informacion"] = mapa_datos.apply(
    lambda fila:
        "Sin información disponible"
        if fila["tiene_informacion"] == 0
        else f'{fila["grado_cons_total"]:.1f} / 100',
    axis=1
)

# SEPARA ENTIDADES CON Y SIN INFORMACION #

mapa_con_info = mapa_datos[
    mapa_datos["tiene_informacion"] == 1
].copy()

mapa_sin_info = mapa_datos[
    mapa_datos["tiene_informacion"] == 0
].copy()

# --------------------------------------------------
# MAPA DE GRADO DE CONSOLIDACION
# --------------------------------------------------

fig_mapa = px.choropleth(
    mapa_con_info,
    geojson=geojson_mexico,
    locations="nombre_mapa",
    featureidkey="properties.name",
    color="grado_cons_total",
    hover_name="nom_ent",

    hover_data={
        "nombre_mapa": False,
        "grado_cons_total": False,
        "tiene_informacion": False,
        "estado_informacion": True
    },

    range_color=(0, 100),

    labels={
        "estado_informacion": "Grado de consolidación",
        "grado_cons_total": "Grado de consolidación"
    },

    color_continuous_scale="Blues",
    projection="mercator"
)

fig_sin_info = px.choropleth(
    mapa_sin_info,
    geojson=geojson_mexico,
    locations="nombre_mapa",
    featureidkey="properties.name",
    hover_name="nom_ent",

    hover_data={
        "nombre_mapa": False,
        "grado_cons_total": False,
        "tiene_informacion": False,
        "estado_informacion": True
    },
    color_discrete_sequence=["#D9D9D9"],
    projection="mercator"
)

for trace in fig_sin_info.data:
    fig_mapa.add_trace(trace)

# --------------------------------------------------
# RESALTAR ENTIDAD SELECCIONADA
# --------------------------------------------------

if st.session_state["entidad_activa"] != "México":

    entidad_activa = st.session_state["entidad_activa"]

    # Ajustar nombre al usado por el GeoJSON
    nombre_mapa_activo = equivalencias_mapa.get(
        entidad_activa,
        entidad_activa
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

            marker_line_color="#111111",
            marker_line_width=4,

            hoverinfo="skip"
        )
    )

# --------------------------------------------------
# AJUSTAR VISTA GEOGRAFICA
# --------------------------------------------------


fig_mapa.update_geos(
    fitbounds="locations",
    visible=False
)


# --------------------------------------------------
# FORMATO GENERAL
# --------------------------------------------------

fig_mapa.update_layout(

    coloraxis_colorbar=dict(
        title="Grado de<br>consolidación",
        tickvals=[0, 20, 40, 60, 80, 100],
        ticksuffix=""
    ),

    margin=dict(
        l=0,
        r=0,
        t=10,
        b=0
    ),

    height=600
)

# --------------------------------------------------
# MOSTRAR MAPA
# --------------------------------------------------

st.subheader("Grado de consolidación")

evento_mapa = st.plotly_chart(
    fig_mapa,
    use_container_width=True,
    key="mapa_mexico",
    on_select="rerun",
    selection_mode="points"
)

# --------------------------------------------------
# CAPTURAR CLIC EN EL MAPA
# --------------------------------------------------

if evento_mapa.selection.points:

    punto = evento_mapa.selection.points[0]

    if "location" in punto:

        entidad_clic = punto["location"]

        # El GeoJSON llama "México" al Estado de México
        equivalencias_inversas = {
            "México": "Estado de México"
        }

        entidad_clic = equivalencias_inversas.get(
            entidad_clic,
            entidad_clic
        )

        if entidad_clic != st.session_state["entidad_activa"]:

            st.session_state["entidad_activa"] = entidad_clic

            st.rerun()


# --------------------------------------------------
# 9. INDICADORES DE GRADO DE CONSOLIDACION
# --------------------------------------------------

st.divider()

if entidad_seleccionada == "México":

    datos_validos = datos_periodo[
        datos_periodo["tiene_informacion"] == 1
    ]

    grado_total = datos_validos[
        "grado_cons_total"
    ].mean()

    grado_implementacion = datos_validos[
        "grado_cons_implem_num"
    ].mean()

    grado_indicadores = datos_validos[
        "grado_cons_indic_num"
    ].mean()

    grado_sye = datos_validos[
        "grado_cons_sye_num"
    ].mean()

    titulo_territorio = "México"

else:

    fila = datos_periodo[
        datos_periodo["nom_ent"] == entidad_seleccionada
    ].iloc[0]

    if fila["tiene_informacion"] == 0:

        st.info(
            "Sin información disponible para esta entidad en el periodo seleccionado."
        )

        st.stop()

    grado_total = fila["grado_cons_total"]
    grado_implementacion = fila["grado_cons_implem_num"]
    grado_indicadores = fila["grado_cons_indic_num"]
    grado_sye = fila["grado_cons_sye_num"]

    titulo_territorio = entidad_seleccionada

# --------------------------------------------------
# 9. TARJETA PRINCIPAL
# --------------------------------------------------

st.markdown(f"### {titulo_territorio}")

st.metric(
    label="Grado de consolidación",
    value=f"{grado_total:.1f} / 100"
)


# --------------------------------------------------
# 10. COMPONENTES DEL GRADO DE CONSOLIDACION
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        label="Implementación",
        value=f"{grado_implementacion * 100:.1f}%"
    )

with col2:

    st.metric(
        label="Indicadores",
        value=f"{grado_indicadores * 100:.1f}%"
    )

with col3:

    st.metric(
        label="Seguimiento y evaluación",
        value=f"{grado_sye * 100:.1f}%"
    )


# --------------------------------------------------
# 11. NOTA METODOLOGICA
# --------------------------------------------------

if entidad_seleccionada == "México":

    st.caption(
        f"Promedio nacional calculado con {len(datos_validos)} entidades con información disponible."
    )

#### SECCION DESIGNACIONES ####

st.divider()

st.subheader("Designaciones Vigentes")

# --------------------------------------------------
# 13.1 CALCULOS DE DESIGNACIONES
# --------------------------------------------------

if entidad_seleccionada == "México":

    # Se consideran únicamente las entidades
    # con información disponible
    datos_designaciones = datos_periodo[
        datos_periodo["tiene_informacion"] == 1
    ].copy()


    # --------------------------------------------------
    # TITULAR SESEA
    # --------------------------------------------------

    titular_vigentes = int(
        datos_designaciones["des_vig_tit"].sum()
    )

    titular_pendientes = int(
        datos_designaciones["des_pend_tit"].sum()
    )

    titular_total = (
        titular_vigentes
        + titular_pendientes
    )


    # --------------------------------------------------
    # COMITE DE SELECCION
    # --------------------------------------------------

    cs_vigentes = int(
        datos_designaciones["des_vig_cs"].sum()
    )

    cs_pendientes = int(
        datos_designaciones["des_pend_cs"].sum()
    )

    cs_total = (
        cs_vigentes
        + cs_pendientes
    )


    # --------------------------------------------------
    # COMITE DE PARTICIPACION CIUDADANA
    # --------------------------------------------------

    cpc_vigentes = int(
        datos_designaciones["des_vig_cpc"].sum()
    )

    cpc_pendientes = int(
        datos_designaciones["des_pend_cpc"].sum()
    )

    cpc_total = (
        cpc_vigentes
        + cpc_pendientes
    )


    # --------------------------------------------------
    # COMITE COORDINADOR
    # --------------------------------------------------

    cc_vigentes = int(
        datos_designaciones["des_vig_cc"].sum()
    )

    cc_pendientes = int(
        datos_designaciones["des_pend_cc"].sum()
    )

    cc_total = (
        cc_vigentes
        + cc_pendientes
    )


    # --------------------------------------------------
    # COMITE RECTOR DEL SISTEMA DE FISCALIZACION
    # --------------------------------------------------

    crsf_vigentes = int(
        datos_designaciones["des_vig_crsf"].sum()
    )

    crsf_pendientes = int(
        datos_designaciones["des_pend_crsf"].sum()
    )

    crsf_total = (
        crsf_vigentes
        + crsf_pendientes
    )


else:

    # --------------------------------------------------
    # DATOS DE LA ENTIDAD SELECCIONADA
    # --------------------------------------------------

    fila_designaciones = datos_periodo[
        datos_periodo["nom_ent"] == entidad_seleccionada
    ].iloc[0]


    # --------------------------------------------------
    # ENTIDAD SIN INFORMACION
    # --------------------------------------------------

    if fila_designaciones["tiene_informacion"] == 0:

        titular_vigentes = 0
        titular_pendientes = 0
        titular_total = 0

        cs_vigentes = 0
        cs_pendientes = 0
        cs_total = 0

        cpc_vigentes = 0
        cpc_pendientes = 0
        cpc_total = 0

        cc_vigentes = 0
        cc_pendientes = 0
        cc_total = 0

        crsf_vigentes = 0
        crsf_pendientes = 0
        crsf_total = 0


    # --------------------------------------------------
    # ENTIDAD CON INFORMACION
    # --------------------------------------------------

    else:

        # TITULAR SESEA

        titular_vigentes = int(
            fila_designaciones["des_vig_tit"]
        )

        titular_pendientes = int(
            fila_designaciones["des_pend_tit"]
        )

        titular_total = (
            titular_vigentes
            + titular_pendientes
        )


        # COMITE DE SELECCION

        cs_vigentes = int(
            fila_designaciones["des_vig_cs"]
        )

        cs_pendientes = int(
            fila_designaciones["des_pend_cs"]
        )

        cs_total = (
            cs_vigentes
            + cs_pendientes
        )


        # COMITE DE PARTICIPACION CIUDADANA

        cpc_vigentes = int(
            fila_designaciones["des_vig_cpc"]
        )

        cpc_pendientes = int(
            fila_designaciones["des_pend_cpc"]
        )

        cpc_total = (
            cpc_vigentes
            + cpc_pendientes
        )


        # COMITE COORDINADOR

        cc_vigentes = int(
            fila_designaciones["des_vig_cc"]
        )

        cc_pendientes = int(
            fila_designaciones["des_pend_cc"]
        )

        cc_total = (
            cc_vigentes
            + cc_pendientes
        )


        # COMITE RECTOR DEL SISTEMA DE FISCALIZACION

        crsf_vigentes = int(
            fila_designaciones["des_vig_crsf"]
        )

        crsf_pendientes = int(
            fila_designaciones["des_pend_crsf"]
        )

        crsf_total = (
            crsf_vigentes
            + crsf_pendientes
        )


# --------------------------------------------------
# 13.2 TOTAL GENERAL DE DESIGNACIONES
# --------------------------------------------------

total_vigentes = (
    titular_vigentes
    + cs_vigentes
    + cpc_vigentes
    + cc_vigentes
    + crsf_vigentes
)

total_pendientes = (
    titular_pendientes
    + cs_pendientes
    + cpc_pendientes
    + cc_pendientes
    + crsf_pendientes
)

total_designaciones = (
    total_vigentes
    + total_pendientes
)


# TEXTO PARA TITULAR SESEA #

if entidad_seleccionada == "México":
    titular_visual = f"{titular_vigentes} de {titular_total}"
else:
    titular_visual = "Sí" if titular_vigentes > 0 else "No"

# --------------------------------------------------
# 13.3 ESTILOS CSS DE LAS TARJETAS
# --------------------------------------------------

st.html(
    """
    <style>

    .designacion-card {
        border: 1px solid #D9D9D9;
        border-radius: 10px;
        padding: 18px 10px;
        text-align: center;
        background-color: #FFFFFF;
        height: 210px;
        box-sizing: border-box;

        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }

    .designacion-titulo {
        font-size: 15px;
        font-weight: 600;
        line-height: 1.25;
        color: #333333;
        min-height: 55px;

        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .designacion-icono {
        font-size: 30px;
        line-height: 1;
        margin: 6px 0;
    }

    .designacion-valor {
        font-size: 32px;
        font-weight: 700;
        color: #1F4E79;
        line-height: 1.1;
        text-align: center;
    }

    .designacion-unidad {
        font-size: 12px;
        color: #6B7280;
        min-height: 20px;
        text-align: center;
    }

    .total-designaciones {
        border: 1px solid #D9D9D9;
        border-radius: 10px;
        padding: 12px 20px;
        background-color: #F7F7F7;
        text-align: center;
        margin-top: 16px;
        box-sizing: border-box;
    }

    .total-designaciones-titulo {
        font-size: 13px;
        font-weight: 600;
        color: #555555;
    }

    .total-designaciones-valor {
        font-size: 34px;
        font-weight: 700;
        color: #1F4E79;
        margin-top: 4px;
    }

    </style>
    """
)


# --------------------------------------------------
# 13.4 CREAR LAS CINCO COLUMNAS
# --------------------------------------------------

col_titular, col_cs, col_cpc, col_cc, col_crsf = st.columns(5)


# --------------------------------------------------
# TITULAR SESEA
# --------------------------------------------------

with col_titular:

    st.html(
        f"""
        <div class="designacion-card">

            <div class="designacion-titulo">
                Titular SESEA
            </div>

            <div class="designacion-icono">
                👤
            </div>

            <div class="designacion-valor">
                {titular_visual}
            </div>

            <div class="designacion-unidad">
                Titular vigente
            </div>

        </div>
        """
    )


# --------------------------------------------------
# COMITE DE SELECCION
# --------------------------------------------------

with col_cs:

    st.html(
        f"""
        <div class="designacion-card">

            <div class="designacion-titulo">
                Comité de Selección (CS)
            </div>

            <div class="designacion-icono">
                👥
            </div>

            <div class="designacion-valor">
                {cs_vigentes} de {cs_total}
            </div>

            <div class="designacion-unidad">
                Designaciones vigentes
            </div>

        </div>
        """
    )


# --------------------------------------------------
# COMITE DE PARTICIPACION CIUDADANA
# --------------------------------------------------

with col_cpc:

    st.html(
        f"""
        <div class="designacion-card">

            <div class="designacion-titulo">
                Comité de Participación Ciudadana (CPC)
            </div>

            <div class="designacion-icono">
                👥
            </div>

            <div class="designacion-valor">
                {cpc_vigentes} de {cpc_total}
            </div>

            <div class="designacion-unidad">
                Designaciones vigentes
            </div>

        </div>
        """
    )


# --------------------------------------------------
# COMITE COORDINADOR
# --------------------------------------------------

with col_cc:

    st.html(
        f"""
        <div class="designacion-card">

            <div class="designacion-titulo">
                Comité Coordinador (CC)
            </div>

            <div class="designacion-icono">
                👥
            </div>

            <div class="designacion-valor">
                {cc_vigentes} de {cc_total}
            </div>

            <div class="designacion-unidad">
                Designaciones vigentes
            </div>

        </div>
        """
    )


# --------------------------------------------------
# COMITE RECTOR DEL SISTEMA DE FISCALIZACION
# --------------------------------------------------

with col_crsf:

    st.html(
        f"""
        <div class="designacion-card">

            <div class="designacion-titulo">
                Comité Rector del Sistema de Fiscalización (CRSF)
            </div>

            <div class="designacion-icono">
                👥
            </div>

            <div class="designacion-valor">
                {crsf_vigentes} de {crsf_total}
            </div>

            <div class="designacion-unidad">
                Designaciones vigentes
            </div>

        </div>
        """
    )


# --------------------------------------------------
# 13.5 TOTAL DE DESIGNACIONES
# --------------------------------------------------

col_espacio, col_total = st.columns([4, 1])

with col_total:

    st.html(
        f"""
        <div class="total-designaciones">

            <div class="total-designaciones-titulo">
                TOTAL DESIGNACIONES
            </div>

            <div class="total-designaciones-valor">
                {total_vigentes} de {total_designaciones}
            </div>

        </div>
        """
    )

# SECCION ENTES INTERCONECTADOS A LA PDN #

st.divider()

st.subheader("Entes Interconectados a la PDN")

# --------------------------------------------------
# 14.1 CALCULOS PDN
# --------------------------------------------------

if entidad_seleccionada == "México":

    # Considerar solo entidades con informacion disponible
    datos_pdn = datos_periodo[
        datos_periodo["tiene_informacion"] == 1
    ].copy()


    # SISTEMA 1

    s1_entes = int(
        datos_pdn["s1_entes"].sum()
    )

    s1_total = int(
        datos_pdn["s1_total"].sum()
    )

    cumplimiento_s1 = (
        (s1_entes / s1_total) * 100
        if s1_total > 0
        else 0
    )


    # SISTEMA 2

    s2_entes = int(
        datos_pdn["s2_entes"].sum()
    )

    s2_total = int(
        datos_pdn["s2_total"].sum()
    )

    cumplimiento_s2 = (
        (s2_entes / s2_total) * 100
        if s2_total > 0
        else 0
    )


    # SISTEMA 3

    s3_entes = int(
        datos_pdn["s3_entes"].sum()
    )

    s3_total = int(
        datos_pdn["s3_total"].sum()
    )

    cumplimiento_s3 = (
        (s3_entes / s3_total) * 100
        if s3_total > 0
        else 0
    )


    # SISTEMA 6

    s6_entes = int(
        datos_pdn["s6_entes"].sum()
    )

    s6_total = int(
        datos_pdn["s6_total"].sum()
    )

    cumplimiento_s6 = (
        (s6_entes / s6_total) * 100
        if s6_total > 0
        else 0
    )


else:

    # Tomar fila de la entidad seleccionada
    fila_pdn = datos_periodo[
        datos_periodo["nom_ent"] == entidad_seleccionada
    ].iloc[0]


    # --------------------------------------------------
    # ENTIDAD SIN INFORMACION
    # --------------------------------------------------

    if fila_pdn["tiene_informacion"] == 0:

        s1_entes = 0
        s1_total = 0
        cumplimiento_s1 = 0

        s2_entes = 0
        s2_total = 0
        cumplimiento_s2 = 0

        s3_entes = 0
        s3_total = 0
        cumplimiento_s3 = 0

        s6_entes = 0
        s6_total = 0
        cumplimiento_s6 = 0


    # --------------------------------------------------
    # ENTIDAD CON INFORMACION
    # --------------------------------------------------

    else:

        # SISTEMA 1

        s1_entes = int(
            fila_pdn["s1_entes"]
        )

        s1_total = int(
            fila_pdn["s1_total"]
        )

        cumplimiento_s1 = float(
            fila_pdn["cumplimiento_s1"]
        ) * 100


        # SISTEMA 2

        s2_entes = int(
            fila_pdn["s2_entes"]
        )

        s2_total = int(
            fila_pdn["s2_total"]
        )

        cumplimiento_s2 = float(
            fila_pdn["cumplimiento_s2"]
        ) * 100


        # SISTEMA 3

        s3_entes = int(
            fila_pdn["s3_entes"]
        )

        s3_total = int(
            fila_pdn["s3_total"]
        )

        cumplimiento_s3 = float(
            fila_pdn["cumplimiento_s3"]
        ) * 100


        # SISTEMA 6

        s6_entes = int(
            fila_pdn["s6_entes"]
        )

        s6_total = int(
            fila_pdn["s6_total"]
        )

        cumplimiento_s6 = float(
            fila_pdn["cumplimiento_s6"]
        ) * 100


# CALCULAR TOTAL DE INTERCONEXIONES #

total_interconexiones = (
    s1_entes
    + s2_entes
    + s3_entes
    + s6_entes
)

total_interconexiones_posibles = (
    s1_total
    + s2_total
    + s3_total
    + s6_total
)

cumplimiento_total_pdn = (
    (total_interconexiones / total_interconexiones_posibles) * 100
    if total_interconexiones_posibles > 0
    else 0
)

# --------------------------------------------------
# 14.2 ESTILOS CSS
# --------------------------------------------------

st.html(
    """
    <style>

    .pdn-card {
        border: 1px solid #D9D9D9;
        border-radius: 10px;
        padding: 18px 12px;
        text-align: center;
        background-color: #FFFFFF;
        height: 230px;
        box-sizing: border-box;

        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }

    .pdn-titulo {
        font-size: 15px;
        font-weight: 600;
        line-height: 1.25;
        color: #333333;
        min-height: 40px;

        display: flex;
        align-items: center;
        justify-content: center;
    }

    .pdn-subtitulo {
        font-size: 12px;
        color: #6B7280;
        min-height: 34px;

        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .pdn-icono {
        font-size: 30px;
        line-height: 1;
        margin: 4px 0;
    }

    .pdn-valor {
        font-size: 31px;
        font-weight: 700;
        color: #1F4E79;
        line-height: 1.1;
    }

    .pdn-porcentaje {
        font-size: 22px;
        font-weight: 700;
        color: #4B5563;
        line-height: 1.1;
    }

    .pdn-unidad {
        font-size: 12px;
        color: #6B7280;
    }

    .pdn-total-card {
    border: 1px solid #D9D9D9;
    border-radius: 10px;
    padding: 18px 20px;
    background-color: #F7F7F7;
    text-align: center;
    margin-top: 16px;
    box-sizing: border-box;
    width:100%;
    min-height: 145px;

    display: flex;
    flex-direction: column;
    align-items: center
    justify-content: center;
    }

    .pdn-total-titulo {
    font-size: 13px;
    font-weight: 600;
    color: #555555;
    white-space: nowrap;
    }

   .pdn-total-valor {
    font-size: 34px;
    font-weight: 700;
    color: #1F4E79;
    margin-top: 4px;
    }

    .pdn-total-porcentaje {
    font-size: 20px;
    font-weight: 700;
    color:  #4B5563;
    margin-top: 6px;
    line-height: 1.1;
    white-space: nowrap;
    }

    </style>
    """
)


# --------------------------------------------------
# 14.3 CREAR LAS CUATRO COLUMNAS
# --------------------------------------------------

col_s1, col_s2, col_s3, col_s6 = st.columns(4)


# --------------------------------------------------
# SISTEMA 1
# --------------------------------------------------

with col_s1:

    st.html(
        f"""
        <div class="pdn-card">

            <div class="pdn-titulo">
                Sistema 1
            </div>

            <div class="pdn-subtitulo">
                Declaraciones patrimoniales y de intereses
            </div>

            <div class="pdn-icono">
                🔗
            </div>

            <div class="pdn-valor">
                {s1_entes} de {s1_total}
            </div>

            <div class="pdn-porcentaje">
                {cumplimiento_s1:.1f}%
            </div>

            <div class="pdn-unidad">
                Entes interconectados
            </div>

        </div>
        """
    )


# --------------------------------------------------
# SISTEMA 2
# --------------------------------------------------

with col_s2:

    st.html(
        f"""
        <div class="pdn-card">

            <div class="pdn-titulo">
                Sistema 2
            </div>

            <div class="pdn-subtitulo">
                Servidores públicos que intervienen en contrataciones
            </div>

            <div class="pdn-icono">
                🔗
            </div>

            <div class="pdn-valor">
                {s2_entes} de {s2_total}
            </div>

            <div class="pdn-porcentaje">
                {cumplimiento_s2:.1f}%
            </div>

            <div class="pdn-unidad">
                Entes interconectados
            </div>

        </div>
        """
    )


# --------------------------------------------------
# SISTEMA 3
# --------------------------------------------------

with col_s3:

    st.html(
        f"""
        <div class="pdn-card">

            <div class="pdn-titulo">
                Sistema 3
            </div>

            <div class="pdn-subtitulo">
                Servidores públicos y particulares sancionados
            </div>

            <div class="pdn-icono">
                🔗
            </div>

            <div class="pdn-valor">
                {s3_entes} de {s3_total}
            </div>

            <div class="pdn-porcentaje">
                {cumplimiento_s3:.1f}%
            </div>

            <div class="pdn-unidad">
                Entes interconectados
            </div>

        </div>
        """
    )


# --------------------------------------------------
# SISTEMA 6
# --------------------------------------------------

with col_s6:

    st.html(
        f"""
        <div class="pdn-card">

            <div class="pdn-titulo">
                Sistema 6
            </div>

            <div class="pdn-subtitulo">
                Información pública de contrataciones
            </div>

            <div class="pdn-icono">
                🔗
            </div>

            <div class="pdn-valor">
                {s6_entes} de {s6_total}
            </div>

            <div class="pdn-porcentaje">
                {cumplimiento_s6:.1f}%
            </div>

            <div class="pdn-unidad">
                Entes interconectados
            </div>

        </div>
        """
    )

    # TOTAL DE INTERCONEXIONES #

    col_espacio_pdn, col_total_pdn = st.columns([1.0, 0.5])

    with col_total_pdn:

        st.html(
            f"""
            <div class="pdn-total-card">

            <div class="pdn-total-titulo">
                 TOTAL INTERCONEXIONES
            </div>

            <div class="pdn-total-valor">
                 {total_interconexiones} de {total_interconexiones_posibles}
            <div>

            <div class="pdn-total-porcentaje">
                {cumplimiento_total_pdn:.1f}%
            <div>

         </div>   
         """      
)


# --------------------------------------------------
# LÍNEA DEL TIEMPO - DATOS Y VISUAL
# --------------------------------------------------

st.markdown("## Avances de la implementación")
st.markdown("### Línea del Tiempo")


# --------------------------------------------------
# CONFIGURACIÓN DE ETAPAS
# --------------------------------------------------

etapas_config = [
    {
        "nombre": "Aprobación PEA",
        "columna": "fecha_aprobacion_pea",
        "descripcion": "Aprobación formal de la Política Estatal Anticorrupción.",
        "icono": "✓"
    },
    {
        "nombre": "Aprobación del PI-PEA",
        "columna": "fecha_aprobacion_pipea",
        "descripcion": "Aprobación del programa para implementar la política estatal.",
        "icono": "▣"
    },
    {
        "nombre": "Ejecución del PI-PEA",
        "columna": "fecha_ejecucion_pipea",
        "descripcion": "Inicio de la ejecución del programa de implementación.",
        "icono": "▶"
    },
    {
        "nombre": "Metodología de seguimiento y evaluación",
        "columna": "fecha_aprobacion_sye",
        "descripcion": "Aprobación del mecanismo de seguimiento y evaluación.",
        "icono": "⌕"
    },
    {
        "nombre": "Evaluación de la política",
        "columna": "fecha_evaluacion",
        "descripcion": "Realización de la evaluación de la política estatal.",
        "icono": "✓"
    }
]


# --------------------------------------------------
# VISTA MÉXICO
# --------------------------------------------------

if entidad_seleccionada == "México":

    datos_timeline = datos_periodo[
        datos_periodo["tiene_informacion"] == 1
    ].copy()

    total_estados = len(datos_timeline)

    etapas_timeline = []

    for etapa in etapas_config:

        total_con_dato = (
            pd.to_datetime(
                datos_timeline[etapa["columna"]],
                errors="coerce"
            )
            .notna()
            .sum()
        )

        etapas_timeline.append(
            {
                "nombre": etapa["nombre"],
                "descripcion": etapa["descripcion"],
                "icono": etapa["icono"],
                "valor": f"{total_con_dato} de {total_estados}",
                "activa": total_con_dato > 0,
                "conteo": int(total_con_dato)
            }
        )


# --------------------------------------------------
# VISTA ESTATAL
# --------------------------------------------------

else:

    fila_timeline = datos_periodo[
        datos_periodo["nom_ent"] == entidad_seleccionada
    ]

    etapas_timeline = []

    if not fila_timeline.empty:

        fila_timeline = fila_timeline.iloc[0]

        for etapa in etapas_config:

            fecha = fila_timeline[etapa["columna"]]

            if pd.notna(fecha):

                fecha = pd.to_datetime(
                    fecha,
                    errors="coerce"
                )

                if pd.notna(fecha):
                    valor = fecha.strftime("%d/%m/%Y")
                    activa = True

                else:
                    valor = "Sin información"
                    activa = False

            else:
                valor = "Sin información"
                activa = False

            etapas_timeline.append(
                {
                    "nombre": etapa["nombre"],
                    "descripcion": etapa["descripcion"],
                    "icono": etapa["icono"],
                    "valor": valor,
                    "activa": activa
                }
            )


# --------------------------------------------------
# SEGMENTOS DE LA LÍNEA
# --------------------------------------------------

segmentos_activos = []

for i in range(4):

    etapa_actual = etapas_timeline[i]
    etapa_siguiente = etapas_timeline[i + 1]

    if entidad_seleccionada == "México":

        # En México se colorea el tramo si la etapa siguiente
        # tiene al menos una entidad con información.
        segmento_activo = etapa_siguiente["conteo"] > 0

    else:

        # En estados, el tramo se colorea solamente si
        # ambas etapas tienen fecha.
        segmento_activo = (
            etapa_actual["activa"]
            and etapa_siguiente["activa"]
        )

    segmentos_activos.append(segmento_activo)


# --------------------------------------------------
# CONSTRUCCIÓN DEL HTML
# --------------------------------------------------

html_timeline = """
<style>

.timeline-wrapper {
    width: 100%;
    margin-top: 30px;
    margin-bottom: 35px;
}

.timeline-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    position: relative;
    align-items: start;
}

.timeline-item {
    text-align: center;
    position: relative;
    z-index: 2;
    padding: 0 12px;
}

.timeline-circle {
    width: 78px;
    height: 78px;

    margin: 0 auto 18px auto;

    border-radius: 50%;

    display: flex;
    justify-content: center;
    align-items: center;

    font-size: 30px;
    font-weight: 700;

    border: 3px solid;
    background-color: white;

    position: relative;
    z-index: 3;
}

.timeline-circle.active {
    border-color: #6F3FA0;
    color: #6F3FA0;
}

.timeline-circle.inactive {
    border-color: #D0D0D0;
    color: #B5B5B5;
    background-color: #F5F5F5;
}

.timeline-title {
    font-size: 16px;
    font-weight: 700;
    line-height: 1.25;
    min-height: 50px;
    margin-bottom: 12px;
}

.timeline-value {
    display: inline-block;

    font-size: 14px;
    font-weight: 600;

    padding: 6px 12px;
    border-radius: 8px;

    margin-bottom: 14px;

    white-space: nowrap;
}

.timeline-value.active {
    color: #6F3FA0;
    border: 1px solid #6F3FA0;
    background-color: #F8F4FB;
}

.timeline-value.inactive {
    color: #8F8F8F;
    border: 1px solid #D0D0D0;
    background-color: #F3F3F3;
}

.timeline-description {
    font-size: 13px;
    line-height: 1.4;
    color: #555555;
}

.timeline-item.inactive .timeline-title,
.timeline-item.inactive .timeline-description {
    color: #9A9A9A;
}


/* -----------------------------------------------
   CONECTORES
------------------------------------------------ */

.timeline-connector {
    position: absolute;

    top: 38px;

    height: 4px;

    z-index: 1;
}

.connector-1 {
    left: 10%;
    width: 20%;
}

.connector-2 {
    left: 30%;
    width: 20%;
}

.connector-3 {
    left: 50%;
    width: 20%;
}

.connector-4 {
    left: 70%;
    width: 20%;
}

.connector-active {
    background-color: #6F3FA0;
}

.connector-inactive {
    background-color: #D8D8D8;
}

</style>


<div class="timeline-wrapper">

    <div class="timeline-row">
"""


# --------------------------------------------------
# CONECTORES
# --------------------------------------------------

for i, activo in enumerate(segmentos_activos, start=1):

    clase_conector = (
        "connector-active"
        if activo
        else "connector-inactive"
    )

    html_timeline += f"""
        <div
            class="timeline-connector connector-{i} {clase_conector}">
        </div>
    """


# --------------------------------------------------
# ETAPAS
# --------------------------------------------------

for etapa in etapas_timeline:

    clase_estado = (
        "active"
        if etapa["activa"]
        else "inactive"
    )

    html_timeline += f"""
        <div class="timeline-item {clase_estado}">

            <div class="timeline-circle {clase_estado}">
                {etapa["icono"]}
            </div>

            <div class="timeline-title">
                {etapa["nombre"]}
            </div>

            <div class="timeline-value {clase_estado}">
                {etapa["valor"]}
            </div>

            <div class="timeline-description">
                {etapa["descripcion"]}
            </div>

        </div>
    """


html_timeline += """
    </div>
</div>
"""


st.html(html_timeline)

# PROFESIONALIZACION #

st. markdown("## Profesionalización")

# Etiquetas de las variables PAA
etiquetas_paa = {
    "paa_judicatura": "Consejo de la Judicatura",
    "paa_contraloria": "Secretaría Anticorrupción y Buen Gobierno / Función Pública",
    "paa_cpc": "Comité de Participación Ciudadana",
    "paa_fecc": "Fiscalía Especializada Contra la Corrupción",
    "paa_osf": "Auditoría Superior",
    "paa_sesea": "Secretaría Ejecutiva del Sistema Estatal Anticorrupción",
    "paa_sesna": "Secretaría Ejecutiva del Sistema Nacional Anticorrupción",
    "paa_tdf": "Coordinación de Vigilancia",
    "paa_tja": "Tribunal de Justicia Administrativa"
}

columnas_paa = list(etiquetas_paa.keys())


# --------------------------------------------------
# DATOS SEGUN SELECCION
# --------------------------------------------------

if entidad_seleccionada == "México":

    datos_prof = datos_periodo[
        datos_periodo["tiene_informacion"] == 1
    ].copy()

    # Total nacional de personas servidoras públicas capacitadas
    cap_serv_pub = int(
        datos_prof["cap_serv_pub"]
        .fillna(0)
        .sum()
    )

    # Totales nacionales PAA
    valores_paa = {}

    for columna in columnas_paa:
        valores_paa[columna] = int(
            datos_prof[columna]
            .fillna(0)
            .sum()
        )

else:

    fila_prof = datos_periodo[
        datos_periodo["nom_ent"] == entidad_seleccionada
    ]

    if not fila_prof.empty:

        fila_prof = fila_prof.iloc[0]

        cap_serv_pub = int(
            pd.to_numeric(
                fila_prof["cap_serv_pub"],
                errors="coerce"
            )
            if pd.notna(fila_prof["cap_serv_pub"])
            else 0
        )

        valores_paa = {}

        for columna in columnas_paa:

            valor = fila_prof[columna]

            if pd.isna(valor):
                valor = 0

            valores_paa[columna] = int(valor)

    else:

        cap_serv_pub = 0

        valores_paa = {
            columna: 0
            for columna in columnas_paa
        }


# --------------------------------------------------
# VISUAL 1 - PERSONAS CAPACITADAS POR LA SESEA
# --------------------------------------------------

st.markdown("### Personas Servidoras Públicas capacitadas por la SESEA")

if cap_serv_pub > 0:


    st.html(
        f"""
        <div style="
            width: 100%;
            text-align: left;
            padding: 20px 0px 30px 0px;
        ">
            <div style="
                font-size: 72px;
                font-weight: 700;
                color: #0F4C81;
                line-height: 1;
            ">
                {cap_serv_pub:,}
            </div>
        </div>
        """
    )

else:

    st.html(
        """
        <div style="
            width: 100%;
            text-align: left;
            padding: 25px 0px 35px 0px;
        ">
            <div style="
                font-size: 28px;
                font-weight: 600;
                color: #8A8A8A;
            ">
                Sin información
            </div>
        </div>
        """
    )


# --------------------------------------------------
# VISUAL 2 - PLATAFORMA DE APRENDIZAJE ANTICORRUPCION
# --------------------------------------------------

st.markdown("### Plataforma de Aprendizaje Anticorrupción")

df_paa = pd.DataFrame([
    {
        "Institución": etiquetas_paa[columna],
        "Personas": valor
    }
    for columna, valor in valores_paa.items()
    if valor > 0
])

if not df_paa.empty:

    df_paa = (
        df_paa
        .sort_values(
            by="Personas",
            ascending=True
        )
        .reset_index(drop=True)
    )

    fig_paa = px.bar(
        df_paa,
        x="Personas",
        y="Institución",
        orientation="h",
        text="Personas"
    )

    fig_paa.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    fig_paa.update_layout(
        height=max(
            320,
            len(df_paa) * 55
        ),
        margin=dict(
            l=20,
            r=80,
            t=10,
            b=20
        ),
        xaxis_title="Personas capacitadas",
        yaxis_title=None,
        showlegend=False
    )

    fig_paa.update_xaxes(
        rangemode="tozero",
        tickformat=","
    )

    st.plotly_chart(
        fig_paa,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )

else:

    st.info("Sin información")
