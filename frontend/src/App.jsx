/**
 * Componente raíz: define las rutas de la aplicación.
 *
 * - Pantallas de acceso (solo sin sesión): inicio de sesión, registro y
 *   recuperación de la contraseña.
 * - Pantallas de enlaces recibidos por correo y textos legales: accesibles
 *   con o sin sesión.
 * - Pantallas internas: requieren sesión (CA22).
 *
 * Realiza: CA22 de la funcionalidad 002.
 */
import { Route, Routes } from 'react-router'
import { DisposicionAcceso, DisposicionInterna } from './componentes/Disposiciones.jsx'
import { RutaProtegida, RutaSoloVisitantes } from './rutas/Rutas.jsx'
import PaginaConfirmarCorreo from './paginas/PaginaConfirmarCorreo.jsx'
import PaginaEstado from './paginas/PaginaEstado.jsx'
import PaginaIniciarSesion from './paginas/PaginaIniciarSesion.jsx'
import PaginaInicio from './paginas/PaginaInicio.jsx'
import PaginaNoEncontrada from './paginas/PaginaNoEncontrada.jsx'
import PaginaPerfil from './paginas/PaginaPerfil.jsx'
import PaginaPrivacidad from './paginas/PaginaPrivacidad.jsx'
import PaginaRecuperarContrasenia from './paginas/PaginaRecuperarContrasenia.jsx'
import PaginaRegistro from './paginas/PaginaRegistro.jsx'
import PaginaRestablecerContrasenia from './paginas/PaginaRestablecerContrasenia.jsx'
import PaginaTerminos from './paginas/PaginaTerminos.jsx'
import PaginaVerificarCorreo from './paginas/PaginaVerificarCorreo.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<DisposicionAcceso />}>
        <Route element={<RutaSoloVisitantes />}>
          <Route path="/iniciar-sesion" element={<PaginaIniciarSesion />} />
          <Route path="/registro" element={<PaginaRegistro />} />
          <Route path="/recuperar-contrasenia" element={<PaginaRecuperarContrasenia />} />
        </Route>
        <Route path="/verificar-correo" element={<PaginaVerificarCorreo />} />
        <Route path="/restablecer-contrasenia" element={<PaginaRestablecerContrasenia />} />
        <Route path="/confirmar-correo" element={<PaginaConfirmarCorreo />} />
        <Route path="/terminos" element={<PaginaTerminos />} />
        <Route path="/privacidad" element={<PaginaPrivacidad />} />
        <Route path="/estado" element={<PaginaEstado />} />
        <Route path="*" element={<PaginaNoEncontrada />} />
      </Route>

      <Route element={<RutaProtegida />}>
        <Route element={<DisposicionInterna />}>
          <Route path="/" element={<PaginaInicio />} />
          <Route path="/perfil" element={<PaginaPerfil />} />
        </Route>
      </Route>
    </Routes>
  )
}
