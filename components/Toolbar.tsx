"use client";

import { textoTrimestre } from "@/lib/format";
import DownloadButton, { type TipoDescarga } from "./DownloadButton";

export default function Toolbar({
  anios,
  anio,
  onAnioChange,
  trimestres,
  trimestre,
  onTrimestreChange,
  entidades,
  entidadActiva,
  onEntidadChange,
  iconosDescarga
}: {
  anios: number[];
  anio: number;
  onAnioChange: (anio: number) => void;
  trimestres: number[];
  trimestre: number;
  onTrimestreChange: (trimestre: number) => void;
  entidades: string[];
  entidadActiva: string;
  onEntidadChange: (entidad: string) => void;
  iconosDescarga: Record<TipoDescarga, string>;
}) {
  const periodo = `${textoTrimestre(trimestre).toLowerCase()} de ${anio}`;

  const descargas: Array<[TipoDescarga, string]> = [
    ["datos", "Descargar la base de datos completa (CSV)"],
    ["fichas", `Descargar las fichas estatales del ${periodo}`],
    ["informe", `Descargar el informe del ${periodo}`]
  ];

  return (
    <div className="toolbar">
      <div className="toolbar-titulo">
        <div className="titulo-barra">
          Tablero sobre la situación de los Sistemas Estatales
          Anticorrupción
        </div>
      </div>

      <div className="toolbar-campo">
        <label htmlFor="selector-anio">Año</label>
        <select
          id="selector-anio"
          value={anio}
          onChange={(evento) => onAnioChange(Number(evento.target.value))}
        >
          {anios.map((valor) => (
            <option key={valor} value={valor}>
              {valor}
            </option>
          ))}
        </select>
      </div>

      <div className="toolbar-campo">
        <label htmlFor="selector-trimestre">Trimestre</label>
        <select
          id="selector-trimestre"
          value={trimestre}
          onChange={(evento) =>
            onTrimestreChange(Number(evento.target.value))
          }
        >
          {trimestres.map((valor) => (
            <option key={valor} value={valor}>
              {textoTrimestre(valor)}
            </option>
          ))}
        </select>
      </div>

      <div className="toolbar-campo">
        <label htmlFor="selector-entidad">Entidad</label>
        <select
          id="selector-entidad"
          value={entidadActiva}
          onChange={(evento) => onEntidadChange(evento.target.value)}
        >
          {entidades.map((valor) => (
            <option key={valor} value={valor}>
              {valor}
            </option>
          ))}
        </select>
      </div>

      <div className="toolbar-descarga">
        {descargas.map(([tipo, etiqueta]) => (
          <DownloadButton
            key={tipo}
            tipo={tipo}
            anio={anio}
            trimestre={trimestre}
            iconoUri={iconosDescarga[tipo]}
            etiqueta={etiqueta}
          />
        ))}
      </div>
    </div>
  );
}
