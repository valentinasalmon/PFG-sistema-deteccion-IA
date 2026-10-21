/**
 * Plan del espacio de trabajo: límites, consumo del mes y cambio de plan con
 * pago simulado (funcionalidad 014).
 *
 * El pago se presenta siempre como simulado: no pide datos de tarjeta ni
 * cobra nada; al confirmar, el plan se aplica de inmediato (RF20 CA2, CP-01).
 * Si el plan no se puede cargar, la sección no se muestra para no estorbar el
 * resto de la pantalla.
 *
 * Realiza: RF20 (CA1, CA2), RF19 (consumo visible).
 */
import { useCallback, useState } from 'react'
import { cambiarPlan, obtenerPlan } from '../api/organizaciones.js'
import { obtenerPlanPersonal } from '../api/perfil.js'
import { useDatos } from '../hooks/useDatos.js'
import { formatearDia } from '../utilidades/fechas.js'
import Aviso from './Aviso.jsx'

function Consumo({ etiqueta, usado, limite }) {
  const porcentaje = Math.min(100, Math.round((usado / limite) * 100))
  return (
    <div className="consumo">
      <div className="consumo__texto">
        <span>{etiqueta}</span>
        <strong>
          {usado} de {limite}
        </strong>
      </div>
      <div
        className={`consumo__barra ${porcentaje >= 90 ? 'consumo__barra--alto' : ''}`}
        role="meter"
        aria-label={etiqueta}
        aria-valuemin={0}
        aria-valuemax={limite}
        aria-valuenow={usado}
      >
        <span style={{ width: `${porcentaje}%` }} />
      </div>
    </div>
  )
}

function CambioDePlan({ idOrganizacion, plan, alTerminar }) {
  const [elegido, setElegido] = useState(null)
  const [confirmando, setConfirmando] = useState(false)
  const [error, setError] = useState(null)
  const otros = plan.disponibles.filter((p) => p.codigo !== plan.codigo)

  async function confirmar() {
    setError(null)
    setConfirmando(true)
    try {
      const respuesta = await cambiarPlan(idOrganizacion, elegido.codigo)
      await alTerminar(respuesta.mensaje)
    } catch (errorApi) {
      setError(errorApi.message)
      setConfirmando(false)
    }
  }

  return (
    <div className="cambio-plan">
      <fieldset className="opciones-tarjeta opciones-tarjeta--dos">
        <legend className="campo__etiqueta">Elegí el plan nuevo</legend>
        {otros.map((opcion) => (
          <label
            key={opcion.codigo}
            className={`opcion-tarjeta ${elegido?.codigo === opcion.codigo ? 'opcion-tarjeta--elegida' : ''}`}
          >
            <input
              type="radio"
              name="plan"
              className="opcion-tarjeta__control"
              checked={elegido?.codigo === opcion.codigo}
              onChange={() => setElegido(opcion)}
            />
            <span className="opcion-tarjeta__titulo">{opcion.nombre}</span>
            <span className="opcion-tarjeta__descripcion">
              Hasta {opcion.miembros} miembros · {opcion.analisis_mes} análisis por mes ·{' '}
              {opcion.imagenes_por_caso} imágenes por caso
            </span>
          </label>
        ))}
      </fieldset>
      {elegido && (
        <div className="pago-simulado" role="region" aria-label="Pago simulado">
          <p>
            <strong>Pago simulado.</strong> Este es un proyecto académico: no se piden datos de
            tarjeta y no se cobra nada. Al confirmar, {elegido.nombre} se aplica de inmediato.
          </p>
          <dl className="datos-fijos">
            <dt>Plan nuevo</dt>
            <dd>{elegido.nombre}</dd>
            <dt>Precio</dt>
            <dd>{elegido.precio}</dd>
          </dl>
          {error && <Aviso tipo="error">{error}</Aviso>}
          <div className="acciones-en-linea">
            <button type="button" className="boton boton--fantasma" onClick={() => alTerminar(null)}>
              Cancelar
            </button>
            <button type="button" className="boton" disabled={confirmando} onClick={confirmar}>
              {confirmando ? 'Aplicando…' : 'Confirmar el cambio de plan'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * @param {{idOrganizacion?: number}} props - sin organización, muestra el plan personal.
 */
export default function SeccionPlan({ idOrganizacion }) {
  const cargar = useCallback(
    () => (idOrganizacion ? obtenerPlan(idOrganizacion) : obtenerPlanPersonal()),
    [idOrganizacion],
  )
  const { datos: plan, error, recargar } = useDatos(cargar)
  const [cambiando, setCambiando] = useState(false)
  const [mensaje, setMensaje] = useState(null)

  if (error || !plan) return null

  async function terminar(texto) {
    setCambiando(false)
    if (texto) {
      setMensaje(texto)
      await recargar()
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-plan">
      <div className="seccion__cabecera">
        <h2 id="titulo-plan">Plan {plan.nombre}</h2>
        {plan.puede_cambiar && !cambiando && (
          <button type="button" className="boton boton--secundario" onClick={() => setCambiando(true)}>
            Cambiar de plan
          </button>
        )}
      </div>
      {mensaje && <Aviso tipo="exito">{mensaje}</Aviso>}
      <div className="consumos">
        {plan.consumo.miembros !== undefined && (
          <Consumo etiqueta="Miembros" usado={plan.consumo.miembros} limite={plan.limites.miembros} />
        )}
        <Consumo
          etiqueta="Análisis de este mes"
          usado={plan.consumo.analisis_mes}
          limite={plan.limites.analisis_mes}
        />
      </div>
      <p className="nota">
        Hasta {plan.limites.imagenes_por_caso} imágenes por caso. Los análisis se renuevan el{' '}
        {formatearDia(plan.renovacion)}.
      </p>
      {cambiando && <CambioDePlan idOrganizacion={idOrganizacion} plan={plan} alTerminar={terminar} />}
    </section>
  )
}
