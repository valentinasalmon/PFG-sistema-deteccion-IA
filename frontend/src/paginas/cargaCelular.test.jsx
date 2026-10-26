/**
 * Pruebas de la carga desde el celular con un código QR (funcionalidad 024).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
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

    await usuario.click(await screen.findByRole('button', { name: 'Mostrar el QR' }))

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

const API_DEL_CASO = {
  ...CON_SESION,
  'GET /api/casos/7': { cuerpo: { caso: CASO, accesos: [] } },
  'GET /api/casos/7/imagenes': {
    cuerpo: { imagenes: [], limite: 20, tamanio_maximo: 20 * 1024 * 1024, puede_modificar: true },
  },
}

describe('enlace para la persona afectada en el caso (028, CP-32)', () => {
  it('crea el enlace con su vigencia, lo ofrece para enviar y lo anula', async () => {
    let enlaces = []
    const creado = {
      id: 4,
      destinatario: 'Juan Gómez',
      creado_en: '2026-10-28T12:00:00',
      vence_en: '2026-11-04T12:00:00',
      creado_por: 'Ana López',
      cargas: 0,
      declaracion_aceptada: false,
    }
    const { solicitudes } = simularApi({
      ...API_DEL_CASO,
      'GET /api/casos/7/enlaces-persona-afectada': () => ({ cuerpo: { enlaces, dias_maximos: 30 } }),
      'POST /api/casos/7/enlaces-persona-afectada': () => {
        enlaces = [creado]
        return {
          estado: 201,
          cuerpo: { enlace: { ...creado, url: 'http://localhost/cargar/token-afectada' }, mensaje: 'Listo.' },
        }
      },
      'DELETE /api/casos/7/enlaces-persona-afectada/4': () => {
        enlaces = []
        return { cuerpo: { mensaje: 'Anulado.' } }
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.click(await screen.findByRole('button', { name: 'Crear el enlace' }))
    const panel = await screen.findByRole('region', { name: 'Enlace para la persona afectada' })
    await usuario.type(within(panel).getByLabelText(/Para quién/), 'Juan Gómez')
    expect(within(panel).getByLabelText('Vence en')).toHaveValue('7')
    await usuario.click(within(panel).getByRole('button', { name: 'Crear el enlace' }))

    expect(await within(panel).findByDisplayValue('http://localhost/cargar/token-afectada')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'POST').cuerpo).toEqual({ dias: 7, destinatario: 'Juan Gómez' })
    const whatsapp = within(panel).getByRole('link', { name: 'Enviar por WhatsApp' })
    expect(decodeURIComponent(whatsapp.getAttribute('href'))).toContain('Hola, Juan Gómez.')
    expect(decodeURIComponent(whatsapp.getAttribute('href'))).not.toContain('CASO-2026')
    expect(await within(panel).findByText(/Vence el 04\/11\/2026/)).toBeInTheDocument()

    await usuario.click(within(panel).getByRole('button', { name: 'Anular' }))
    await usuario.click(within(panel).getByRole('button', { name: 'Anular' }))
    await vi.waitFor(() => expect(within(panel).queryByText(/Vence el 04\/11\/2026/)).not.toBeInTheDocument())
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

  it('la persona afectada ve quién le pide las fotos y acepta la declaración (028, CP-32)', async () => {
    const { solicitudes } = simularApi({
      'GET /api/carga/token-afectada': {
        cuerpo: {
          tipo: 'persona_afectada',
          solicitante: 'Ana López',
          organizacion: 'Estudio Pérez',
          vence_en: '2099-01-08T12:00:00',
          restantes: 30,
          declaracion: 'Declaro que las fotos son mías o que tengo permiso para compartirlas.',
          declaracion_aceptada: false,
          tamanio_maximo: 20 * 1024 * 1024,
        },
      },
      'POST /api/carga/token-afectada': (cuerpo) => ({
        estado: 201,
        cuerpo: { imagen: { nombre: cuerpo.archivo.name }, mensaje: 'Se cargó.' },
      }),
    })
    const { usuario } = renderizarEn('/cargar/token-afectada')

    expect(await screen.findByRole('heading', { name: 'Te piden fotos del hecho' })).toBeInTheDocument()
    expect(screen.getByText('Ana López')).toBeInTheDocument()
    expect(screen.getByText('Estudio Pérez')).toBeInTheDocument()
    expect(screen.queryByText(/CASO-/)).not.toBeInTheDocument()
    const galeria = screen.getByLabelText('Elegir de la galería')
    expect(galeria).toBeDisabled()
    expect(screen.getByText('Marcá la declaración para continuar.')).toBeInTheDocument()

    await usuario.click(screen.getByRole('checkbox', { name: /Declaro que las fotos son mías/ }))
    expect(galeria).toBeEnabled()
    await usuario.upload(galeria, [archivo('choque.jpg')])

    const lista = await screen.findByRole('list', { name: 'Tus fotos' })
    expect(within(lista).getByText(/Subida/)).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'POST').cuerpo.declaracion).toBe('true')

    await usuario.click(screen.getByRole('button', { name: 'Terminé' }))
    expect(screen.getByRole('heading', { name: '¡Listo, gracias!' })).toBeInTheDocument()
    expect(screen.getByText(/Enviaste 1 foto a Ana López/)).toBeInTheDocument()
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
