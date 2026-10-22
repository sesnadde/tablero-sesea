import fs from "node:fs";
import path from "node:path";

const CARPETA_ICONOS = path.join(process.cwd(), "public", "icons");

export const ARCHIVOS_ICONOS: Record<string, string> = {
  persona: "person_100dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.svg",
  grupo: "groups_100dp_FFFFFF_FILL0_wght400_GRAD0_opsz48.svg",
  check: "check_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
  lista: "list_alt_check_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
  grading: "grading_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
  play: "play_arrow_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
  grafica: "graph_2_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
  red: "network_node_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
  finanzas: "finance_100dp_A31746_FILL0_wght400_GRAD0_opsz48.svg",
  link: "link_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
  database_down: "database-down.svg",
  informe: "informe.svg",
  fichas: "fichas.svg"
};

const cache = new Map<string, string>();

/** Lee un SVG local, sustituye su color de relleno y lo entrega como data URI. */
export function iconoUri(nombre: string, color = "#ffffff"): string {
  const clave = `${nombre}:${color}`;

  const enCache = cache.get(clave);
  if (enCache) return enCache;

  const archivo = ARCHIVOS_ICONOS[nombre];
  if (!archivo) return "";

  const ruta = path.join(CARPETA_ICONOS, archivo);
  if (!fs.existsSync(ruta)) return "";

  let svg = fs.readFileSync(ruta, "utf-8");

  svg = svg.replace(
    /fill="(#[0-9A-Fa-f]{3,8}|currentColor)"/g,
    `fill="${color}"`
  );

  const codificado = Buffer.from(svg, "utf-8").toString("base64");
  const uri = `data:image/svg+xml;base64,${codificado}`;

  cache.set(clave, uri);
  return uri;
}
