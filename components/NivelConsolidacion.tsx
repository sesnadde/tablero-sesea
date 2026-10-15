"use client";

import { NIVELES_CONSOLIDACION } from "@/lib/constants";

export default function NivelConsolidacion({
  nivel,
  texto,
  distribucion,
  hayInformacion,
  esNacional
}: {
  nivel: number | null;
  texto: string | null;
  distribucion: number[];
  hayInformacion: boolean;
  esNacional: boolean;
}) {
  const maximo = Math.max(1, ...distribucion);

  return (
    <div className="card card-nivel">
      <div className="titulo-seccion">
        Grado de consolidación de la política anticorrupción
      </div>
      <div className="nota-seccion">
        {esNacional
          ? "Número de entidades en cada nivel de consolidación en la implementación de la PEA."
          : "Nivel de consolidación en la implementación de la PEA."}
      </div>

      <div className="nivel-escala">
        {NIVELES_CONSOLIDACION.map((item, posicion) => {
          const conteo = distribucion[posicion] ?? 0;
          const activo = esNacional ? conteo > 0 : nivel === posicion;

          // En la vista nacional la intensidad del fondo crece con
          // el número de entidades en el nivel.
          const intensidad = esNacional ? conteo / maximo : activo ? 1 : 0;

          return (
            <div
              key={item.nivel}
              className={`nivel-paso${activo ? " activo" : ""}${
                intensidad >= 0.55 ? " oscuro" : ""
              }`}
              title={`${item.nivel} (${item.rango}): ${item.descripcion}`}
              style={{ "--intensidad": intensidad.toFixed(2) } as React.CSSProperties}
            >
              <div className="nivel-clave">{item.nivel}</div>
              <div className="nivel-rango">{item.rango}</div>
              {esNacional && hayInformacion ? (
                <div className="nivel-conteo">
                  {conteo} <span>{conteo === 1 ? "entidad" : "entidades"}</span>
                </div>
              ) : null}
            </div>
          );
        })}
      </div>

      <div className="nivel-detalle">
        {!hayInformacion ? (
          <span className="nivel-sin-dato">Sin información</span>
        ) : esNacional ? (
          <span className="nivel-sin-dato">
            Pasa el cursor sobre cada nivel para ver su descripción.
          </span>
        ) : nivel === null && !texto ? (
          <span className="nivel-sin-dato">Sin información</span>
        ) : (
          <>
            {nivel !== null ? (
              <span className="nivel-insignia">
                {NIVELES_CONSOLIDACION[nivel].nivel}
              </span>
            ) : null}
            <span className="nivel-texto">{texto}</span>
          </>
        )}
      </div>
    </div>
  );
}
