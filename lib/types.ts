export interface FilaDatos {
  nom_ent: string;
  id_ent: number | string;
  anio: number;
  trimestre: number;
  tiene_informacion: number;
  grado_cons_total: number | null;
  grado_cons_implem_num: number | null;
  grado_cons_indic_num: number | null;
  grado_cons_sye_num: number | null;
  des_pend_tit: number | null;
  des_pend_cs: number | null;
  des_pend_cpc: number | null;
  des_pend_cc: number | null;
  des_pend_crsf: number | null;
  des_vig_tit: number | null;
  des_vig_cs: number | null;
  des_vig_cpc: number | null;
  des_vig_cc: number | null;
  des_vig_crsf: number | null;
  s1_total: number | null;
  s2_total: number | null;
  s3_total: number | null;
  s6_total: number | null;
  s1_entes: number | null;
  s2_entes: number | null;
  s3_entes: number | null;
  s6_entes: number | null;
  cumplimiento_s1: number | null;
  cumplimiento_s2: number | null;
  cumplimiento_s3: number | null;
  cumplimiento_s6: number | null;
  fecha_aprobacion_pea: string | null;
  fecha_aprobacion_pipea: string | null;
  fecha_ejecucion_pipea: string | null;
  fecha_aprobacion_sye: string | null;
  fecha_evaluacion: string | null;
  cap_serv_pub: number | null;
  paa_judicatura: number | null;
  paa_contraloria: number | null;
  paa_cpc: number | null;
  paa_fecc: number | null;
  paa_osf: number | null;
  paa_sesea: number | null;
  paa_sesna: number | null;
  paa_tdf: number | null;
  paa_tja: number | null;
  pj: number | null;
  sh: number | null;
  tdj: number | null;
  link_pea: string | null;
  link_pipea: string | null;
  link_sise: string | null;
  text_aprob_pea: string | null;
  text_aprob_pipea: string | null;
  text_ejec_pipea: string | null;
  text_metodologia_sise: string | null;
  text_evalua_politica: string | null;
  grado_cons_text: string | null;
  [clave: string]: unknown;
}

export interface FichaEspecialEvento {
  fecha: string;
  eventos: string[];
}

export interface FichaEspecial {
  situacion_actual: string;
  situacion_institucional: string;
  hechos_relevantes: string[];
  linea_tiempo: FichaEspecialEvento[];
}

export type FichasEspeciales = Record<string, FichaEspecial>;

export interface Componente {
  nombre: string;
  puntos: number | null;
  maximo: number;
}

export interface Designacion {
  clave: string;
  titulo: string;
  icono: string;
  color: string;
  vigentes: number;
  total: number;
}

export interface Sistema {
  clave: string;
  titulo: string;
  descripcion: string;
  nombre: string;
  entes: number;
  total: number;
  porcentaje: number;
}

export interface Etapa {
  nombre: string;
  columna: string;
  icono: string;
  columna_link: string | null;
  columna_texto: string | null;
  valor: string;
  activa: boolean;
  link: string | null;
  texto: string | null;
}

export interface FilaPaa {
  institucion: string;
  institucion_completa: string;
  personas: number;
}

export interface Indicadores {
  nacional: boolean;
  hayInformacion: boolean;
  entidades: number;
  gradoTotal: number | null;
  componentes: Componente[];
  designaciones: Designacion[];
  designacionesVigentes: number;
  designacionesTotal: number;
  sistemas: Sistema[];
  pdnEntes: number;
  pdnTotal: number;
  pdnPorcentaje: number;
  etapas: Etapa[];
  capacitadas: number | null;
  paa: FilaPaa[];
  nivelConsolidacion: number | null;
  textoConsolidacion: string | null;
  distribucionNiveles: number[];
}
