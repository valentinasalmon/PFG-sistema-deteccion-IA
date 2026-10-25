/**
 * Pruebas de la sección "Imágenes" de la pantalla del caso (funcionalidad 006).
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

const ACCIONES = {
  editar: true, cerrar: true, archivar: false, desarchivar: false, reabrir: false,
  compartir: false, transferir: true, eliminar: true,
}
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
  acciones: ACCIONES,
  transferencia_pendiente: null,
}
const IMAGEN = {
  id: 11,
  nombre: 'frente.jpg',
  formato: 'JPEG',
  tamanio: 1572864,
  ancho: 4000,
  alto: 3000,
  huella: 'a'.repeat(64),
  cargada_en: '2026-10-19T15:00:00',
  cargada_por: 'Ana López',
  en_informe: false,
  miniatura: '/api/archivos/token-miniatura',
}
const LISTADO = { imagenes: [IMAGEN], limite: 20, tamanio_maximo: 20 * 1024 * 1024, puede_modificar: true }

function api(listado = LISTADO, extra = {}) {
  return simularApi({
    ...CON_SESION,
    'GET /api/casos/7': { cuerpo: { caso: CASO, accesos: [] } },
    'GET /api/casos/7/imagenes': typeof listado === 'function' ? listado : { cuerpo: listado },
    'GET /api/casos/7/analisis': { cuerpo: { analisis: [] } },
    'GET /api/casos/7/informes': { cuerpo: { informes: [] } },
    ...extra,
  })
}

const seccion = () => screen.getByRole('region', { name: /^Imágenes/ })

function archivo(nombre, tamanio = 10, tipo = 'image/jpeg') {
  return new File([new Uint8Array(tamanio)], nombre, { type: tipo })
}

describe('imágenes del caso', () => {
  it('muestra cada imagen con su vista previa, datos técnicos y huella (CA7)', async () => {
    api()
    renderizarEn('/casos/7')

    const vista = await screen.findByRole('img', { name: 'Vista previa de frente.jpg' })
    expect(vista).toHaveAttribute('src', '/api/archivos/token-miniatura')
    const zona = seccion()
    expect(within(zona).getByRole('heading', { name: 'Imágenes (1 de 20)' })).toBeInTheDocument()
    expect(within(zona).getByText(/JPEG · 4000 × 3000 px · 1,5 MB/)).toBeInTheDocument()
    expect(within(zona).getByText(`SHA-256: ${'a'.repeat(64)}`)).toBeInTheDocument()
    expect(within(zona).getByText(/Cargada el 19\/10\/2026 por Ana López/)).toBeInTheDocument()
  })

  it('carga varios archivos de a uno e informa el resultado de cada uno (CA5)', async () => {
    let imagenes = []
    const { solicitudes } = api(() => ({ cuerpo: { ...LISTADO, imagenes } }), {
      'POST /api/casos/7/imagenes': (cuerpo) => {
        if (cuerpo.archivo.name === 'texto.jpg') {
          return {
            estado: 400,
            cuerpo: {
              mensaje: 'Revisá los datos.',
              errores: { archivo: 'El formato real del archivo no es válido.' },
            },
          }
        }
        imagenes = [IMAGEN]
        return { estado: 201, cuerpo: { imagen: IMAGEN, mensaje: 'Se cargó.' } }
      },
    })
    const { usuario } = renderizarEn('/casos/7')
    await screen.findByText('Todavía no hay imágenes en este caso.')

    await usuario.upload(within(seccion()).getByLabelText('Elegir imágenes'), [
      archivo('frente.jpg'),
      archivo('texto.jpg'),
      archivo('enorme.png', 21 * 1024 * 1024, 'image/png'),
    ])

    const resultados = await screen.findByRole('list', { name: 'Resultado de la carga' })
    expect(within(resultados).getByText(/Cargada/)).toBeInTheDocument()
    expect(within(resultados).getByText(/El formato real del archivo no es válido/)).toBeInTheDocument()
    expect(within(resultados).getByText(/Supera el máximo de 20 MB/)).toBeInTheDocument()
    expect(await screen.findByRole('img', { name: 'Vista previa de frente.jpg' })).toBeInTheDocument()
    // El archivo demasiado grande no se envía.
    expect(solicitudes.filter((s) => s.metodo === 'POST').map((s) => s.cuerpo.archivo.name)).toEqual([
      'frente.jpg',
      'texto.jpg',
    ])
  })

  it('el Lector solo consulta y descarga (CA6)', async () => {
    api({ ...LISTADO, puede_modificar: false }, {
      'GET /api/casos/7/imagenes/11/descarga': { cuerpo: { url: '/api/archivos/token-original' } },
    })
    const { usuario } = renderizarEn('/casos/7')

    await screen.findByRole('img', { name: 'Vista previa de frente.jpg' })
    expect(within(seccion()).queryByLabelText('Elegir imágenes')).not.toBeInTheDocument()
    expect(within(seccion()).queryByRole('button', { name: 'Eliminar' })).not.toBeInTheDocument()

    await usuario.click(screen.getByRole('button', { name: 'Descargar el original de frente.jpg' }))

    await vi.waitFor(() => expect(abrirDescarga).toHaveBeenCalledWith('/api/archivos/token-original'))
  })

  it('elimina una imagen con confirmación (CA9)', async () => {
    let imagenes = [IMAGEN]
    api(() => ({ cuerpo: { ...LISTADO, imagenes } }), {
      'DELETE /api/casos/7/imagenes/11': () => {
        imagenes = []
        return { cuerpo: { mensaje: 'La imagen fue eliminada.' } }
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    await screen.findByRole('img', { name: 'Vista previa de frente.jpg' })
    await usuario.click(within(seccion()).getByRole('button', { name: 'Eliminar' }))
    await usuario.click(within(seccion()).getByRole('button', { name: 'Eliminar' }))

    expect(await screen.findByText('Se eliminó «frente.jpg».')).toBeInTheDocument()
    expect(screen.getByText('Todavía no hay imágenes en este caso.')).toBeInTheDocument()
  })

  it('una imagen en un informe no ofrece eliminarla (RN24)', async () => {
    api({ ...LISTADO, imagenes: [{ ...IMAGEN, en_informe: true }] })
    renderizarEn('/casos/7')

    expect(await screen.findByText('Está en un informe: no se puede eliminar.')).toBeInTheDocument()
    expect(within(seccion()).queryByRole('button', { name: 'Eliminar' })).not.toBeInTheDocument()
  })

  it('si la vista previa venció, permite volver a cargarla (CA8)', async () => {
    const { solicitudes } = api()
    const { usuario } = renderizarEn('/casos/7')

    const vista = await screen.findByRole('img', { name: 'Vista previa de frente.jpg' })
    vista.dispatchEvent(new Event('error'))
    await usuario.click(await screen.findByRole('button', { name: 'Volver a cargar la vista previa' }))

    await vi.waitFor(() =>
      expect(solicitudes.filter((s) => s.ruta === '/api/casos/7/imagenes')).toHaveLength(2),
    )
  })

  it('muestra los errores de la API', async () => {
    api(LISTADO, {
      'GET /api/casos/7/imagenes/11/descarga': { estado: 404, cuerpo: { mensaje: 'El enlace venció.' } },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.click(await screen.findByRole('button', { name: 'Descargar el original de frente.jpg' }))

    expect(await within(seccion()).findByText('El enlace venció.')).toBeInTheDocument()
  })
})

describe('sello de tiempo en Hedera (funcionalidades 016 y 023)', () => {
  it('muestra el sello confirmado, en curso o simulado (RF37)', async () => {
    const sellada = { ...IMAGEN, sello: { estado: 'sellado', referencia: 'Hedera testnet · tema 0.0.2002 · mensaje 7', fecha: '2026-10-22T12:00:00', simulado: false, enlace: 'https://hashscan.io/testnet/topic/0.0.2002/message/7' } }
    const enCurso = { ...IMAGEN, id: 2, nombre: 'lateral.jpg', huella: 'b'.repeat(64), sello: { estado: 'enviado', simulado: false } }
    api({ ...LISTADO, imagenes: [sellada, enCurso] })
    renderizarEn('/casos/7')

    expect(await screen.findByText(/Registrada en Hedera el 22\/10\/2026 .*mensaje 7/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Verificar en HashScan' })).toHaveAttribute(
      'href',
      'https://hashscan.io/testnet/topic/0.0.2002/message/7',
    )
    expect(screen.getByText('Sello en Hedera en curso…')).toBeInTheDocument()
  })
})
