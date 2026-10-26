import {
  COMPONENTES_GRADO,
  DESIGNACIONES,
  ETAPAS,
  ETIQUETAS_PAA,
  NACIONAL,
  NIVELES_CONSOLIDACION,
  SISTEMAS_PDN,
  COLORES_TARJETAS
} from "./constants";
import type {
  Componente,
  Designacion,
  Etapa,
  FilaDatos,
  FilaPaa,
  Indicadores,
  Sistema
} from "./types";

function toNumberOrNull(valor: unknown): number | null {
  if (valor === null || valor === undefined || valor === "") return null;
  const numero = typeof valor === "number" ? valor : Number(valor);
  return Number.isFinite(numero) ? numero : null;
}

/** Equivalente a pd.to_numeric(...).fillna(0), usado antes de sumar. */
function sumNumeric(filas: FilaDatos[], columna: string): number {
  return filas.reduce((acumulado, fila) => {
    const numero = toNumberOrNull(fila[columna]);
    return acumulado + (numero ?? 0);
  }, 0);
}

/** Equivalente a Series.mean() de pandas: ignora nulos, no los trata como 0. */
function meanSkipNull(filas: FilaDatos[], columna: string): number | null {
  const validos = filas
    .map((fila) => toNumberOrNull(fila[columna]))
    .filter((valor): valor is number => valor !== null);

  if (validos.length === 0) return null;

  return validos.reduce((a, b) => a + b, 0) / validos.length;
}

function parseFecha(valor: unknown): Date | null {
  if (!valor) return null;
  const fecha = new Date(String(valor));
  return Number.isNaN(fecha.getTime()) ? null : fecha;
}

function formatearFecha(fecha: Date): string {
  const dia = String(fecha.getUTCDate()).padStart(2, "0");
  const mes = String(fecha.getUTCMonth() + 1).padStart(2, "0");
  const anio = fecha.getUTCFullYear();
  return `${dia}/${mes}/${anio}`;
}

/**
 * Separa "N3. Cuenta con..." en nivel (3) y descripción. Algunos
 * textos llegan con la "í" mal codificada (U+FFFD + U+00AD) y se
 * corrige aquí para no mostrar caracteres rotos.
 */
function parseNivel(valor: unknown): { nivel: number | null; texto: string | null } {
  if (!valor) return { nivel: null, texto: null };

  const limpio = String(valor).replace(/�­/g, "í").trim();
  const coincidencia = limpio.match(/^N\s*([0-4])\b[\s.:\-–]*/i);

  if (!coincidencia) return { nivel: null, texto: limpio || null };

  const texto = limpio.slice(coincidencia[0].length).trim();
  return {
    nivel: Number(coincidencia[1]),
    texto: texto ? texto.charAt(0).toUpperCase() + texto.slice(1) : null
  };
}

