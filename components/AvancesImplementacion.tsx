"use client";

import { VINO } from "@/lib/constants";
import { claveIcono, COLOR_INACTIVO } from "@/lib/iconKeys";
import type { Etapa } from "@/lib/types";

export default function AvancesImplementacion({
  etapas,
  esNacional,
  iconos
}: {
  etapas: Etapa[];
  esNacional: boolean;
  iconos: Record<string, string>;
}) {
  const etapasActivas = etapas
    .map((etapa, indice) => (etapa.activa ? indice : -1))
    .filter((indice) => indice >= 0);

  const ultimaActiva = etapasActivas.length
    ? Math.max(...etapasActivas)
    : 0;
  const anchoProgreso = ultimaActiva * 20;

  const notaAvances = esNacional
    ? "Entidades que han concluido cada etapa de la política estatal."
    : "Fechas registradas para cada etapa de la política estatal.";

  return (
    <div className="card card-avances">
      <div className="titulo-seccion">Avances de la implementación</div>
      <div className="nota-seccion">{notaAvances}</div>

      <div className="avances-fila">
        <div className="avances-linea" />
        <div
          className="avances-progreso"
          style={{ width: `${anchoProgreso}%` }}
        />

        {etapas.map((etapa) => {
          const clase = etapa.activa
            ? "avance-etapa"
            : "avance-etapa inactiva";

          const colorIcono = etapa.activa ? VINO : COLOR_INACTIVO;
          const iconoUri = iconos[claveIcono(etapa.icono, colorIcono)];

          const linkHtml =
            !esNacional && etapa.link ? (
              <a
                className="avance-link"
                href={etapa.link}
                target="_blank"
                rel="noopener noreferrer"
                title="Consultar documento"
              >
                <img
                  src={iconos[claveIcono("link", VINO)]}
                  width={16}
                  height={16}
                  alt=""
                />
              </a>
            ) : null;

          const circuloContenido = (
            <img src={iconoUri} width={24} height={24} alt="" />
          );

          return (
            <div className={clase} key={etapa.nombre}>
              {!esNacional && etapa.texto ? (
                <details className="avance-info-etapa">
                  <summary
                    className="avance-circulo"
                    title="Ver información de la etapa"
                  >
                    {circuloContenido}
                  </summary>
                  <div className="avance-info-contenido">{etapa.texto}</div>
                </details>
              ) : (
                <div className="avance-circulo">{circuloContenido}</div>
              )}

              <div className="avance-nombre">{etapa.nombre}</div>

              <div className="avance-documento">{linkHtml}</div>

              <div className="avance-valor">{etapa.valor}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
