"use client";

import { useState } from "react";

export type TipoDescarga = "datos" | "informe" | "fichas";

const ERROR_GENERAL = "No se pudo preparar la descarga, intenta de nuevo";

export default function DownloadButton({
  tipo,
  anio,
  trimestre,
  iconoUri,
  etiqueta
}: {
  tipo: TipoDescarga;
  anio: number;
  trimestre: number;
  iconoUri: string;
  etiqueta: string;
}) {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function descargar() {
    setCargando(true);
    setError(null);

    try {
      const parametros = new URLSearchParams({
        tipo,
        anio: String(anio),
        trimestre: String(trimestre)
      });
      const respuesta = await fetch(`/api/descargar?${parametros}`);

      if (!respuesta.ok) {
        // Un 404 indica que el documento del periodo aún no se publica
        throw new Error(
          respuesta.status === 404
            ? "No hay documento disponible para este periodo"
            : ERROR_GENERAL
        );
      }

      // La base de datos llega como CSV; los PDF, como enlace firmado
      // que el storage ya entrega como descarga.
      const esCsv = tipo === "datos";
      const url = esCsv
        ? URL.createObjectURL(await respuesta.blob())
        : ((await respuesta.json()) as { url: string }).url;

      const enlace = document.createElement("a");
      enlace.href = url;
      if (esCsv) enlace.download = "dashboard_sesea.csv";
      document.body.appendChild(enlace);
      enlace.click();
      enlace.remove();

      if (esCsv) URL.revokeObjectURL(url);
    } catch (causa) {
      setError(causa instanceof Error ? causa.message : ERROR_GENERAL);
    } finally {
      setCargando(false);
    }
  }

  return (
    <button
      type="button"
      className={`download-button${error ? " con-error" : ""}`}
      style={{ backgroundImage: `url("${iconoUri}")` }}
      onClick={descargar}
      disabled={cargando}
      title={error ?? etiqueta}
      aria-label={etiqueta}
    />
  );
}