export function calcularIndicadores(
  datosPeriodo: FilaDatos[],
  entidad: string
): Indicadores {
  const nacional = entidad === NACIONAL;

  const base = nacional
    ? datosPeriodo.filter((fila) => fila.tiene_informacion === 1)
    : datosPeriodo.filter(
        (fila) => fila.nom_ent === entidad && fila.tiene_informacion === 1
      );

  const hayInformacion = base.length > 0;

  // ---------- Grado de consolidación ----------

  const gradoTotal = hayInformacion
    ? meanSkipNull(base, "grado_cons_total")
    : null;

  const componentes: Componente[] = COMPONENTES_GRADO.map(
    ([nombre, columna, maximo]) => {
      const media = hayInformacion ? meanSkipNull(base, columna) : null;
      return {
        nombre,
        puntos: media === null ? null : media * 100,
        maximo
      };
    }
  );

  // ---------- Nivel de consolidación (N0 a N4) ----------

  const niveles = base.map((fila) => parseNivel(fila.grado_cons_text));

  const distribucionNiveles = NIVELES_CONSOLIDACION.map(
    (_, posicion) => niveles.filter((item) => item.nivel === posicion).length
  );

  const nivelConsolidacion = !nacional && niveles.length ? niveles[0].nivel : null;
  const textoConsolidacion = !nacional && niveles.length ? niveles[0].texto : null;

  // ---------- Designaciones ----------

  // En la vista nacional se incluye a la Ciudad de México aunque no tenga
  // información para el resto del tablero; solo se excluye Oaxaca.
  const baseDesignaciones = nacional
    ? datosPeriodo.filter((fila) => fila.nom_ent !== "Oaxaca")
    : base;

  const designaciones: Designacion[] = DESIGNACIONES.map((config, posicion) => {
    let vigentes: number;
    let total: number;

    if (nacional && config.clave === "tit") {
      vigentes = sumNumeric(baseDesignaciones, "des_vig_tit");
      total = 31;
    } else if (!hayInformacion) {
      vigentes = 0;
      total = 0;
    } else {
      vigentes = sumNumeric(baseDesignaciones, `des_vig_${config.clave}`);
      const pendientes = sumNumeric(baseDesignaciones, `des_pend_${config.clave}`);
      total = vigentes + pendientes;
    }

    return {
      ...config,
      color: COLORES_TARJETAS[posicion],
      vigentes,
      total
    };
  });

  const designacionesVigentes = designaciones.reduce(
    (acumulado, item) => acumulado + item.vigentes,
    0
  );

  const designacionesTotal = designaciones.reduce(
    (acumulado, item) => acumulado + item.total,
    0
  );

  // ---------- Entes interconectados a la PDN ----------

  const sistemas: Sistema[] = SISTEMAS_PDN.map((config) => {
    let entes = 0;
    let total = 0;
    let porcentaje = 0;

    if (hayInformacion) {
      entes = sumNumeric(base, `${config.clave}_entes`);
      total = sumNumeric(base, `${config.clave}_total`);

      if (nacional) {
        porcentaje = total ? (entes / total) * 100 : 0;
      } else {
        porcentaje = (toNumberOrNull(base[0][`cumplimiento_${config.clave}`]) ?? 0) * 100;
      }
    }

    return { ...config, entes, total, porcentaje };
  });

  const pdnEntes = sistemas.reduce((acumulado, item) => acumulado + item.entes, 0);
  const pdnTotal = sistemas.reduce((acumulado, item) => acumulado + item.total, 0);
  const pdnPorcentaje = pdnTotal ? (pdnEntes / pdnTotal) * 100 : 0;

  // ---------- Avances de la implementación ----------

  const etapas: Etapa[] = ETAPAS.map((config) => {
    if (!hayInformacion) {
      return {
        ...config,
        valor: "Sin información",
        activa: false,
        link: null,
        texto: null
      };
    }

    if (nacional) {
      const conteo = base.filter(
        (fila) => parseFecha(fila[config.columna]) !== null
      ).length;

      return {
        ...config,
        valor: `${conteo} de ${base.length}`,
        activa: conteo > 0,
        link: null,
        texto: null
      };
    }

    const fila = base[0];
    const fecha = parseFecha(fila[config.columna]);
    const activa = fecha !== null;

    let link: string | null = null;
    if (config.columna_link) {
      const valorLink = fila[config.columna_link];
      if (valorLink) {
        const texto = String(valorLink).trim();
        if (texto.startsWith("http://") || texto.startsWith("https://")) {
          link = texto;
        }
      }
    }

    let texto: string | null = null;
    if (config.columna_texto) {
      const valorTexto = fila[config.columna_texto];
      if (valorTexto) {
        const limpio = String(valorTexto).trim();
        if (limpio) texto = limpio;
      }
    }

    return {
      ...config,
      valor: activa && fecha ? formatearFecha(fecha) : "Sin fecha",
      activa,
      link,
      texto
    };
  });

  // ---------- Profesionalización ----------

  let capacitadas: number | null = null;
  let paa: FilaPaa[] = [];

  if (hayInformacion) {
    capacitadas = sumNumeric(base, "cap_serv_pub");

    const filasPaa: FilaPaa[] = [];

    for (const [columna, [corta, larga]] of Object.entries(ETIQUETAS_PAA)) {
      const valor = sumNumeric(base, columna);
      if (valor > 0) {
        filasPaa.push({
          institucion: corta,
          institucion_completa: larga,
          personas: valor
        });
      }
    }

    if (filasPaa.length > 7) {
      const ordenadas = [...filasPaa].sort((a, b) => b.personas - a.personas);
      const principales = ordenadas.slice(0, 6);
      const restantes = ordenadas.slice(6);

      paa = [
        ...principales,
        {
          institucion: `Otras ${restantes.length} instituciones`,
          institucion_completa: restantes
            .map((item) => item.institucion_completa)
            .join(" · "),
          personas: restantes.reduce((a, b) => a + b.personas, 0)
        }
      ];
    } else {
      paa = filasPaa;
    }
  }

  return {
    nacional,
    hayInformacion,
    entidades: base.length,
    gradoTotal,
    componentes,
    designaciones,
    designacionesVigentes,
    designacionesTotal,
    sistemas,
    pdnEntes,
    pdnTotal,
    pdnPorcentaje,
    etapas,
    capacitadas,
    paa,
    nivelConsolidacion,
    textoConsolidacion,
    distribucionNiveles
  };
}
