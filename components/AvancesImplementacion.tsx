"use client";

import { useEffect, useRef, useState } from "react";
import { VINO } from "@/lib/constants";
import { claveIcono, COLOR_INACTIVO } from "@/lib/iconKeys";
import type { Etapa } from "@/lib/types";

export default function AvancesImplementacion({
  etapas,
  esNacional,
  entidad,
  iconos
}: {
  etapas: Etapa[];
  esNacional: boolean;
  entidad: string;
  iconos: Record<string, string>;
}) {
  const [indiceAbierto, setIndiceAbierto] = useState<number | null>(null);
  const dialogoRef = useRef<HTMLDialogElement>(null);

  const etapaAbierta = indiceAbierto === null ? null : etapas[indiceAbierto];

  // Si cambia la entidad o el periodo, la ventana se cierra para no
  // mostrar información de otra etapa.
  useEffect(() => {
    setIndiceAbierto(null);
  }, [etapas]);

  // <dialog> se abre con showModal() para obtener el fondo oscurecido,
  // el cierre con Esc y el foco atrapado dentro de la ventana.
  useEffect(() => {
    const dialogo = dialogoRef.current;
    if (!dialogo) return;

    if (etapaAbierta && !dialogo.open) dialogo.showModal();
    if (!etapaAbierta && dialogo.open) dialogo.close();
  }, [etapaAbierta]);

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

        {etapas.map((etapa, indice) => {
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
                <button
                  type="button"
                  className="avance-circulo avance-circulo-boton"
                  title="Ver información de la etapa"
                  onClick={() => setIndiceAbierto(indice)}
                >
                  {circuloContenido}
                </button>
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

      {!esNacional && (
        <p className="avances-nota">
          Nota: Los hitos se presentan según su secuencia de implementación.
          Cuando las fechas oficiales no siguen un orden cronológico, la
          visualización prioriza el orden de las etapas.
        </p>
      )}

      <dialog
        ref={dialogoRef}
        className="etapa-modal"
        aria-labelledby="etapa-modal-titulo"
        onClose={() => setIndiceAbierto(null)}
        onClick={(evento) => {
          // El contenido ocupa toda la ventana, así que un clic cuyo
          // destino es el propio <dialog> cae en el fondo oscurecido.
          if (evento.target === evento.currentTarget) {
            dialogoRef.current?.close();
          }
        }}
      >
        {etapaAbierta && (
          <div className="etapa-modal-contenido">
            <button
              type="button"
              className="etapa-modal-cerrar"
              aria-label="Cerrar"
              onClick={() => dialogoRef.current?.close()}
            >
              ×
            </button>

            <div className="etapa-modal-etiqueta">{entidad}</div>
            <h2 className="etapa-modal-titulo" id="etapa-modal-titulo">
              {etapaAbierta.nombre}
            </h2>
            <div className="etapa-modal-fecha">{etapaAbierta.valor}</div>

            <p className="etapa-modal-texto">{etapaAbierta.texto}</p>

            {etapaAbierta.link && (
              <a
                className="etapa-modal-link"
                href={etapaAbierta.link}
                target="_blank"
                rel="noopener noreferrer"
              >
                Consultar aquí
              </a>
            )}
          </div>
        )}
      </dialog>
    </div>
  );
}
