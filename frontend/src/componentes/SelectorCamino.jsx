/**
 * Primer paso del registro: cómo se va a usar la plataforma (funcionalidad
 * 032, frame 10a).
 *
 * Tres caminos: abogado independiente (plan personal, sin pago), abogado con
 * estudio jurídico (con el nombre del estudio, plan y pago) o aseguradora
 * (plan, pago y aprobación). El perfil (Abogado o Aseguradora) no cambia
 * después (RN01). Lo usan el registro común y el registro con Google.
 *
 * Realiza: RF01, RF10, RF52 (CA1); RN01; CA1 y CA2 de la funcionalidad 032.
 */
import CampoTexto from './CampoTexto.jsx'
import Icono from './Icono.jsx'

const CAMINOS = [
  {
    valor: 'independiente',
    icono: 'perfil',
    titulo: 'Abogado o abogada independiente',
    descripcion:
      'Trabajás solo. Plan personal gratuito. Más adelante podés crear tu estudio desde Mi perfil.',
  },
  {
    valor: 'estudio',
    icono: 'organizaciones',
    titulo: 'Abogado con estudio jurídico',
    descripcion: 'Registrás tu estudio, elegís un plan y sumás a tu equipo.',
  },
  {
    valor: 'aseguradora',
    icono: 'verificado',
    titulo: 'Aseguradora',
    descripcion:
      'Para quien administra la cuenta de la empresa. La aprueba un Administrador; tu equipo se suma por invitación.',
  },
]

export default function SelectorCamino({ valores, errores, cambiar, sinEstudio = false }) {
  const caminos = sinEstudio ? CAMINOS.filter((c) => c.valor !== 'estudio') : CAMINOS
  return (
    <>
      <fieldset
        className="selector-camino"
        aria-labelledby="titulo-paso"
        aria-describedby={errores.camino ? 'ayuda-camino error-camino' : 'ayuda-camino'}
      >
        {caminos.map((camino) => {
          const elegido = valores.camino === camino.valor
          return (
            <label key={camino.valor} className={`camino${elegido ? ' camino--elegido' : ''}`}>
              <input
                type="radio"
                name="camino"
                value={camino.valor}
                checked={elegido}
                onChange={cambiar}
                className="camino__control"
              />
              <span className="camino__icono" aria-hidden="true">
                <Icono nombre={camino.icono} tamanio={24} />
              </span>
              <span className="camino__titulo">{camino.titulo}</span>
              <span className="camino__descripcion">{camino.descripcion}</span>
            </label>
          )
        })}
      </fieldset>
      {valores.camino === 'estudio' && (
        <CampoTexto
          etiqueta="Nombre del estudio jurídico"
          nombre="nombre_estudio"
          autoComplete="organization"
          maxLength={150}
          value={valores.nombre_estudio}
          onChange={cambiar}
          error={errores.nombre_estudio}
          ayuda="Vas a ser su Referente. Después invitás a tu equipo."
          required
        />
      )}
      <p id="ayuda-camino" className="campo__ayuda">
        El estudio y la aseguradora pagan su plan al final del registro. El perfil personal no paga y no
        puede cambiarse después.
      </p>
      {errores.camino && (
        <p id="error-camino" className="campo__error">
          {errores.camino}
        </p>
      )}
    </>
  )
}
