"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Mide el alto de un contenedor de gráfica y lee la escala del
 * tablero, y los actualiza cuando cambian.
 *
 * Las gráficas de Plotly no toman por sí solas el alto que les deja
 * el layout (useResizeHandler solo escucha el "resize" de la ventana),
 * así que se mide el contenedor y se pasa como layout.height.
 *
 * El contenedor compensa el zoom del tablero (ver globals.css), así
 * que las gráficas deben multiplicar sus tamaños de letra por `escala`
 * para verse proporcionales al resto.
 *
 * `activo` indica si el contenedor está montado; al cambiar, se vuelve
 * a observar.
 */
export function useAltoContenedor<T extends HTMLElement>(activo = true) {
  const ref = useRef<T>(null);
  const [alto, setAlto] = useState<number | null>(null);
  const [escala, setEscala] = useState(1);

  useEffect(() => {
    const contenedor = ref.current;
    if (!contenedor) return;

    // Al cambiar la escala del tablero cambia el tamaño visible del
    // contenedor, así que el mismo observador detecta ambas cosas.
    const observador = new ResizeObserver(([entrada]) => {
      setAlto(Math.floor(entrada.contentRect.height));

      const valor = parseFloat(
        getComputedStyle(contenedor).getPropertyValue("--escala")
      );
      setEscala(Number.isFinite(valor) && valor > 0 ? valor : 1);
    });

    observador.observe(contenedor);
    return () => observador.disconnect();
  }, [activo]);

  return [ref, alto, escala] as const;
}
