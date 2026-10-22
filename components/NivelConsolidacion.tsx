"use client";

import { ESCALA_MAPA, NIVELES_CONSOLIDACION } from "@/lib/constants";

// Punto de la escala del mapa que representa a cada nivel: 0% para
// N0 y el centro de su rango para N1 a N4.
const POSICION_NIVEL = [0, 0.13, 0.38, 0.63, 0.88];

function hexARgb(hex: string): [number, number, number] {
  const valor = parseInt(hex.slice(1), 16);
  return [(valor >> 16) & 255, (valor >> 8) & 255, valor & 255];
}

// Interpola el color de ESCALA_MAPA en t (0 a 1), igual que Plotly.
function colorEnEscala(t: number): [number, number, number] {
  for (let i = 1; i < ESCALA_MAPA.length; i++) {
    const [fin, colorFin] = ESCALA_MAPA[i];
    if (t <= fin) {
      const [inicio, colorInicio] = ESCALA_MAPA[i - 1];
      const f = (t - inicio) / (fin - inicio);
      const a = hexARgb(colorInicio);
      const b = hexARgb(colorFin);
      return [0, 1, 2].map((c) => Math.round(a[c] + (b[c] - a[c]) * f)) as [
        number,
        number,
        number
      ];
    }
  }
  return hexARgb(ESCALA_MAPA[ESCALA_MAPA.length - 1][1]);
}

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

          // Cada nivel lleva el color del mapa para su rango; los
          // niveles sin entidades (o que no son el de la entidad) se
          // atenúan, como el resto de estados en el mapa.
          const [r, g, b] = colorEnEscala(POSICION_NIVEL[posicion]);
          const oscuro = 0.299 * r + 0.587 * g + 0.114 * b < 150;

          return (
            <div
              key={item.nivel}
              className={`nivel-paso${activo ? " activo" : ""}${
                oscuro ? " oscuro" : ""
              }`}
              title={`${item.nivel} (${item.rango}): ${item.descripcion}`}
              style={{ backgroundColor: `rgb(${r}, ${g}, ${b})` }}
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

      {/* En la vista nacional los conteos de la escala bastan; el
          detalle solo se muestra para una entidad o si no hay datos. */}
      {esNacional && hayInformacion ? null : (
        <div className="nivel-detalle">
          {!hayInformacion || (nivel === null && !texto) ? (
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
      )}
    </div>
  );
}
