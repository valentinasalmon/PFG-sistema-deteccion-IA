/**
 * Plan del espacio de trabajo: límites, consumo del mes y cambio de plan
 * (funcionalidad 014).
 *
 * Desde la funcionalidad 032 el cambio de plan se paga por transferencia: se
 * elige el plan nuevo, se pasa a la página de pago y el plan rige al
 * acreditarse. Si el pago del alta está pendiente, se ofrece retomarlo. Con
 * los lugares del plan ocupados, se sugiere pasar a Profesional.
 * Si el plan no se puede cargar, la sección no se muestra para no estorbar el
 * resto de la pantalla.
 *
 * Realiza: RF20 (CA1, CA2), RF19 (consumo visible); CA8 y CA9 de la 032.
 */
import { useCallback, useState } from "react";
import { useNavigate } from "react-router";
import {
  cambiarPlan,
  obtenerPlan,
  retomarPago,
} from "../api/organizaciones.js";
import { obtenerPlanPersonal } from "../api/perfil.js";
import { useDatos } from "../hooks/useDatos.js";
import { formatearDia } from "../utilidades/fechas.js";
import Aviso from "./Aviso.jsx";
import SelectorPlan from "./SelectorPlan.jsx";

function Consumo({ etiqueta, usado, limite }) {
  const porcentaje = Math.min(100, Math.round((usado / limite) * 100));
  return (
    <div className="consumo">
      <div className="consumo__texto">
        <span>{etiqueta}</span>
        <strong>
          {usado} de {limite}
        </strong>
      </div>
      <div
        className={`consumo__barra ${porcentaje >= 90 ? "consumo__barra--alto" : ""}`}
        role="meter"
        aria-label={etiqueta}
        aria-valuemin={0}
        aria-valuemax={limite}
        aria-valuenow={usado}
      >
        <span style={{ width: `${porcentaje}%` }} />
      </div>
    </div>
  );
}

function CambioDePlan({ idOrganizacion, plan, alCancelar }) {
  const navegar = useNavigate();
  const otros = plan.disponibles.filter((p) => p.codigo !== plan.codigo);
  const [elegido, setElegido] = useState(otros[0]?.codigo);
  const [confirmando, setConfirmando] = useState(false);
  const [error, setError] = useState(null);

  async function confirmar() {
    setError(null);
    setConfirmando(true);
    try {
      const respuesta = await cambiarPlan(idOrganizacion, elegido);
      navegar(`/pago/${respuesta.pago.token}`);
    } catch (errorApi) {
      setError(errorApi.message);
      setConfirmando(false);
    }
  }

  return (
    <div className="cambio-plan">
      <h3 id="titulo-paso">Elegí el plan nuevo</h3>
      <SelectorPlan
        planes={otros}
        valor={elegido}
        onChange={(evento) => setElegido(evento.target.value)}
        nombre="plan-nuevo"
      />
      <p className="nota">
        El plan nuevo rige cuando se acredita la transferencia. Hasta entonces
        sigue el plan {plan.nombre}.
      </p>
      {error && <Aviso tipo="error">{error}</Aviso>}
      <div className="acciones-en-linea">
        <button
          type="button"
          className="boton boton--fantasma"
          onClick={alCancelar}
        >
          Cancelar
        </button>
        <button
          type="button"
          className="boton"
          disabled={confirmando || !elegido}
          onClick={confirmar}
        >
          {confirmando ? "Preparando el pago…" : "Ir al pago"}
        </button>
      </div>
    </div>
  );
}

function PagoPendiente({ idOrganizacion, puedeRetomar }) {
  const navegar = useNavigate();
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);

  async function retomar() {
    setError(null);
    setEnviando(true);
    try {
      const respuesta = await retomarPago(idOrganizacion);
      navegar(`/pago/${respuesta.pago.token}`);
    } catch (errorApi) {
      setError(errorApi.message);
      setEnviando(false);
    }
  }

  return (
    <Aviso tipo="alerta" flotante={false}>
      <strong>Falta el pago del plan.</strong> Hasta que se acredite no se
      pueden invitar miembros ni cargar casos de la organización.
      {puedeRetomar && (
        <div className="acciones-en-linea">
          <button
            type="button"
            className="boton boton--lima"
            onClick={retomar}
            disabled={enviando}
          >
            {enviando ? "Preparando…" : "Retomar el pago"}
          </button>
        </div>
      )}
      {error && <span className="campo__error">{error}</span>}
    </Aviso>
  );
}

/**
 * @param {{idOrganizacion?: number}} props - sin organización, muestra el plan personal.
 */
export default function SeccionPlan({ idOrganizacion }) {
  const cargar = useCallback(
    () =>
      idOrganizacion ? obtenerPlan(idOrganizacion) : obtenerPlanPersonal(),
    [idOrganizacion],
  );
  const { datos: plan, error } = useDatos(cargar);
  const [cambiando, setCambiando] = useState(false);

  if (error || !plan) return null;
  const pagoPendiente = plan.estado_organizacion === "pago_pendiente";
  const puedeCambiar =
    plan.puede_cambiar && plan.estado_organizacion === "activa";
  const lleno =
    plan.consumo.miembros !== undefined &&
    plan.consumo.miembros >= plan.limites.miembros;
  const hayMayor = plan.disponibles?.some(
    (p) => p.miembros > plan.limites.miembros,
  );

  return (
    <section className="seccion" aria-labelledby="titulo-plan">
      <div className="seccion__cabecera">
        <h2 id="titulo-plan">Plan {plan.nombre}</h2>
        {puedeCambiar && !cambiando && (
          <button
            type="button"
            className="boton boton--secundario"
            onClick={() => setCambiando(true)}
          >
            Cambiar de plan
          </button>
        )}
      </div>
      {pagoPendiente && (
        <PagoPendiente
          idOrganizacion={idOrganizacion}
          puedeRetomar={plan.puede_cambiar}
        />
      )}
      {lleno && hayMayor && puedeCambiar && !cambiando && (
        <Aviso tipo="info" flotante={false}>
          Ocupaste todos los lugares del plan. Para sumar más miembros,{" "}
          <button
            type="button"
            className="boton-enlace"
            onClick={() => setCambiando(true)}
          >
            pasá a un plan con más lugares
          </button>
          .
        </Aviso>
      )}
      <div className="consumos">
        {plan.consumo.miembros !== undefined && (
          <Consumo
            etiqueta="Miembros"
            usado={plan.consumo.miembros}
            limite={plan.limites.miembros}
          />
        )}
        <Consumo
          etiqueta="Análisis de este mes"
          usado={plan.consumo.analisis_mes}
          limite={plan.limites.analisis_mes}
        />
      </div>
      <p className="nota">
        Hasta {plan.limites.imagenes_por_caso} imágenes por caso. Los análisis
        se renuevan el {formatearDia(plan.renovacion)}.
      </p>
      {cambiando && (
        <CambioDePlan
          idOrganizacion={idOrganizacion}
          plan={plan}
          alCancelar={() => setCambiando(false)}
        />
      )}
    </section>
  );
}
