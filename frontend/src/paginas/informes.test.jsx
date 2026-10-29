/**
 * Pruebas de la descarga, el historial y la regeneración de los informes PDF
 * (funcionalidad 008).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

vi.mock('../utilidades/archivos.js', async (original) => ({
  ...(await original()),
  abrirDescarga: vi.fn(),
}))
const { abrirDescarga } = await import('../utilidades/archivos.js')

const CASO = {
  id: 7,
  cantidad_imagenes: 2,
  cantidad_informes: 1,
  numero: 'CASO-2026-000007',
  tipo: 'laboral',
  tipo_nombre: 'Laboral',
  fecha_hecho: '2026-10-01',
  lugar: 'Planta',
  expediente: null,
  descripcion: null,
  estado: 'analizado',
  estado_nombre: 'Analizado',
  espacio: { tipo: 'personal', id: null, nombre: 'Personal' },
  responsable: { id: USUARIO.id, nombre: 'Ana López', correo: 'ana@ejemplo.com' },
  mi_permiso: 'responsable',
  mi_permiso_nombre: 'Responsable',
  creado_en: '2026-10-16T12:00:00',
  actualizado_en: '2026-10-19T15:10:05',
  retencion_vence: null,
  acciones: {
    editar: true, cerrar: true, archivar: false, desarchivar: false, reabrir: false,
    compartir: false, transferir: true, eliminar: true,
  },
  transferencia_pendiente: null,
}
const INFORME = {
  id: 3,
  id_analisis: 5,
  generado_en: '2026-10-19T15:10:05',
  solicitante: 'Ana López',
  imagenes: ['frente.jpg', 'lateral.png'],
  huella: 'f'.repeat(64),
  tamanio: 48 * 1024,
}
const RESUMEN = {
  id: 5,
  estado: 'finalizado',
  estado_nombre: 'Finalizado',
  en_curso: false,
  solicitante: 'Ana López',
  creado_en: '2026-10-19T15:10:00',
  finalizado_en: '2026-10-19T15:10:05',
  cantidad_imagenes: 2,
  progreso: { imagen_actual: 2, capa_actual: null },
  motivo_falla: null,
}
const DETALLE = { ...RESUMEN, versiones: {}, imagenes: [], informe: INFORME }

function api({ caso = CASO, detalle = DETALLE, informes = [INFORME], extra = {} } = {}) {
  return simularApi({
    ...CON_SESION,
    'GET /api/casos/7': { cuerpo: { caso, accesos: [] } },
    'GET /api/casos/7/imagenes': {
      cuerpo: { imagenes: [], limite: 20, tamanio_maximo: 1, puede_modificar: caso.acciones.editar },
    },
    'GET /api/casos/7/analisis': { cuerpo: { analisis: [RESUMEN] } },
    'GET /api/casos/7/analisis/5': typeof detalle === 'function' ? () => ({ cuerpo: { analisis: detalle() } }) : { cuerpo: { analisis: detalle } },
    'GET /api/casos/7/informes': typeof informes === 'function' ? () => ({ cuerpo: { informes: informes() } }) : { cuerpo: { informes } },
    'GET /api/casos/7/informes/3/descarga': { cuerpo: { url: '/api/archivos/token-pdf' } },
    ...extra,
  })
}

describe('informes del caso', () => {
  it('lista el historial con solicitante, imágenes y huella, y descarga el PDF (CA7, CA8)', async () => {
    api()
    const { usuario } = renderizarEn('/casos/7')

    // Con informes, el caso analizado abre en la etapa del informe (028).
    const seccion = await screen.findByRole('region', { name: 'Informes' })
    expect(within(seccion).getByRole('heading', { name: 'Informe del 19/10/2026' })).toBeInTheDocument()
    expect(within(seccion).getByText('Pedido por Ana López')).toBeInTheDocument()
    expect(within(seccion).getByText('frente.jpg')).toBeInTheDocument()
    expect(within(seccion).getByText('lateral.png')).toBeInTheDocument()
    expect(within(seccion).getByText('f'.repeat(64))).toBeInTheDocument()
    expect(within(seccion).getByText('48 KB')).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Cargar imágenes' })).not.toBeInTheDocument()

    await usuario.click(within(seccion).getByRole('button', { name: 'Descargar el informe del 19/10/2026' }))

    await vi.waitFor(() => expect(abrirDescarga).toHaveBeenCalledWith('/api/archivos/token-pdf'))
  })

  it('cada análisis finalizado ofrece descargar su informe', async () => {
    abrirDescarga.mockClear()
    api()
    const { usuario } = renderizarEn('/casos/7?etapa=analisis')

    await usuario.click(await screen.findByRole('button', { name: 'Descargar el informe PDF' }))

    await vi.waitFor(() => expect(abrirDescarga).toHaveBeenCalledWith('/api/archivos/token-pdf'))
  })

  it('si el informe no se generó, permite generarlo de nuevo (CA6)', async () => {
    let informe = null
    const { solicitudes } = api({
      detalle: () => ({ ...DETALLE, informe }),
      informes: () => (informe ? [informe] : []),
      extra: {
        'POST /api/casos/7/analisis/5/informe': () => {
          informe = INFORME
          return { estado: 201, cuerpo: { informe: INFORME, mensaje: 'Se generó el informe.' } }
        },
      },
    })
    const { usuario } = renderizarEn('/casos/7?etapa=analisis')

    expect(await screen.findByText('No se pudo generar el informe PDF de este análisis.')).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Informes' })).not.toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Generar el informe' }))

    expect(solicitudes.some((s) => s.metodo === 'POST' && s.ruta === '/api/casos/7/analisis/5/informe')).toBe(true)
    expect(await screen.findByRole('button', { name: 'Descargar el informe PDF' })).toBeInTheDocument()
  })

  it('el Lector no puede generar el informe que falta', async () => {
    api({
      caso: { ...CASO, mi_permiso: 'lectura', acciones: { ...CASO.acciones, editar: false } },
      detalle: { ...DETALLE, informe: null },
      informes: [],
    })
    renderizarEn('/casos/7?etapa=analisis')

    expect(await screen.findByText('No se pudo generar el informe PDF de este análisis.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Generar el informe' })).not.toBeInTheDocument()
  })

  it('muestra los errores de la descarga y del historial', async () => {
    api({
      extra: { 'GET /api/casos/7/informes/3/descarga': { estado: 404, cuerpo: { mensaje: 'El informe no existe.' } } },
    })
    const { usuario } = renderizarEn('/casos/7')

    const seccion = await screen.findByRole('region', { name: 'Informes' })
    await usuario.click(within(seccion).getByRole('button', { name: /Descargar el informe del/ }))
    expect(await within(seccion).findByText('El informe no existe.')).toBeInTheDocument()

    await usuario.click(screen.getByRole('link', { name: /Análisis/ }))
    await usuario.click(await screen.findByRole('button', { name: 'Descargar el informe PDF' }))
    expect(await screen.findByText('El informe no existe.')).toBeInTheDocument()
  })

  it('muestra el resumen por imagen y los informes anteriores (028)', async () => {
    const anterior = { ...INFORME, id: 2, id_analisis: null, generado_en: '2026-10-18T10:00:00', imagenes: ['viejo.jpg'] }
    api({
      detalle: {
        ...DETALLE,
        imagenes: [
          {
            id_imagen: 1, nombre: 'frente.jpg', huella: 'a', integridad: 'verificada',
            resultados: [{ capa: 'metadatos', estado: 'completado', nivel: 10, anomalias: [] }],
          },
        ],
      },
      informes: [INFORME, anterior],
    })
    renderizarEn('/casos/7')

    const resumen = await screen.findByRole('list', { name: 'Resultado por imagen' })
    expect(within(resumen).getByText('frente.jpg')).toBeInTheDocument()
    expect(within(resumen).getByText(/· 10 %/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Informes anteriores' })).toBeInTheDocument()
    expect(screen.getByText(/1 imagen\(es\): viejo.jpg/)).toBeInTheDocument()
  })

  it('sin informes, la etapa lo explica (028)', async () => {
    api({ informes: [] })
    renderizarEn('/casos/7?etapa=informe')

    expect(await screen.findByText(/Todavía no hay informes/)).toBeInTheDocument()
  })

  it('muestra el error del historial de informes', async () => {
    api({ extra: { 'GET /api/casos/7/informes': { estado: 500, cuerpo: { mensaje: 'Error del servidor.' } } } })
    renderizarEn('/casos/7')

    const seccion = await screen.findByRole('region', { name: 'Informes' })
    expect(within(seccion).getByText('Error del servidor.')).toBeInTheDocument()
  })
})
