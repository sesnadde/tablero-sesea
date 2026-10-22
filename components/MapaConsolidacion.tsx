"use client";

import dynamic from "next/dynamic";
import type { Data, Layout, PlotMouseEvent } from "plotly.js";
import { useMemo } from "react";
import {
  ESCALA_MAPA,
  EQUIVALENCIAS_INVERSAS,
  EQUIVALENCIAS_MAPA,
  TINTA,
  VINO
} from "@/lib/constants";
import { formato, textoTrimestre } from "@/lib/format";
import type { Componente, FilaDatos } from "@/lib/types";
import { useAltoContenedor } from "@/lib/useAltoContenedor";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function MapaConsolidacion({
  entidadSeleccionada,
  esNacional,
  gradoTotal,
  componentes,
  entidadesConInformacion,
  hayInformacion,
  anio,
  trimestre,
  datosPeriodo,
  geojson,
  onVolverNacional,
  onEntidadClick
}: {
  entidadSeleccionada: string;
  esNacional: boolean;
  gradoTotal: number | null;
  componentes: Componente[];
  entidadesConInformacion: number;
  hayInformacion: boolean;
  anio: number;
  trimestre: number;
  datosPeriodo: FilaDatos[];
  geojson: GeoJSON.FeatureCollection;
  onVolverNacional: () => void;
  onEntidadClick: (entidad: string) => void;
}) {
  const notaMapa = esNacional
    ? `Promedio de ${entidadesConInformacion} entidades con información. Haz clic en un estado para filtrar.`
    : "Haz clic en el mapa para cambiar de entidad.";

  // El mapa ocupa el alto que deja libre la columna, que a su vez se
  // iguala al alto de la columna de designaciones/PDN. Las líneas y
  // letras se multiplican por la escala del tablero (ver
  // useAltoContenedor).
  const [mapaRef, altoMapa, escala] = useAltoContenedor<HTMLDivElement>();

  const { data, layout } = useMemo(() => {
    const conInfo = datosPeriodo.filter((fila) => fila.tiene_informacion === 1);
    const sinInfo = datosPeriodo.filter((fila) => fila.tiene_informacion !== 1);

    const nombreMapa = (nomEnt: string) =>
      EQUIVALENCIAS_MAPA[nomEnt] ?? nomEnt;

    // Con una entidad seleccionada, el resto se atenúa para que ella
    // destaque sin necesidad de un contorno grueso.
    const opacidadBase = esNacional ? 1 : 0.4;

    // Se construyen como objetos simples (no como el tipo Data, una
    // unión de variantes de traza) y se convierten al final: así no
    // hace falta repetir el cast de "geojson" en cada una.
    const trazasCrudas: Record<string, unknown>[] = [];

    trazasCrudas.push({
      type: "choropleth",
      geojson,
      featureidkey: "properties.name",
      locations: conInfo.map((fila) => nombreMapa(fila.nom_ent)),
      z: conInfo.map((fila) => fila.grado_cons_total ?? 0),
      zmin: 0,
      zmax: 100,
      colorscale: ESCALA_MAPA,
      showscale: false,
      marker: {
        opacity: opacidadBase,
        line: { color: "#ffffff", width: 0.6 * escala }
      },
      hovertext: conInfo.map((fila) => fila.nom_ent),
      customdata: conInfo.map((fila) => [
        `${(fila.grado_cons_total ?? 0).toFixed(1)}%`
      ]),
      hovertemplate:
        "<b>%{hovertext}</b><br><br>Grado de consolidación: %{customdata[0]}<extra></extra>"
    });

    trazasCrudas.push({
      type: "choropleth",
      geojson,
      featureidkey: "properties.name",
      locations: sinInfo.map((fila) => nombreMapa(fila.nom_ent)),
      z: sinInfo.map(() => 1),
      colorscale: [
        [0, "#D9D9D9"],
        [1, "#D9D9D9"]
      ],
      showscale: false,
      marker: {
        opacity: opacidadBase,
        line: { color: "#ffffff", width: 0.6 * escala }
      },
      hovertext: sinInfo.map((fila) => fila.nom_ent),
      customdata: sinInfo.map(() => [
        "Información de carácter institucional <br>no sujeta a actualización trimestral"
      ]),
      hovertemplate: "<b>%{hovertext}</b><br><br>%{customdata[0]}<extra></extra>"
    });

    if (!esNacional) {
      const nombreMapaActivo = nombreMapa(entidadSeleccionada);
      const filaActiva = conInfo.find(
        (fila) => fila.nom_ent === entidadSeleccionada
      );

      // La entidad se vuelve a dibujar encima, a color completo y con
      // un borde blanco fino (apenas más que el del resto) para no
      // deformar su contorno.
      trazasCrudas.push({
        type: "choropleth",
        geojson,
        featureidkey: "properties.name",
        locations: [nombreMapaActivo],
        ...(filaActiva
          ? {
              z: [filaActiva.grado_cons_total ?? 0],
              zmin: 0,
              zmax: 100,
              colorscale: ESCALA_MAPA
            }
          : {
              z: [1],
              colorscale: [
                [0, "#D9D9D9"],
                [1, "#D9D9D9"]
              ]
            }),
        showscale: false,
        marker: { line: { color: "#ffffff", width: 0.8 * escala } },
        hoverinfo: "skip"
      });
    }

    const trazas = trazasCrudas as unknown as Data[];

    const disenio: Partial<Layout> = {
      geo: {
        visible: false,
        bgcolor: "rgba(0,0,0,0)",
        lonaxis: { range: [-119.0, -85.8] },
        lataxis: { range: [14.1, 33.4] },
        projection: { type: "mercator" }
      },
      margin: { l: 0, r: 0, t: 0, b: 0 },
      showlegend: false,
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      dragmode: false,
      hoverlabel: {
        bgcolor: "#ffffff",
        bordercolor: VINO,
        font: { color: TINTA, size: 12 * escala }
      }
    };

    return { data: trazas, layout: disenio };
  }, [datosPeriodo, geojson, esNacional, entidadSeleccionada, escala]);

  const layoutMapa = useMemo<Partial<Layout>>(
    () => (altoMapa ? { ...layout, height: altoMapa } : layout),
    [layout, altoMapa]
  );

  function manejarClic(evento: Readonly<PlotMouseEvent>) {
    const punto = evento.points?.[0] as { location?: string } | undefined;
    if (!punto?.location) return;

    const entidadClic =
      EQUIVALENCIAS_INVERSAS[punto.location] ?? punto.location;

    if (entidadClic !== entidadSeleccionada) {
      onEntidadClick(entidadClic);
    }
  }

  return (
    <div className="card card-mapa">
      <div className="titulo-con-info">
        <div className="titulo-seccion">Grado de consolidación</div>

        <details className="avance-info">
          <summary title="Cómo se calcula el grado de consolidación">
            i
          </summary>
          <div className="avance-info-contenido">
            Cada componente (Implementación, Indicadores y Seguimiento y
            evaluación) se integra por varios reactivos con un peso
            asignado. Cuando un reactivo se cumple (&ldquo;Sí&rdquo;),
            aporta su peso en puntos; si no, aporta cero. Los tres
            componentes suman hasta 100 puntos, por lo que su suma es
            directamente el porcentaje de consolidación; junto a cada uno
            se indica lo que aporta y su máximo posible.
          </div>
        </details>
      </div>

      <div className="nota-seccion">{notaMapa}</div>

      {!hayInformacion && (
        <div className="aviso-sin-informacion">
          {entidadSeleccionada} no cuenta con información disponible para
          el {textoTrimestre(trimestre).toLowerCase()} de {anio}.
        </div>
      )}

      <div className="cons-encabezado">
        <div>
          <div className="cons-entidad">{entidadSeleccionada}</div>
          <div className="cons-valor">
            {formato(gradoTotal, 1)}
            <span>%</span>
          </div>
        </div>

        <div className="cons-componentes">
          {componentes.map((componente) => {
            // El valor es lo que el componente aporta al grado total (en
            // %); la barra muestra qué tanto de su máximo ha alcanzado.
            const ancho =
              componente.puntos === null
                ? 0
                : Math.max(
                    0,
                    Math.min(100, (componente.puntos / componente.maximo) * 100)
                  );

            return (
              <div
                className="cons-fila"
                key={componente.nombre}
                title={`Aporta hasta ${componente.maximo}% del grado de consolidación`}
              >
                <div>{componente.nombre}</div>
                <div className="cons-pista">
                  {/* El degradado abarca toda la pista (igual que la
                      leyenda del mapa), así el color final del relleno
                      corresponde al porcentaje alcanzado. */}
                  <span
                    className="cons-relleno"
                    style={{
                      width: `${ancho.toFixed(1)}%`,
                      backgroundSize:
                        ancho > 0 ? `${(10000 / ancho).toFixed(1)}% 100%` : undefined
                    }}
                  />
                </div>
                <div className="cons-porcentaje">
                  <span className="cons-aporte">
                    {formato(componente.puntos, 1, "%")}
                  </span>
                  <span className="cons-maximo">/ {componente.maximo}%</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {!esNacional && (
        <button
          type="button"
          className="btn-volver-nacional"
          onClick={onVolverNacional}
        >
          ← Regresar a la vista nacional
        </button>
      )}

      <div className="mapa-plot-wrapper" ref={mapaRef}>
        <Plot
          data={data}
          layout={layoutMapa}
          config={{
            displayModeBar: false,
            scrollZoom: false,
            responsive: true
          }}
          style={{ width: "100%", height: "100%" }}
          useResizeHandler
          onClick={manejarClic}
        />
      </div>

      <div className="leyenda-mapa">
        <span>Bajo 0%</span>
        <span className="leyenda-barra" />
        <span>100% Alto</span>
        <span style={{ marginLeft: 12 }}>
          <span className="leyenda-sin-dato" />
          Sin información
        </span>
      </div>
    </div>
  );
}
