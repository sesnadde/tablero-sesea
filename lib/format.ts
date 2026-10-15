export function formato(
  valor: number | null | undefined,
  decimales = 0,
  sufijo = ""
): string {
  if (valor === null || valor === undefined || Number.isNaN(valor)) {
    return "s/d";
  }

  const texto = valor.toLocaleString("es-MX", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales
  });

  return `${texto}${sufijo}`;
}

export function textoTrimestre(numero: number): string {
  return `${Math.trunc(numero)}° Trimestre`;
}

export function aclarar(color: string, proporcion: number): string {
  const hex = color.replace("#", "");

  const canales = [0, 2, 4].map((posicion) =>
    parseInt(hex.slice(posicion, posicion + 2), 16)
  );

  const mezclados = canales.map((canal) =>
    Math.round(canal * proporcion + 255 * (1 - proporcion))
  );

  return `#${mezclados
    .map((canal) => canal.toString(16).padStart(2, "0"))
    .join("")}`;
}
