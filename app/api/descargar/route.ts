import archiver from "archiver";
import { PassThrough } from "node:stream";
import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";
import { filasACsv } from "@/lib/csv";
import { ARCHIVOS_DESCARGA, NOMBRE_BUCKET_DESCARGA } from "@/lib/constants";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

// Se cachea en memoria de proceso para no volver a descargar los PDF
// (~20MB) del storage en cada clic, igual que @st.cache_data en la
// versión de Streamlit. Se invalida al reiniciar el servidor.
let paqueteCache: Buffer | null = null;

async function prepararPaqueteDescarga(): Promise<Buffer> {
  if (paqueteCache) return paqueteCache;

  const archivo = archiver("zip", { zlib: { level: 9 } });
  const flujo = new PassThrough();
  const partes: Buffer[] = [];

  flujo.on("data", (parte: Buffer) => partes.push(parte));

  const listo = new Promise<Buffer>((resolve, reject) => {
    flujo.on("end", () => resolve(Buffer.concat(partes)));
    archivo.on("error", reject);
  });

  archivo.pipe(flujo);

  for (const nombreArchivo of ARCHIVOS_DESCARGA) {
    const { data, error } = await supabase.storage
      .from(NOMBRE_BUCKET_DESCARGA)
      .download(nombreArchivo);

    if (error || !data) {
      throw new Error(
        `No se pudo descargar ${nombreArchivo} del storage: ${error?.message ?? "sin datos"}`
      );
    }

    const contenido = Buffer.from(await data.arrayBuffer());
    archivo.append(contenido, { name: nombreArchivo });
  }

  const { data: filas, error } = await supabase
    .from("dashboard_sesea")
    .select("*");

  if (error) {
    throw new Error(`No se pudo consultar dashboard_sesea: ${error.message}`);
  }

  const csv = filasACsv(filas ?? []);
  archivo.append(Buffer.from(csv, "utf-8"), { name: "dashboard_sesea.csv" });

  await archivo.finalize();

  const resultado = await listo;
  paqueteCache = resultado;
  return resultado;
}

export async function GET() {
  try {
    const zip = await prepararPaqueteDescarga();

    return new NextResponse(new Uint8Array(zip), {
      status: 200,
      headers: {
        "Content-Type": "application/zip",
        "Content-Disposition": 'attachment; filename="informes_sesea.zip"',
        "Content-Length": String(zip.length)
      }
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json(
      { error: "No se pudo preparar el archivo de descarga." },
      { status: 500 }
    );
  }
}
