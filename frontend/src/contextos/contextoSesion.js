/**
 * Contexto de React que comparte la sesión con toda la aplicación.
 *
 * Se define en un archivo propio para que el proveedor y el hook useSesion
 * puedan importarlo sin depender uno del otro.
 */
import { createContext } from 'react'

export const ContextoSesion = createContext(null)
