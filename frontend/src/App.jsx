/**
 * Componente raíz: define las rutas de la aplicación.
 *
 * - Pantallas de acceso (solo sin sesión): inicio de sesión, registro y
 *   recuperación de la contraseña.
 * - Pantallas de enlaces recibidos por correo (incluida la invitación a una
 *   organización), la carga desde el celular con un QR (024) y textos
 *   legales: accesibles con o sin sesión.
 * - Pantallas internas: requieren sesión (CA22).
 *
 * Realiza: CA22 de la funcionalidad 002; pantallas de las funcionalidades 004
 * y 005.
 */
import { Route, Routes } from 'react-router'
import { DisposicionAcceso, DisposicionInterna } from './componentes/Disposiciones.jsx'
import { RutaProtegida, RutaSoloVisitantes } from './rutas/Rutas.jsx'
import PaginaAdministracion from './paginas/PaginaAdministracion.jsx'
import PaginaCargaCelular from './paginas/PaginaCargaCelular.jsx'
import PaginaCaso from './paginas/PaginaCaso.jsx'
import PaginaCasos from './paginas/PaginaCasos.jsx'
import PaginaConfirmarCorreo from './paginas/PaginaConfirmarCorreo.jsx'
import PaginaEstado from './paginas/PaginaEstado.jsx'
import PaginaIniciarSesion from './paginas/PaginaIniciarSesion.jsx'
import PaginaInvitacion from './paginas/PaginaInvitacion.jsx'
import PaginaInicio from './paginas/PaginaInicio.jsx'
import PaginaNoEncontrada from './paginas/PaginaNoEncontrada.jsx'
import PaginaNuevaOrganizacion from './paginas/PaginaNuevaOrganizacion.jsx'
import PaginaNuevoCaso from './paginas/PaginaNuevoCaso.jsx'
import PaginaOrganizacion from './paginas/PaginaOrganizacion.jsx'
import PaginaOrganizaciones from './paginas/PaginaOrganizaciones.jsx'
import PaginaPerfil from './paginas/PaginaPerfil.jsx'
import PaginaPrivacidad from './paginas/PaginaPrivacidad.jsx'
import PaginaRecuperarContrasenia from './paginas/PaginaRecuperarContrasenia.jsx'
import PaginaRegistro from './paginas/PaginaRegistro.jsx'
import PaginaRegistroGoogle from './paginas/PaginaRegistroGoogle.jsx'
import PaginaRestablecerContrasenia from './paginas/PaginaRestablecerContrasenia.jsx'
import PaginaTerminos from './paginas/PaginaTerminos.jsx'
import PaginaVerificarCorreo from './paginas/PaginaVerificarCorreo.jsx'
import PaginaVerificarInforme from './paginas/PaginaVerificarInforme.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<DisposicionAcceso />}>
        <Route element={<RutaSoloVisitantes />}>
          <Route path="/iniciar-sesion" element={<PaginaIniciarSesion />} />
          <Route path="/registro" element={<PaginaRegistro />} />
          <Route path="/registro/google" element={<PaginaRegistroGoogle />} />
          <Route path="/recuperar-contrasenia" element={<PaginaRecuperarContrasenia />} />
        </Route>
        <Route path="/verificar-correo" element={<PaginaVerificarCorreo />} />
        <Route path="/restablecer-contrasenia" element={<PaginaRestablecerContrasenia />} />
        <Route path="/confirmar-correo" element={<PaginaConfirmarCorreo />} />
        <Route path="/invitaciones/responder" element={<PaginaInvitacion />} />
        <Route path="/cargar/:token" element={<PaginaCargaCelular />} />
        <Route path="/verificar" element={<PaginaVerificarInforme />} />
        <Route path="/verificar/:codigo" element={<PaginaVerificarInforme />} />
        <Route path="/terminos" element={<PaginaTerminos />} />
        <Route path="/privacidad" element={<PaginaPrivacidad />} />
        <Route path="/estado" element={<PaginaEstado />} />
        <Route path="*" element={<PaginaNoEncontrada />} />
      </Route>

      <Route element={<RutaProtegida />}>
        <Route element={<DisposicionInterna />}>
          <Route path="/" element={<PaginaInicio />} />
          <Route path="/perfil" element={<PaginaPerfil />} />
          <Route path="/casos" element={<PaginaCasos />} />
          <Route path="/casos/nuevo" element={<PaginaNuevoCaso />} />
          <Route path="/casos/:id" element={<PaginaCaso />} />
          <Route path="/organizaciones" element={<PaginaOrganizaciones />} />
          <Route path="/organizaciones/nueva" element={<PaginaNuevaOrganizacion />} />
          <Route path="/organizaciones/:id" element={<PaginaOrganizacion />} />
          <Route path="/administracion" element={<PaginaAdministracion />} />
        </Route>
      </Route>
    </Routes>
  )
}
