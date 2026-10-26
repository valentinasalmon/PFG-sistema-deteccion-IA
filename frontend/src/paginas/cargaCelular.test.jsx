/**
 * Pruebas de la carga desde el celular con un código QR (funcionalidad 024).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const CASO = {
  id: 7,
  numero: 'CASO-2026-000007',
  tipo: 'laboral',
  tipo_nombre: 'Laboral',
  fecha_hecho: '2026-10-01',
  lugar: 'Planta',
  expediente: null,
  descripcion: null,
  estado: 'borrador',
  estado_nombre: 'Borrador',
  espacio: { tipo: 'personal', id: null, nombre: 'Personal' },
  responsable: { id: USUARIO.id, nombre: 'Ana López', correo: 'ana@ejemplo.com' },
  mi_permiso: 'responsable',
  mi_permiso_nombre: 'Responsable',
  creado_en: '2026-10-16T12:00:00',
  actualizado_en: '2026-10-16T12:00:00',
  retencion_vence: null,
  acciones: {
    editar: true,
    cerrar: true,
    archivar: false,
    desarchivar: false,
    reabrir: false,
    compartir: false,
    transferir: true,
    eliminar: true,
  },
  transferencia_pendiente: null,
}

const ENLACE = {
  url: 'http://localhost/cargar/token-de-prueba',
  qr: 'data:image/svg+xml,qr',
  vence_en: '2099-01-01T12:15:00',
}

function archivo(nombre) {
  return new File([new Uint8Array(10)], nombre, { type: 'image/jpeg' })
}

describe('cargar desde el celular en la computadora (RF53 CA2)', () => {
  it('muestra el QR del caso y lo cancela al cerrarlo', async () => {
    const { solicitudes } = simularApi({
      ...CON_SESION,
      'GET /api/casos/7': { cuerpo: { caso: CASO, accesos: [] } },
      'GET /api/casos/7/imagenes': {
        cuerpo: { imagenes: [], limite: 20, tamanio_maximo: 20 * 1024 * 1024, puede_modificar: true },
      },
      'GET /api/casos/7/analisis': { cuerpo: { analisis: [] } },
      'GET /api/casos/7/informes': { cuerpo: { informes: [] } },
      'POST /api/casos/7/enlace-carga': { estado: 201, cuerpo: { enlace: ENLACE } },
      'DELETE /api/casos/7/enlace-carga': { cuerpo: { mensaje: 'Cancelado.' } },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.click(await screen.findByRole('button', { name: 'Cargar desde el celular' }))

    const panel = await screen.findByRole('region', { name: 'Cargar desde el celular' })
    expect(within(panel).getByRole('img', { name: /Código QR/ })).toHaveAttribute('src', ENLACE.qr)
    expect(within(panel).getByText(/Abrí la cámara del celular/)).toBeInTheDocument()
    expect(within(panel).getByText(/todas las fotos que quieras/)).toBeInTheDocument()

    await usuario.click(within(panel).getByRole('button', { name: 'Cancelar' }))
    expect(screen.queryByRole('region', { name: 'Cargar desde el celular' })).not.toBeInTheDocument()
    expect(solicitudes.some((s) => s.metodo === 'DELETE' && s.ruta === '/api/casos/7/enlace-carga')).toBe(
      true,
    )
  })
})

describe('página del celular (RF53 CA2 a CA4)', () => {
  it('sube las fotos elegidas sin iniciar sesión', async () => {
    let restantes = 30
    const { solicitudes } = simularApi({
      'GET /api/carga/token-de-prueba': () => ({
        cuerpo: {
          numero: 'CASO-2026-000123',
          vence_en: '2099-01-01T12:15:00',
          restantes,
          tamanio_maximo: 20 * 1024 * 1024,
        },
      }),
      'POST /api/carga/token-de-prueba': (cuerpo) => {
        restantes -= 1
        return { estado: 201, cuerpo: { imagen: { nombre: cuerpo.archivo.name }, mensaje: 'Se cargó.' } }
      },
    })
    const { usuario } = renderizarEn('/cargar/token-de-prueba')

    expect(
      await screen.findByRole('heading', { name: 'Subir fotos al caso CASO-2026-000123' }),
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Sacar una foto')).toHaveAttribute('capture', 'environment')
    const galeria = screen.getByLabelText('Elegir de la galería')
    expect(galeria.getAttribute('accept')).toContain('image/heic')

    await usuario.upload(galeria, [archivo('IMG_0001.jpg'), archivo('IMG_0002.jpg')])

    const lista = await screen.findByRole('list', { name: 'Fotos subidas' })
    expect(within(lista).getAllByText(/Subida/)).toHaveLength(2)
    expect(solicitudes.filter((s) => s.metodo === 'POST' && s.ruta.startsWith('/api/carga/'))).toHaveLength(2)
  })

  it('avisa si el enlace venció', async () => {
    simularApi({
      'GET /api/carga/vencido': {
        estado: 404,
        cuerpo: { codigo: 'enlace_invalido', mensaje: 'El enlace venció o ya no es válido.' },
      },
    })
    renderizarEn('/cargar/vencido')

    expect(await screen.findByText('El enlace venció o ya no es válido.')).toBeInTheDocument()
  })
})
