/**
 * Página inicial del esqueleto caminante.
 *
 * Consulta el estado de la API al cargar y muestra, en español, si cada
 * componente del sistema responde. Es provisoria: a partir de la
 * funcionalidad 002 se reemplaza por el inicio de sesión.
 *
 * Realiza: CA4 y CA5 de la funcionalidad 001.
 */
import { useEffect, useState } from 'react'
import { obtenerSalud } from '../api/salud.js'

/** Nombres legibles de cada componente informado por la API. */
const NOMBRES_COMPONENTES = {
  api: 'API',
  base_de_datos: 'Base de datos',
  redis: 'Cola de tareas (Redis)',
}

export default function PaginaInicio() {
  const [salud, setSalud] = useState(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    obtenerSalud()
      .then(setSalud)
      .catch(() => setError(true))
  }, [])

  return (
    <main className="contenedor">
      <h1>Sistema de detección de imágenes</h1>
      <p className="subtitulo">Plataforma de apoyo a la evaluación preliminar de pruebas</p>

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
          </ul>
          <p className="pie">
            Entorno: {salud.entorno} · Versión {salud.version}
          </p>
        </section>
      )}
    </main>
  )
}
