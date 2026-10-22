import { type NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";
import { filasACsv } from "@/lib/csv";
import {
  NOMBRE_BUCKET_DESCARGA,
  nombreDocumento,
  type TipoDocumento
} from "@/lib/constants";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

// Vigencia del enlace firmado a los PDF del storage (segundos)
const VIGENCIA_ENLACE = 60;

async function descargarDatos() {
  const { data: filas, error } = await supabase
    .from("dashboard_sesea")
    .select("*");

  if (error) {
    throw new Error(`No se pudo consultar dashboard_sesea: ${error.message}`);
  }

  return new NextResponse(filasACsv(filas ?? []), {
    status: 200,
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="dashboard_sesea.csv"'
    }
  });
}

// Los PDF (~10MB) no pasan por el servidor: se entrega un enlace
// firmado y el navegador los descarga directo del storage.
async function enlaceDocumento(
  tipo: TipoDocumento,
  anio: number,
  trimestre: number
) {
  const nombre = nombreDocumento(tipo, anio, trimestre);

  const { data, error } = await supabase.storage
    .from(NOMBRE_BUCKET_DESCARGA)
    .createSignedUrl(nombre, VIGENCIA_ENLACE, { download: nombre });

  if (error || !data) {
    return NextResponse.json(
      { error: `No hay documento disponible para el periodo (${nombre}).` },
      { status: 404 }
    );
  }

  return NextResponse.json({ url: data.signedUrl });
}

export async function GET(request: NextRequest) {
  const parametros = request.nextUrl.searchParams;
  const tipo = parametros.get("tipo");

  try {
    if (tipo === "datos") return await descargarDatos();

    if (tipo === "informe" || tipo === "fichas") {
      const anio = Number(parametros.get("anio"));
      const trimestre = Number(parametros.get("trimestre"));

      if (!Number.isInteger(anio) || ![1, 2, 3, 4].includes(trimestre)) {
        return NextResponse.json(
          { error: "Periodo no válido." },
          { status: 400 }
        );
      }

      return await enlaceDocumento(tipo, anio, trimestre);
    }

    return NextResponse.json(
      { error: "Tipo de descarga no válido." },
      { status: 400 }
    );
  } catch (error) {
    console.error(error);
    return NextResponse.json(
      { error: "No se pudo preparar la descarga." },
      { status: 500 }
    );
  }
}
