"use client";

import { useEffect, useMemo, useState } from "react";
import { NACIONAL, VINO } from "@/lib/constants";
import { claveIcono } from "@/lib/iconKeys";
import { calcularIndicadores } from "@/lib/indicadores";
import type { FichasEspeciales, FilaDatos } from "@/lib/types";
import Toolbar from "./Toolbar";
import FichaEspecial from "./FichaEspecial";
import MapaConsolidacion from "./MapaConsolidacion";
import AvancesImplementacion from "./AvancesImplementacion";
import Designaciones from "./Designaciones";
import PdnInterconectados from "./PdnInterconectados";
import Profesionalizacion from "./Profesionalizacion";
import NivelConsolidacion from "./NivelConsolidacion";

function aniosDisponibles(datos: FilaDatos[]): number[] {
  return Array.from(new Set(datos.map((fila) => fila.anio))).sort(
    (a, b) => b - a
  );
}

function trimestresDisponibles(datos: FilaDatos[], anio: number): number[] {
  return Array.from(
    new Set(
      datos.filter((fila) => fila.anio === anio).map((fila) => fila.trimestre)
    )
  ).sort((a, b) => a - b);
}

function entidadesDisponibles(datosPeriodo: FilaDatos[]): string[] {
  return [NACIONAL, ...datosPeriodo.map((fila) => fila.nom_ent).sort()];
}

export default function Dashboard({
  datosIniciales,
  geojson,
  fichasEspeciales,
  iconos
}: {
  datosIniciales: FilaDatos[];
  geojson: GeoJSON.FeatureCollection;
  fichasEspeciales: FichasEspeciales;
  iconos: Record<string, string>;
}) {
  const datos = datosIniciales;

  const anios = useMemo(() => aniosDisponibles(datos), [datos]);
  const [anio, setAnio] = useState<number>(() => anios[0]);

  const trimestres = useMemo(
    () => trimestresDisponibles(datos, anio),
    [datos, anio]
  );
  const [trimestre, setTrimestre] = useState<number>(() => trimestres[0]);

  const [entidadActiva, setEntidadActiva] = useState<string>(NACIONAL);

  // Si el año cambia y el trimestre elegido ya no existe en ese año,
  // se elige el primero disponible (mismo comportamiento que los
  // selectbox de Streamlit al perder su valor previo).
  useEffect(() => {
    if (!trimestres.includes(trimestre)) {
      setTrimestre(trimestres[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trimestres]);

  const datosPeriodo = useMemo(
    () =>
      datos.filter((fila) => fila.anio === anio && fila.trimestre === trimestre),
    [datos, anio, trimestre]
  );

  const entidades = useMemo(
    () => entidadesDisponibles(datosPeriodo),
    [datosPeriodo]
  );

  // La entidad activa se sincroniza con ?entidad= de la URL al montar.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const entidadUrl = params.get("entidad");

    if (entidadUrl && entidades.includes(entidadUrl)) {
      setEntidadActiva(entidadUrl);
    }
    // Solo se ejecuta una vez, al montar.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Si cambia el periodo y la entidad activa deja de existir, se
  // regresa a la vista nacional.
  useEffect(() => {
    if (!entidades.includes(entidadActiva)) {
      setEntidadActiva(NACIONAL);
    }
  }, [entidades, entidadActiva]);

  // La entidad se refleja en la URL para poder compartir la vista.
  useEffect(() => {
    const url = new URL(window.location.href);

    if (entidadActiva === NACIONAL) {
      url.searchParams.delete("entidad");
    } else {
      url.searchParams.set("entidad", entidadActiva);
    }

    window.history.replaceState({}, "", url);
  }, [entidadActiva]);

  const esNacional = entidadActiva === NACIONAL;
  const esFichaEspecial = entidadActiva in fichasEspeciales;

  const indicadores = useMemo(
    () => calcularIndicadores(datosPeriodo, entidadActiva),
    [datosPeriodo, entidadActiva]
  );

  return (
    <div className="app-shell">
      <Toolbar
        anios={anios}
        anio={anio}
        onAnioChange={setAnio}
        trimestres={trimestres}
        trimestre={trimestre}
        onTrimestreChange={setTrimestre}
        entidades={entidades}
        entidadActiva={entidadActiva}
        onEntidadChange={setEntidadActiva}
        iconoDescargaUri={iconos[claveIcono("database_down", VINO)]}
      />

      {esFichaEspecial ? (
        <FichaEspecial
          ficha={fichasEspeciales[entidadActiva]}
          entidad={entidadActiva}
          onVolver={() => setEntidadActiva(NACIONAL)}
        />
      ) : (
        <div className="contenido-principal">
          <div className="columna">
            <MapaConsolidacion
              entidadSeleccionada={entidadActiva}
              esNacional={esNacional}
              gradoTotal={indicadores.gradoTotal}
              componentes={indicadores.componentes}
              entidadesConInformacion={indicadores.entidades}
              hayInformacion={indicadores.hayInformacion}
              anio={anio}
              trimestre={trimestre}
              datosPeriodo={datosPeriodo}
              geojson={geojson}
              onVolverNacional={() => setEntidadActiva(NACIONAL)}
              onEntidadClick={setEntidadActiva}
            />

            <AvancesImplementacion
              etapas={indicadores.etapas}
              esNacional={esNacional}
              iconos={iconos}
            />
          </div>

          <div className="columna">
            <Designaciones
              designaciones={indicadores.designaciones}
              designacionesVigentes={indicadores.designacionesVigentes}
              designacionesTotal={indicadores.designacionesTotal}
              hayInformacion={indicadores.hayInformacion}
              esNacional={esNacional}
              iconos={iconos}
            />

            <div className="fila-pdn-profesionalizacion">
              <PdnInterconectados
                sistemas={indicadores.sistemas}
                pdnEntes={indicadores.pdnEntes}
                pdnTotal={indicadores.pdnTotal}
                pdnPorcentaje={indicadores.pdnPorcentaje}
                hayInformacion={indicadores.hayInformacion}
                iconos={iconos}
              />

              <Profesionalizacion
                capacitadas={indicadores.capacitadas}
                paa={indicadores.paa}
                iconos={iconos}
              />
            </div>

            <NivelConsolidacion
              nivel={indicadores.nivelConsolidacion}
              texto={indicadores.textoConsolidacion}
              distribucion={indicadores.distribucionNiveles}
              hayInformacion={indicadores.hayInformacion}
              esNacional={esNacional}
            />
          </div>
        </div>
      )}
    </div>
  );
}
