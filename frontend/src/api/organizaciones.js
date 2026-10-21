/**
 * Operaciones sobre organizaciones, sus miembros y sus invitaciones.
 *
 * Realiza: RF10 a RF18 (funcionalidad 004).
 */
import { solicitar } from './cliente.js'

const base = (id) => `/api/organizaciones/${id}`

/** Organizaciones a las que pertenece el usuario, con su rol. */
export async function listarOrganizaciones() {
  const { organizaciones } = await solicitar('GET', '/api/organizaciones')
  return organizaciones
}

/** Crea una organización; el usuario queda como Referente (RF10). */
export async function crearOrganizacion(datos) {
  const { organizacion } = await solicitar('POST', '/api/organizaciones', datos)
  return organizacion
}

/** Datos de una organización, su plan y el rol del usuario. */
export async function obtenerOrganizacion(id) {
  const { organizacion } = await solicitar('GET', base(id))
  return organizacion
}

/** Modifica los datos de la organización (RF11). */
export function editarOrganizacion(id, cambios) {
  return solicitar('PATCH', base(id), cambios)
}

/** Elimina la organización; exige su nombre como confirmación (RF18). */
export function eliminarOrganizacion(id, confirmacion) {
  return solicitar('DELETE', base(id), { confirmacion })
}

/** Miembros de la organización (RF16). */
export async function listarMiembros(id) {
  const { miembros } = await solicitar('GET', `${base(id)}/miembros`)
  return miembros
}

/** Cambia el cargo de un miembro (RF15). */
export function editarCargo(id, idUsuario, cargo) {
  return solicitar('PATCH', `${base(id)}/miembros/${idUsuario}`, { cargo })
}

/** Desvincula a un miembro (RF14). */
export function desvincularMiembro(id, idUsuario) {
  return solicitar('DELETE', `${base(id)}/miembros/${idUsuario}`)
}

/** Transfiere el rol de Referente a otro miembro (RF15). */
export function designarReferente(id, idUsuario) {
  return solicitar('POST', `${base(id)}/referente`, { id_usuario: idUsuario })
}

/** Abandona la organización; si es el único miembro, debe confirmar su eliminación (RF17). */
export function abandonarOrganizacion(id, confirmarEliminacion = false) {
  return solicitar('POST', `${base(id)}/abandono`, { confirmar_eliminacion: confirmarEliminacion })
}

/** Invitaciones pendientes de la organización (Referente). */
export async function listarInvitaciones(id) {
  const { invitaciones } = await solicitar('GET', `${base(id)}/invitaciones`)
  return invitaciones
}

/** Invita a una persona por correo (RF12). */
export function invitar(id, correo, cargo) {
  return solicitar('POST', `${base(id)}/invitaciones`, { correo, cargo: cargo || null })
}

/** Reenvía una invitación y renueva su vencimiento (RF12). */
export function reenviarInvitacion(id, idInvitacion) {
  return solicitar('POST', `${base(id)}/invitaciones/${idInvitacion}/reenvio`)
}

/** Cancela una invitación pendiente (RF12). */
export function cancelarInvitacion(id, idInvitacion) {
  return solicitar('DELETE', `${base(id)}/invitaciones/${idInvitacion}`)
}

/** Invitaciones pendientes dirigidas al correo del usuario. */
export async function misInvitaciones() {
  const { invitaciones } = await solicitar('GET', '/api/invitaciones')
  return invitaciones
}

/** Datos de la invitación de un enlace; no requiere sesión. */
export async function consultarInvitacion(token) {
  const { invitacion } = await solicitar('POST', '/api/invitaciones/consulta', { token })
  return invitacion
}

/** Acepta una invitación (RF13). */
export function aceptarInvitacion(idInvitacion) {
  return solicitar('POST', `/api/invitaciones/${idInvitacion}/aceptacion`)
}

/** Rechaza una invitación (RF13). */
export function rechazarInvitacion(idInvitacion) {
  return solicitar('POST', `/api/invitaciones/${idInvitacion}/rechazo`)
}

/** Plan, límites y consumo de la organización (RF20, funcionalidad 014). */
export async function obtenerPlan(idOrganizacion) {
  const { plan } = await solicitar('GET', `/api/organizaciones/${idOrganizacion}/plan`)
  return plan
}

/** Aplica otro plan después del pago simulado (RF20 CA2). */
export function cambiarPlan(idOrganizacion, plan) {
  return solicitar('POST', `/api/organizaciones/${idOrganizacion}/plan`, { plan })
}
