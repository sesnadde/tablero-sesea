// Paleta institucional
export const VINO = "#9b2247";
export const VINO_OSCURO = "#611232";
export const ORO = "#a57f2c";
export const ORO_CLARO = "#e6d194";
export const GRIS = "#98989A";
export const TINTA = "#161a1d";

// Paleta complementaria para tarjetas de designaciones
export const COLORES_TARJETAS = [
  "#4F7187",
  "#397D86",
  "#6F8F82",
  "#7D8790",
  "#82758F"
];

// Escala del mapa (claro = bajo, oscuro = alto)
export const ESCALA_MAPA: Array<[number, string]> = [
  [0.0, "#f7f0e2"],
  [0.35, ORO_CLARO],
  [0.7, VINO],
  [1.0, VINO_OSCURO]
];

export const NACIONAL = "Nacional";

export interface ConfigDesignacion {
  clave: string;
  titulo: string;
  icono: string;
}

export const DESIGNACIONES: ConfigDesignacion[] = [
  { clave: "tit", titulo: "Titular SESEA", icono: "persona" },
  { clave: "cs", titulo: "Comité de Selección", icono: "grupo" },
  {
    clave: "cpc",
    titulo: "Comité de Participación Ciudadana",
    icono: "grupo"
  },
  { clave: "cc", titulo: "Comité Coordinador", icono: "grupo" },
  {
    clave: "crsf",
    titulo: "Comité Rector del Sistema de Fiscalización",
    icono: "grupo"
  }
];

export interface ConfigSistema {
  clave: string;
  titulo: string;
  descripcion: string;
  // Nombre completo del sistema, se muestra al pasar el cursor
  nombre: string;
}

export const SISTEMAS_PDN: ConfigSistema[] = [
  {
    clave: "s1",
    titulo: "S1",
    descripcion: "Declaraciones patrimoniales y de intereses",
    nombre:
      "Sistema de evolución patrimonial, de declaración de intereses y constancia de presentación de declaración fiscal"
  },
  {
    clave: "s2",
    titulo: "S2",
    descripcion: "Servidores públicos en contrataciones",
    nombre:
      "Sistema de los servidores públicos que intervengan en procedimientos de contrataciones públicas"
  },
  {
    clave: "s3",
    titulo: "S3",
    descripcion: "Servidores públicos y particulares sancionados",
    nombre:
      "Sistema nacional de servidores públicos y particulares sancionados"
  },
  {
    clave: "s6",
    titulo: "S6",
    descripcion: "Información pública de contrataciones",
    nombre:
      "Sistema de información pública de contrataciones"
  }
];

export interface ConfigEtapa {
  nombre: string;
  columna: string;
  icono: string;
  columna_link: string | null;
  columna_texto: string | null;
}

export const ETAPAS: ConfigEtapa[] = [
  {
    nombre: "Aprobación PEA",
    columna: "fecha_aprobacion_pea",
    icono: "lista",
    columna_link: "link_pea",
    columna_texto: "text_aprob_pea"
  },
  {
    nombre: "Aprobación del PI-PEA",
    columna: "fecha_aprobacion_pipea",
    icono: "grading",
    columna_link: "link_pipea",
    columna_texto: "text_aprob_pipea"
  },
  {
    nombre: "Ejecución del PI-PEA",
    columna: "fecha_ejecucion_pipea",
    icono: "play",
    columna_link: null,
    columna_texto: "text_ejec_pipea"
  },
  {
    nombre: "Metodología de seguimiento y evaluación",
    columna: "fecha_aprobacion_sye",
    icono: "grafica",
    columna_link: "link_sise",
    columna_texto: "text_metodologia_sise"
  },
  {
    nombre: "Evaluación de la política",
    columna: "fecha_evaluacion",
    icono: "check",
    columna_link: null,
    columna_texto: "text_evalua_politica"
  }
];

