/**
 * Proveedor de la sesión: sabe quién inició sesión y ofrece las acciones
 * para iniciarla, cerrarla y actualizar los datos del usuario.
 *
 * Al cargar la aplicación consulta GET /api/sesion para recuperar una sesión
 * abierta. Si cualquier solicitud informa que la sesión venció (por
 * inactividad o duración máxima), borra el usuario y las rutas protegidas
 * redirigen al inicio de sesión. ``motivoSalida`` indica por qué terminó la
 * sesión ('cierre' o 'vencida') para mostrar el aviso correspondiente.
 *
 * Realiza: RF03, RF04 y CA7, CA12, CA22 de la funcionalidad 002.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { configurarAlExpirarSesion } from '../api/cliente.js'
import * as apiSesion from '../api/sesion.js'
import { ContextoSesion } from './contextoSesion.js'

export default function ProveedorSesion({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [motivoSalida, setMotivoSalida] = useState(null)
  // Permite saber, desde el aviso de sesión vencida, si había alguien conectado.
  const usuarioActual = useRef(null)

  useEffect(() => {
    usuarioActual.current = usuario
  }, [usuario])

  useEffect(() => {
    let activo = true
    apiSesion
      .obtenerSesion()
      .then((datos) => activo && setUsuario(datos))
      .catch(() => activo && setUsuario(null))
      .finally(() => activo && setCargando(false))
    return () => {
      activo = false
    }
  }, [])

  useEffect(() => {
    configurarAlExpirarSesion(() => {
      if (usuarioActual.current) setMotivoSalida('vencida')
      setUsuario(null)
    })
    return () => configurarAlExpirarSesion(null)
  }, [])

  const iniciarSesion = useCallback(async (correo, contrasenia) => {
    const datos = await apiSesion.iniciarSesion(correo, contrasenia)
    setMotivoSalida(null)
    setUsuario(datos)
    return datos
  }, [])

  const cerrarSesion = useCallback(async () => {
    try {
      await apiSesion.cerrarSesion()
    } finally {
      setMotivoSalida('cierre')
      setUsuario(null)
    }
  }, [])

  const recargarUsuario = useCallback(async () => {
    const datos = await apiSesion.obtenerSesion()
    setUsuario(datos)
    return datos
  }, [])

  const valor = useMemo(
    () => ({
      usuario,
      cargando,
      motivoSalida,
      iniciarSesion,
      cerrarSesion,
      recargarUsuario,
      actualizarUsuario: setUsuario,
    }),
    [usuario, cargando, motivoSalida, iniciarSesion, cerrarSesion, recargarUsuario],
  )

  return <ContextoSesion.Provider value={valor}>{children}</ContextoSesion.Provider>
}
