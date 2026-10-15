"use client";

import { useState } from "react";

export default function DownloadButton({
  iconoUri
}: {
  iconoUri: string;
}) {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(false);

  async function descargar() {
    setCargando(true);
    setError(false);

    try {
      const respuesta = await fetch("/api/descargar");
      if (!respuesta.ok) throw new Error("Respuesta no exitosa");

      const blob = await respuesta.blob();
      const url = URL.createObjectURL(blob);

      const enlace = document.createElement("a");
      enlace.href = url;
      enlace.download = "informes_sesea.zip";
      document.body.appendChild(enlace);
      enlace.click();
      enlace.remove();

      URL.revokeObjectURL(url);
    } catch {
      setError(true);
    } finally {
      setCargando(false);
    }
  }

  return (
    <button
      type="button"
      className="download-button"
      style={{ backgroundImage: `url("${iconoUri}")` }}
      onClick={descargar}
      disabled={cargando}
      title={
        error
          ? "No se pudo preparar la descarga, intenta de nuevo"
          : "Descargar los informes del trimestre y la base de datos completa"
      }
      aria-label="Descargar informes y base de datos"
    />
  );
}
