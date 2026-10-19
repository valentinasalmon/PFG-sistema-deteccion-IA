/**
 * Operaciones sobre casos y sus accesos (funcionalidad 005).
 *
 * Realiza: RF23 a RF33.
 */
import { solicitar } from './cliente.js'

const base = (id) => `/api/casos/${id}`

/** Casos accesibles con búsqueda, filtros y página (RF26). */
export function listarCasos(filtros = {}) {
  const parametros = new URLSearchParams(
    Object.entries(filtros).filter(([, valor]) => valor !== '' && valor !== null && valor !== undefined),
  )
  const consulta = parametros.toString()
  return solicitar('GET', consulta ? `/api/casos?${consulta}` : '/api/casos')
}

/** Cantidad de casos por estado. */
export async function resumenDeCasos() {
  const { por_estado: porEstado } = await solicitar('GET', '/api/casos/resumen')
  return porEstado
}

/** Transferencias de casos personales que esperan mi respuesta (RF33 CA2). */
export async function transferenciasPendientes() {
  const { transferencias } = await solicitar('GET', '/api/casos/transferencias')
  return transferencias
}

/** Crea un caso (RF23). */
export async function crearCaso(datos) {
  const { caso } = await solicitar('POST', '/api/casos', datos)
  return caso
}

/** Detalle del caso y sus accesos (RF24). */
export function obtenerCaso(id) {
  return solicitar('GET', base(id))
}

/** Modifica los datos del caso (RF25). */
export function editarCaso(id, cambios) {
  return solicitar('PATCH', base(id), cambios)
}

/** Cierra, archiva, desarchiva o reabre el caso (RF27 a RF29). */
export function cambiarEstadoCaso(id, operacion) {
  return solicitar('POST', `${base(id)}/estado`, { operacion })
}

/** Comparte con un miembro o, sin idUsuario, con toda la organización (RF30). */
export function compartirCaso(id, nivel, idUsuario = null) {
  return solicitar('POST', `${base(id)}/accesos`, { nivel, id_usuario: idUsuario })
}

/** Cambia el nivel de un acceso (RF31). */
export function modificarAcceso(id, idAcceso, nivel) {
  return solicitar('PATCH', `${base(id)}/accesos/${idAcceso}`, { nivel })
}

/** Revoca un acceso (RF31). */
export function revocarAcceso(id, idAcceso) {
  return solicitar('DELETE', `${base(id)}/accesos/${idAcceso}`)
}

/** Transfiere el caso: id de un miembro o correo de un usuario (RF33). */
export function transferirCaso(id, destino, conservarColaboracion = true) {
  return solicitar('POST', `${base(id)}/transferencia`, {
    destino: String(destino),
    conservar_colaboracion: conservarColaboracion,
  })
}

/** Cancela una transferencia pendiente. */
export function cancelarTransferencia(id) {
  return solicitar('DELETE', `${base(id)}/transferencia`)
}

/** Acepta o rechaza un caso personal transferido. */
export function responderTransferencia(id, aceptar) {
  return solicitar('POST', `${base(id)}/transferencia/${aceptar ? 'aceptacion' : 'rechazo'}`)
}

/** Elimina el caso; exige su número como confirmación (RF32). */
export function eliminarCaso(id, confirmacion) {
  return solicitar('DELETE', base(id), { confirmacion })
}
