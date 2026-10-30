/**
 * Página pública "Estado del sistema" (/estado).
 *
 * Consulta el estado de la API al cargar y muestra, en español, si cada
 * componente del sistema responde. Fue la página inicial del esqueleto
 * caminante; desde la funcionalidad 002 el inicio es la pantalla con sesión.
 *
 * También muestra si el sello en Hedera está activo, en qué red y cuándo se
 * confirmó el último, para comprobar en producción que funciona (023, 029).
 *
 * Realiza: CA4 y CA5 de la funcionalidad 001; RF37.
 */
import { useEffect, useState } from 'react'
import { obtenerSalud } from '../api/salud.js'

/** Nombres legibles de cada componente informado por la API. */
const NOMBRES_COMPONENTES = {
  api: 'API',
  base_de_datos: 'Base de datos',
  redis: 'Cola de tareas (Redis)',
}

/** Texto de cada estado del sello que informa la API. */
const ESTADOS_SELLO = {
  ok: 'Funciona',
  con_demoras: 'Con demoras: hay sellos esperando confirmación',
  con_fallas: 'Con fallas: hay sellos que no se pudieron registrar',
  error: 'No se pudo consultar',
  desactivado: 'Desactivado',
}

/** Nombre del modo del sello: Hedera con su red, simulado o nada si está apagado. */
function nombreDelModo(sello) {
  if (sello.modo === 'hedera') return `Hedera (${sello.red})`
  if (sello.modo === 'simulado') return 'Simulado'
  return null
}

/** Fila con el estado del sello de tiempo (Hedera o simulado). */
function EstadoSello({ sello }) {
  if (!sello) return null
  const modo = nombreDelModo(sello)
  return (
    <li>
      <span>Sello de tiempo{modo ? ` · ${modo}` : ''}</span>
      <strong>
        {ESTADOS_SELLO[sello.estado] ?? sello.estado}
        {sello.ultimo && (
          <small className="nota">
            {' '}
            · último confirmado el {new Date(`${sello.ultimo}Z`).toLocaleString('es-AR')}
          </small>
        )}
      </strong>
    </li>
  )
}

export default function PaginaEstado() {
  const [salud, setSalud] = useState(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    obtenerSalud()
      .then(setSalud)
      .catch(() => setError(true))
  }, [])

  return (
    <>
      <h1>Estado del sistema</h1>

      {error && (
        <p className="aviso aviso--error" role="alert">
          No se pudo conectar con la API.
        </p>
      )}

      {!error && !salud && <p>Verificando la conexión con la API…</p>}

      {salud && (
        <section aria-label="Estado del sistema">
          <p className={salud.estado === 'ok' ? 'aviso aviso--ok' : 'aviso aviso--error'}>
            {salud.estado === 'ok'
              ? 'API conectada: todos los servicios funcionan.'
              : 'API conectada, pero hay servicios que no responden.'}
          </p>
          <ul className="lista-componentes">
            {Object.entries(salud.componentes).map(([nombre, estado]) => (
              <li key={nombre}>
                <span>{NOMBRES_COMPONENTES[nombre] ?? nombre}</span>
                <strong>{estado === 'ok' ? 'Funciona' : 'No responde'}</strong>
              </li>
            ))}
            <EstadoSello sello={salud.sello} />
          </ul>
          <p className="nota">
            Entorno: {salud.entorno} · Versión {salud.version}
          </p>
        </section>
      )}
    </>
  )
}
