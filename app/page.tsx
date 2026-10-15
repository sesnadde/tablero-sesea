import fs from "node:fs";
import path from "node:path";
import { supabase } from "@/lib/supabase";
import type { FichasEspeciales, FilaDatos } from "@/lib/types";
import Dashboard from "@/components/Dashboard";
import fichasEspeciales from "@/content/fichasEspeciales.json";
import { construirMapaIconos } from "@/lib/iconMap";

// Los datos se consultan en cada solicitud: la tabla se actualiza
// periódicamente desde cargar_supabase.py y el tablero debe reflejarlo.
export const dynamic = "force-dynamic";
export const revalidate = 0;

async function cargarDatos(): Promise<FilaDatos[]> {
  const { data, error } = await supabase
    .from("dashboard_sesea")
    .select("*");

  if (error) {
    throw new Error(`No se pudo consultar dashboard_sesea: ${error.message}`);
  }

  return (data ?? []) as FilaDatos[];
}

function cargarGeojson() {
  const ruta = path.join(process.cwd(), "public", "estados_mexico.json");
  const contenido = fs.readFileSync(ruta, "utf-8");
  return JSON.parse(contenido);
}

export default async function Page() {
  const datos = await cargarDatos();
  const geojson = cargarGeojson();
  const iconos = construirMapaIconos();

  return (
    <Dashboard
      datosIniciales={datos}
      geojson={geojson}
      fichasEspeciales={fichasEspeciales as FichasEspeciales}
      iconos={iconos}
    />
  );
}