// Cada componente aporta puntos al grado de consolidación.
// Los tres suman los 100 puntos del índice.
export const COMPONENTES_GRADO: Array<[string, string, number]> = [
  ["Implementación", "grado_cons_implem_num", 67.5],
  ["Indicadores", "grado_cons_indic_num", 7.5],
  ["Seguimiento y evaluación", "grado_cons_sye_num", 25.0]
];

// Tabla 1. Grado de consolidación en la implementación de las
// políticas anticorrupción. El nivel de cada entidad viene como
// prefijo ("N3. ...") en la columna grado_cons_text.
export const NIVELES_CONSOLIDACION: Array<{
  nivel: string;
  rango: string;
  descripcion: string;
}> = [
  {
    nivel: "N0",
    rango: "0%",
    descripcion: "No cuenta con programa de implementación."
  },
  {
    nivel: "N1",
    rango: "1% al 25%",
    descripcion:
      "Existe un programa de implementación, pero no está en ejecución."
  },
  {
    nivel: "N2",
    rango: "26% al 50%",
    descripcion:
      "Existe un programa de implementación en ejecución, pero no genera informes de manera periódica de su implementación."
  },
  {
    nivel: "N3",
    rango: "51% al 75%",
    descripcion:
      "Existe un programa de implementación en ejecución, se generan reportes periódicos de la implementación, existen herramientas para el seguimiento y cuentan con indicadores aprobados por el CC-SEA."
  },
  {
    nivel: "N4",
    rango: "76% al 100%",
    descripcion:
      "Además de lo anterior, se integran reportes sobre los indicadores aprobados por el CC-SEA, realizan evaluaciones e implementan estrategias a partir de sus hallazgos."
  }
];

// Etiqueta corta para la gráfica y nombre completo para el detalle
export const ETIQUETAS_PAA: Record<string, [string, string]> = {
  paa_osf: ["Auditoría Superior", "Auditoría Superior"],
  paa_sesea: [
    "SESEA",
    "Secretaría Ejecutiva del Sistema Estatal Anticorrupción"
  ],
  paa_fecc: [
    "Fiscalía Anticorrupción",
    "Fiscalía Especializada Contra la Corrupción"
  ],
  paa_contraloria: [
    "Función Pública / SABG",
    "Secretaría Anticorrupción y Buen Gobierno / Función Pública"
  ],
  paa_cpc: [
    "Participación Ciudadana",
    "Comité de Participación Ciudadana"
  ],
  paa_judicatura: ["Judicatura", "Consejo de la Judicatura"],
  paa_tja: [
    "Justicia Administrativa",
    "Tribunal de Justicia Administrativa"
  ],
  paa_tdf: ["Coord. de Vigilancia", "Coordinación de Vigilancia"],
  paa_sesna: [
    "SESNA",
    "Secretaría Ejecutiva del Sistema Nacional Anticorrupción"
  ],
  pj: ["Poder Judicial", "Poder Judicial"],
  sh: ["Secretaría de Hacienda", "Secretaría de Hacienda"],
  tdj: ["Disciplina Judicial", "Tribunal de Disciplina Judicial"]
};

// El GeoJSON nombra "México" al Estado de México
export const EQUIVALENCIAS_MAPA: Record<string, string> = {
  "Estado de México": "México"
};

export const EQUIVALENCIAS_INVERSAS: Record<string, string> = {
  México: "Estado de México"
};

export const NOMBRE_BUCKET_DESCARGA = "Archivos";

export type TipoDocumento = "informe" | "fichas";

// Sufijo de cada documento del trimestre en el storage
const SUFIJOS_DOCUMENTO: Record<TipoDocumento, string> = {
  informe: "hallazgosvf",
  fichas: "compendiovf"
};

/** Nombre del PDF de un periodo, p. ej. informe_sea_2t_26_hallazgosvf.pdf */
export function nombreDocumento(
  tipo: TipoDocumento,
  anio: number,
  trimestre: number
): string {
  const anioCorto = String(anio).slice(-2);
  return `informe_sea_${trimestre}t_${anioCorto}_${SUFIJOS_DOCUMENTO[tipo]}.pdf`;
}
