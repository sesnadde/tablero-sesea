"use client";

import { aclarar } from "@/lib/format";
import { claveIcono } from "@/lib/iconKeys";
import type { Designacion } from "@/lib/types";

export default function Designaciones({
  designaciones,
  designacionesVigentes,
  designacionesTotal,
  hayInformacion,
  esNacional,
  iconos
}: {
  designaciones: Designacion[];
  designacionesVigentes: number;
  designacionesTotal: number;
  hayInformacion: boolean;
  esNacional: boolean;
  iconos: Record<string, string>;
}) {
  return (
    <div className="card card-designaciones">
      <div className="titulo-seccion">Designaciones vigentes</div>
      <div className="nota-seccion">
        Integrantes designados respecto de las posiciones que
        corresponden.
      </div>

      <div className="grid-designaciones">
        {designaciones.map((item) => {
          let valorTarjeta: string | number;
          let metaTarjeta: string;

          if (item.clave === "tit" && !esNacional) {
            valorTarjeta = item.vigentes === 1 ? "Sí" : "No";
            metaTarjeta = "";
          } else {
            valorTarjeta = hayInformacion ? item.vigentes : "s/d";
            metaTarjeta = hayInformacion
              ? `de ${item.total}`
              : "Sin información";
          }

          const estilo = {
            "--color": item.color,
            "--tinte": aclarar(item.color, 0.2),
            "--borde": aclarar(item.color, 0.28)
          } as React.CSSProperties;

          return (
            <div
              className="des-tarjeta"
              style={estilo}
              title={item.titulo}
              key={item.clave}
            >
              <div className="des-icono">
                <img
                  src={iconos[claveIcono(item.icono, "#ffffff")]}
                  width={20}
                  height={20}
                  alt=""
                />
              </div>
              <div className="des-titulo">{item.titulo}</div>
              <div className="des-valor">{valorTarjeta}</div>
              <div className="des-meta">{metaTarjeta}</div>
            </div>
          );
        })}
      </div>

      {hayInformacion ? (
        <div className="des-resumen">
          <span>Total de designaciones vigentes</span>
          <b>{designacionesVigentes}</b>
          <span>de {designacionesTotal}</span>
        </div>
      ) : (
        <div className="des-resumen">
          <span>Sin información disponible para el periodo seleccionado</span>
        </div>
      )}
    </div>
  );
}
