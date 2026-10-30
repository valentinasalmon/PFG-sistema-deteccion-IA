/**
 * Pago del plan por transferencia, como cobra Cresium (funcionalidad 032,
 * frames 10c y 10g).
 *
 * Muestra el CVU, el alias y la referencia con botones para copiarlos, el
 * resumen del plan y el estado del cobro, que se consulta cada pocos segundos:
 * cuando el pago se acredita, avisa con ``alAcreditar``. Mientras no esté la
 * API de Cresium, «Simular la transferencia» hace de aviso de acreditación.
 *
 * Lo usan el último paso del registro, la página ``/pago/<token>``, la
 * creación de un estudio desde Mi perfil y el cambio de plan.
 *
 * Realiza: RF20 (CA2); CP-34; RNF10.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { consultarCobro, simularPago } from '../api/pagos.js'
import { useDatos } from '../hooks/useDatos.js'
import { textoDelPrecio } from '../utilidades/planes.js'
import Aviso from './Aviso.jsx'
import Cargando from './Cargando.jsx'

const INTERVALO_DE_CONSULTA = 4000 // milisegundos

function DatoCopiable({ etiqueta, valor }) {
  const [copiado, setCopiado] = useState(false)

  async function copiar() {
    try {
      await navigator.clipboard.writeText(valor)
      setCopiado(true)
    } catch {
      setCopiado(false)
    }
  }

  return (
    <div className="pago__dato">
      <dt>{etiqueta}</dt>
      <dd className="pago__valor">{valor}</dd>
      <dd>
        <button
          type="button"
          className="boton-enlace pago__copiar"
          onClick={copiar}
          aria-label={`Copiar ${etiqueta.toLowerCase()}`}
        >
          {copiado ? 'Copiado' : 'Copiar'}
        </button>
      </dd>
    </div>
  )
}

export default function PanelPago({ token, alAcreditar }) {
  const cargar = useCallback(() => consultarCobro(token), [token])
  const { datos: cobro, error, recargar } = useDatos(cargar)
  const [simulando, setSimulando] = useState(false)
  const [errorSimulacion, setErrorSimulacion] = useState(null)
  const avisado = useRef(false)
  const pendiente = cobro?.estado === 'pendiente'

  // Mientras esté pendiente, se consulta el estado: el pago real llega solo.
  useEffect(() => {
    if (!pendiente) return undefined
    const temporizador = setInterval(() => recargar(), INTERVALO_DE_CONSULTA)
    return () => clearInterval(temporizador)
  }, [pendiente, recargar])

  useEffect(() => {
    if (cobro && cobro.estado !== 'pendiente' && !avisado.current) {
      avisado.current = true
      alAcreditar?.(cobro)
    }
  }, [cobro, alAcreditar])

  async function simular() {
    setErrorSimulacion(null)
    setSimulando(true)
    try {
      await simularPago(token)
      await recargar()
    } catch (errorApi) {
      setErrorSimulacion(errorApi.message)
    } finally {
      setSimulando(false)
    }
  }

  if (error) return <Aviso tipo="error">{error.message}</Aviso>
  if (!cobro) return <Cargando texto="Preparando el pago…" />

  return (
    <section className="pago" aria-labelledby="titulo-pago">
      <div className="pago__cabecera">
        <h2 id="titulo-pago">Pagá el plan por transferencia</h2>
        <span className="pago__proveedor">
          <span aria-hidden="true">C</span>
          Cobro con {cobro.proveedor}
        </span>
      </div>
      <p className="nota">
        Transferí desde la cuenta de {cobro.organizacion.nombre} a estos datos. El pago se acredita solo,
        sin mandar comprobantes.
      </p>
      <div className="pago__cuerpo">
        <div className="pago__principal">
          <dl className="pago__datos">
            <DatoCopiable etiqueta="CVU" valor={cobro.cvu} />
            <DatoCopiable etiqueta="Alias" valor={cobro.alias} />
            <div className="pago__dato">
              <dt>Titular</dt>
              <dd className="pago__valor pago__valor--texto">{cobro.titular}</dd>
            </div>
            <DatoCopiable etiqueta="Referencia" valor={cobro.referencia} />
          </dl>
          <div className={`pago__estado${pendiente ? '' : ' pago__estado--ok'}`} role="status">
            {pendiente ? (
              <>
                <span className="pago__girando" aria-hidden="true" />
                <div>
                  <strong>Esperando la transferencia…</strong>
                  <span className="nota">
                    Esta pantalla se actualiza sola cuando se acredita. Podés cerrarla: lo podés retomar
                    desde la organización.
                  </span>
                </div>
              </>
            ) : (
              <strong>Pago acreditado</strong>
            )}
          </div>
          {pendiente && cobro.permite_simular && (
            <Aviso tipo="alerta" flotante={false}>
              <strong>Simulación.</strong> Todavía no hay cobro real: tocá «Simular la transferencia» para
              seguir.
            </Aviso>
          )}
          {errorSimulacion && <Aviso tipo="error">{errorSimulacion}</Aviso>}
        </div>
        <aside className="pago__resumen" aria-label="Resumen del pago">
          <strong>Resumen</strong>
          <dl>
            <div>
              <dt>Plan</dt>
              <dd>{cobro.plan.nombre}</dd>
            </div>
            <div>
              <dt>Período</dt>
              <dd>1 mes</dd>
            </div>
            <div>
              <dt>Organización</dt>
              <dd>{cobro.organizacion.nombre}</dd>
            </div>
            <div className="pago__total">
              <dt>Total</dt>
              <dd>{textoDelPrecio(cobro.plan.precio)}</dd>
            </div>
          </dl>
        </aside>
      </div>
      {pendiente && cobro.permite_simular && (
        <div className="pago__acciones">
          <button type="button" className="boton boton--lima" onClick={simular} disabled={simulando}>
            {simulando ? 'Acreditando…' : 'Simular la transferencia'}
          </button>
        </div>
      )}
    </section>
  )
}
