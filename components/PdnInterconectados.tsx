"use client";

import { formato } from "@/lib/format";
import { claveIcono } from "@/lib/iconKeys";
import { VINO } from "@/lib/constants";
import type { Sistema } from "@/lib/types";

export default function PdnInterconectados({
  sistemas,
  pdnEntes,
  pdnTotal,
  pdnPorcentaje,
  hayInformacion,
  iconos
}: {
  sistemas: Sistema[];
  pdnEntes: number;
  pdnTotal: number;
  pdnPorcentaje: number;
  hayInformacion: boolean;
  iconos: Record<string, string>;
}) {
  return (
    <div className="card card-pdn">
      <div className="titulo-seccion">Entes interconectados a la PDN</div>
      <div className="nota-seccion">
        Entes públicos que reportan información en cada sistema de la
        Plataforma Digital Nacional.
      </div>

      <div className="pdn-contenido">
        <div className="grid-pdn">
          {sistemas.map((sistema) => {
            const porcentaje = hayInformacion
              ? Math.max(0, Math.min(100, sistema.porcentaje))
              : 0;

            return (
              <div
                className="pdn-sistema"
                title={`${sistema.titulo}. ${sistema.nombre}`}
                key={sistema.clave}
              >
                <div
                  className="pdn-anillo"
                  style={{ "--pct": porcentaje.toFixed(1) } as React.CSSProperties}
                >
                  <div className="pdn-anillo-centro">{sistema.titulo}</div>
                </div>
                <div className="pdn-valor">
                  {hayInformacion ? (
                    <>
                      {sistema.entes} <span>de {sistema.total}</span>
                    </>
                  ) : (
                    <span>Sin información</span>
                  )}
                </div>
                <div className="pdn-porcentaje">
                  {hayInformacion ? formato(sistema.porcentaje, 1, "%") : ""}
                </div>
                <div className="pdn-descripcion">{sistema.descripcion}</div>
              </div>
            );
          })}
        </div>

        <div className="pdn-separador" />

        <div className="pdn-total">
          <img
            src={iconos[claveIcono("red", VINO)]}
            width={32}
            height={32}
            alt=""
          />
          <div className="pdn-total-titulo">Total de interconexiones</div>
          <div className="pdn-total-valor">
            {hayInformacion ? pdnEntes.toLocaleString("es-MX") : "s/d"}
            <span>
              {hayInformacion ? ` de ${pdnTotal.toLocaleString("es-MX")}` : ""}
            </span>
          </div>
          <div className="pdn-porcentaje">
            {hayInformacion ? formato(pdnPorcentaje, 1, "%") : ""}
          </div>
        </div>
      </div>
    </div>
  );
}
