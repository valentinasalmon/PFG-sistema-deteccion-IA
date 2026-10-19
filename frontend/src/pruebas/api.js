/**
 * Utilidades de prueba: simulan la API del backend reemplazando fetch.
 *
 * Cada respuesta se define por "MÉTODO /ruta". El valor puede ser un objeto
 * { estado, cuerpo } o una función que recibe el cuerpo enviado y devuelve
 * ese objeto (para variar la respuesta según los datos). Las solicitudes
 * recibidas quedan en `solicitudes` para verificarlas.
 */
import { vi } from 'vitest'

export function simularApi(respuestas = {}) {
  const solicitudes = []
  const fetchSimulado = vi.fn(async (ruta, opciones = {}) => {
    const metodo = opciones.method ?? 'GET'
    let cuerpoEnviado
    if (opciones.body instanceof FormData) cuerpoEnviado = Object.fromEntries(opciones.body)
    else if (opciones.body) cuerpoEnviado = JSON.parse(opciones.body)
    solicitudes.push({ metodo, ruta, cuerpo: cuerpoEnviado, cabeceras: opciones.headers ?? {} })

    let respuesta = respuestas[`${metodo} ${ruta}`]
    if (typeof respuesta === 'function') respuesta = respuesta(cuerpoEnviado)
    if (!respuesta && ruta === '/api/sesion/csrf') respuesta = { estado: 200, cuerpo: { csrf: 'token-csrf' } }
    if (!respuesta && metodo === 'GET' && ruta === '/api/sesion') {
      respuesta = { estado: 401, cuerpo: { codigo: 'sesion_requerida', mensaje: 'Tenés que iniciar sesión.' } }
    }
    if (!respuesta) throw new Error(`Solicitud no simulada: ${metodo} ${ruta}`)

    const { estado = 200, cuerpo = {} } = respuesta
    return { ok: estado >= 200 && estado < 300, status: estado, json: async () => cuerpo }
  })
  vi.stubGlobal('fetch', fetchSimulado)
  return { solicitudes, fetch: fetchSimulado }
}

/** Usuario de ejemplo con sesión iniciada. */
export const USUARIO = {
  id: 1,
  nombre: 'Ana',
  apellido: 'López',
  correo: 'ana@ejemplo.com',
  perfil: 'abogado',
  colegio: 'CPACF',
  rol: 'usuario',
}

/** Respuesta de GET /api/sesion con una sesión abierta. */
export const CON_SESION = { 'GET /api/sesion': { estado: 200, cuerpo: { usuario: USUARIO } } }
