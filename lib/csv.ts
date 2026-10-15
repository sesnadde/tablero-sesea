function escaparCelda(valor: unknown): string {
  if (valor === null || valor === undefined) return "";

  const texto =
    typeof valor === "object" ? JSON.stringify(valor) : String(valor);

  if (/[",\n\r]/.test(texto)) {
    return `"${texto.replace(/"/g, '""')}"`;
  }

  return texto;
}

/** Serializa filas a CSV con BOM UTF-8 (equivalente a to_csv + utf-8-sig). */
export function filasACsv(filas: Array<Record<string, unknown>>): string {
  if (filas.length === 0) return "﻿";

  const columnas = Object.keys(filas[0]);

  const encabezado = columnas.map(escaparCelda).join(",");

  const cuerpo = filas
    .map((fila) => columnas.map((columna) => escaparCelda(fila[columna])).join(","))
    .join("\r\n");

  return `﻿${encabezado}\r\n${cuerpo}`;
}
