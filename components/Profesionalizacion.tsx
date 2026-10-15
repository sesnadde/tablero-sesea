"use client";

import dynamic from "next/dynamic";
import type { Data, Layout } from "plotly.js";
import { formato } from "@/lib/format";
import { claveIcono } from "@/lib/iconKeys";
import { TINTA, VINO } from "@/lib/constants";
import type { FilaPaa } from "@/lib/types";
import { useAltoContenedor } from "@/lib/useAltoContenedor";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function Profesionalizacion({
  capacitadas,
  paa,
  iconos
}: {
  capacitadas: number | null;
  paa: FilaPaa[];
  iconos: Record<string, string>;
}) {
  // La gráfica llena el espacio que le deja la tarjeta, cuyo alto
  // marca la tarjeta de la PDN que comparte fila.
  const hayPaa = paa.length > 0;
  const [contenedorRef, alto, escala] =
    useAltoContenedor<HTMLDivElement>(hayPaa);

  const datosOrdenados = [...paa].sort((a, b) => a.personas - b.personas);

  const data: Data[] = [
    {
      type: "bar",
      orientation: "h",
      x: datosOrdenados.map((fila) => fila.personas),
      y: datosOrdenados.map((fila) => fila.institucion),
      text: datosOrdenados.map((fila) => String(fila.personas)),
      texttemplate: "%{text:,.0f}",
      textposition: "outside",
      textfont: { size: 9.5 * escala, color: TINTA },
      cliponaxis: false,
      marker: { color: VINO },
      customdata: datosOrdenados.map((fila) => [fila.institucion_completa]),
      hovertemplate:
        "<b>%{customdata[0]}</b><br>%{x:,.0f} personas<extra></extra>"
    }
  ];

  const layout: Partial<Layout> = {
    autosize: true,
    ...(alto ? { height: alto } : {}),
    margin: { l: 0, r: 46 * escala, t: 0, b: 0 },
    bargap: 0.35,
    xaxis: { visible: false, rangemode: "tozero" },
    yaxis: { showgrid: false, ticksuffix: " " },
    showlegend: false,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { size: 9.5 * escala, color: TINTA }
  };

  return (
    <div className="card card-profesionalizacion">
      <div className="titulo-seccion">Profesionalización</div>

      <div className="prof-encabezado">
        <div className="prof-icono">
          <img
            src={iconos[claveIcono("finanzas", VINO)]}
            width={26}
            height={26}
            alt=""
          />
        </div>

        <div className="prof-numero">{formato(capacitadas)}</div>

        <div className="prof-texto">
          Personas servidoras públicas
          <br />
          capacitadas por las SESEA
        </div>
      </div>

      <div className="prof-separador" />

      <div className="prof-subtitulo">
        Personas servidoras públicas capacitadas por la PAA
      </div>

      {hayPaa ? (
        <div className="profesionalizacion-plot-wrapper" ref={contenedorRef}>
          <Plot
            data={data}
            layout={layout}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%", height: "100%" }}
            useResizeHandler
          />
        </div>
      ) : (
        <div className="sin-dato">
          Sin registros de la Plataforma de Aprendizaje Anticorrupción en
          el periodo.
        </div>
      )}
    </div>
  );
}
