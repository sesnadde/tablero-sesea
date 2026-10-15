"use client";

import type { FichaEspecial as FichaEspecialType } from "@/lib/types";

export default function FichaEspecial({
  ficha,
  entidad,
  onVolver
}: {
  ficha: FichaEspecialType;
  entidad: string;
  onVolver: () => void;
}) {
  return (
    <>
      <button
        type="button"
        className="btn-volver-nacional"
        onClick={onVolver}
      >
        ← Regresar a la vista nacional
      </button>

      <div className="ficha-especial">
        <div className="ficha-encabezado">
          <div className="ficha-etiqueta">
            Situación institucional especial
          </div>

          <div className="ficha-entidad">{entidad}</div>

          <div className="ficha-situacion">{ficha.situacion_actual}</div>

          <div className="ficha-nota">
            Información de carácter institucional no sujeta a
            actualización trimestral
          </div>
        </div>

        <div className="ficha-contenido">
          <div className="ficha-columna-situacion">
            <div className="ficha-titulo-seccion">Situación actual</div>
            <div className="ficha-texto">
              {ficha.situacion_institucional}
            </div>
          </div>

          <div className="ficha-columna-hechos">
            <div className="ficha-titulo-seccion">Hechos relevantes</div>
            <div className="ficha-hechos">
              {ficha.hechos_relevantes.map((hecho, indice) => (
                <div className="ficha-hecho" key={indice}>
                  <span className="ficha-vineta">•</span>
                  <span>{hecho}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="ficha-linea-bloque">
          <div className="ficha-titulo-seccion">Línea de tiempo</div>
          <div className="ficha-timeline">
            {ficha.linea_tiempo.map((evento, indice) => (
              <div className="ficha-evento" key={indice}>
                <div className="ficha-evento-punto" />
                <div className="ficha-evento-fecha">{evento.fecha}</div>
                <ul className="ficha-evento-textos">
                  {evento.eventos.map((punto, i) => (
                    <li key={i}>{punto}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
