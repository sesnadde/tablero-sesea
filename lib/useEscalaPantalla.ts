"use client";

import { useLayoutEffect, useRef, useState } from "react";

const ESCALA_MINIMA = 0.6;
const ESCALA_MAXIMA = 1.8;

// Si un salto de línea hace que la escala oscile entre dos valores,
// se deja de ajustar tras estos intentos seguidos.
const AJUSTES_MAXIMOS = 6;

/**
 * Escala el tablero de forma proporcional (CSS zoom) para que su alto
 * coincida con el de la ventana: lo agranda en pantallas altas y lo
 * reduce en pantallas bajas.
 *
 * El alto natural depende del ancho de layout, que a su vez cambia con
 * la escala; por eso se recalcula cada vez que el contenedor cambia de
 * tamaño hasta que el valor se estabiliza.
 *
 * Devuelve null en pantallas angostas, donde las columnas se apilan y
 * se hace scroll; entonces rige la --escala definida en globals.css.
 */
export function useEscalaPantalla<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [escala, setEscala] = useState<number | null>(null);

  useLayoutEffect(() => {
    const elemento = ref.current;
    if (!elemento) return;

    const angosta = window.matchMedia("(max-width: 1000px)");
    let cuadro = 0;
    let ajustes = 0;
    let reinicio = 0;

    function medir() {
      if (!elemento) return;

      if (angosta.matches) {
        setEscala(null);
        return;
      }

      // getBoundingClientRect devuelve el alto ya escalado (visible).
      const actual = parseFloat(getComputedStyle(elemento).zoom) || 1;
      const altoVisible = elemento.getBoundingClientRect().height;
      if (!altoVisible) return;

      // Se apunta 1px por debajo del alto de la ventana para que el
      // redondeo no haga aparecer la barra de scroll.
      const objetivo = Math.min(
        ESCALA_MAXIMA,
        Math.max(
          ESCALA_MINIMA,
          (actual * (window.innerHeight - 1)) / altoVisible
        )
      );

      // Reducir siempre está permitido (si no, el tablero desborda);
      // solo los aumentos se limitan para cortar oscilaciones.
      const reducir = objetivo < actual;
      if (!reducir && (objetivo - actual < 0.003 || ajustes >= AJUSTES_MAXIMOS)) {
        return;
      }

      ajustes += 1;
      window.clearTimeout(reinicio);
      reinicio = window.setTimeout(() => (ajustes = 0), 1000);

      setEscala(objetivo);
    }

    function programar() {
      cancelAnimationFrame(cuadro);
      cuadro = requestAnimationFrame(medir);
    }

    function alRedimensionar() {
      ajustes = 0;
      programar();
    }

    medir();

    const observador = new ResizeObserver(programar);
    observador.observe(elemento);
    window.addEventListener("resize", alRedimensionar);

    return () => {
      cancelAnimationFrame(cuadro);
      window.clearTimeout(reinicio);
      observador.disconnect();
      window.removeEventListener("resize", alRedimensionar);
    };
  }, []);

  return [ref, escala] as const;
}
