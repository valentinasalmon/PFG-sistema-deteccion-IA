/**
 * Cómo termina el pago del plan, según la organización (funcionalidad 032,
 * frame 10d):
 *
 * - un estudio jurídico o una aseguradora quedan esperando la aprobación del
 *   Administrador (038: también los estudios);
 * - un cambio de plan ya rige.
 *
 * Realiza: RF10, RF20; RN38.
 */
import Icono from './Icono.jsx'

export default function ResultadoPago({ cobro, children }) {
  const esAseguradora = cobro.organizacion.tipo === 'aseguradora'
  const esCambio = cobro.motivo === 'cambio_plan'
  let titulo = 'Pago recibido: falta la aprobación'
  let texto =
    `Se acreditó el pago del plan ${cobro.plan.nombre}. Un Administrador revisa el estudio y te avisamos por ` +
    'correo cuando esté activo; desde ese momento podés invitar a tu equipo. Si no se aprueba, el pago se ' +
    'devuelve y te avisamos el motivo.'
  if (esCambio) {
    titulo = 'Listo: el plan nuevo ya rige'
    texto = `Se acreditó el pago y ${cobro.organizacion.nombre} pasó al plan ${cobro.plan.nombre}.`
  } else if (esAseguradora) {
    titulo = 'Pago recibido: falta la aprobación'
    texto =
      'Un Administrador revisa que la aseguradora figure en el catálogo de la SSN y que seas quien la ' +
      'representa. Te avisamos por correo. Si no se aprueba, el pago se devuelve y te avisamos el motivo.'
  }
  const pendienteDeAprobacion = !esCambio
  return (
    <section className="resultado-pago" aria-labelledby="titulo-resultado-pago" role="status">
      <span
        className={`resultado-pago__icono${pendienteDeAprobacion ? ' resultado-pago__icono--espera' : ''}`}
        aria-hidden="true"
      >
        <Icono nombre={pendienteDeAprobacion ? 'reloj' : 'verificado'} tamanio={30} />
      </span>
      <h2 id="titulo-resultado-pago">{titulo}</h2>
      <p>{texto}</p>
      <ul className="resultado-pago__etiquetas">
        <li className="estado-caso estado-caso--analizado">Pago acreditado</li>
        {pendienteDeAprobacion && <li className="estado-caso estado-caso--en_analisis">Aprobación pendiente</li>}
      </ul>
      {pendienteDeAprobacion && (
        <ol className="resultado-pago__orden" aria-label="Pasos para la organización">
          <li className="resultado-pago__paso--hecho">Registro</li>
          <li className="resultado-pago__paso--hecho">Pago</li>
          <li className="resultado-pago__paso--actual">Aprobación del Administrador</li>
          <li>Cuenta activa</li>
        </ol>
      )}
      {children}
    </section>
  )
}
