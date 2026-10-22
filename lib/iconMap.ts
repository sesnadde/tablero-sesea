import "server-only";
import { iconoUri } from "./icons";
import { DESIGNACIONES, ETAPAS, VINO } from "./constants";
import { COLOR_INACTIVO, claveIcono } from "./iconKeys";

/** Precalcula, en el servidor, todos los iconos (nombre+color) que la
 * interfaz necesita, para pasarlos como data URIs a los componentes
 * de cliente. */
export function construirMapaIconos(): Record<string, string> {
  const combinaciones = new Set<string>();

  for (const config of DESIGNACIONES) {
    combinaciones.add(claveIcono(config.icono, "#ffffff"));
  }

  for (const config of ETAPAS) {
    combinaciones.add(claveIcono(config.icono, VINO));
    combinaciones.add(claveIcono(config.icono, COLOR_INACTIVO));
  }

  combinaciones.add(claveIcono("link", VINO));
  combinaciones.add(claveIcono("red", VINO));
  combinaciones.add(claveIcono("finanzas", VINO));
  combinaciones.add(claveIcono("database_down", VINO));
  combinaciones.add(claveIcono("informe", VINO));
  combinaciones.add(claveIcono("fichas", VINO));

  const mapa: Record<string, string> = {};

  for (const clave of combinaciones) {
    const [nombre, color] = clave.split("|");
    mapa[clave] = iconoUri(nombre, color);
  }

  return mapa;
}
