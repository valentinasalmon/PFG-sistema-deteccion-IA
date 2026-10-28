/**
 * Pruebas del panel principal en la pantalla de inicio (funcionalidad 013).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const caso = (id, extra = {}) => ({
  id,
  numero: `CASO-2026-00000${id}`,
  tipo_nombre: 'Laboral',
  estado: 'borrador',
  estado_nombre: 'Borrador',
  actualizado_en: '2026-10-20T15:00:00',
  ...extra,
})
const VACIO = {
  por_estado: {},
  recientes: [],
  analisis_en_curso: [],
  compartidos: [],
  invitaciones: [],
  transferencias: [],
  proximos_a_destruir: [],
  actividad: [],
}
const COMPLETO = {
  por_estado: { borrador: 2, cerrado: 1 },
  recientes: [caso(1), caso(2, { estado: 'cerrado', estado_nombre: 'Cerrado' })],
  analisis_en_curso: [{ id: 9, caso: caso(1), estado: 'en_proceso', cantidad_imagenes: 3 }],
  compartidos: [
    { caso: caso(3), nivel_nombre: 'Lectura', responsable: 'Beto Pérez', otorgado_en: '2026-10-19T12:00:00' },
  ],
  invitaciones: [{ id: 4, invitante: 'Carla Gómez', organizacion: { id: 1, nombre: 'Estudio Pérez' } }],
  transferencias: [{ id: 5, numero: 'CASO-2026-000005', solicitante: { nombre: 'Dani Ruiz' } }],
  proximos_a_destruir: [{ caso: caso(2), vence_en: '2026-11-01T12:00:00' }],
  actividad: [
    { fecha: '2026-10-20T15:00:00', id_caso: 1, numero: 'CASO-2026-000001', texto: 'Ana López cargó la imagen «frente.jpg» en CASO-2026-000001' },
    { fecha: '2026-10-20T14:00:00', id_caso: 1, numero: 'CASO-2026-000001', texto: 'Terminó el análisis de CASO-2026-000001' },
  ],
}

function api(panel) {
  simularApi({ ...CON_SESION, 'GET /api/panel': { cuerpo: { panel } } })
}

describe('panel principal', () => {
  it('muestra la cantidad de casos por estado con enlaces al listado filtrado', async () => {
    api(COMPLETO)
    renderizarEn('/')

    const borradores = await screen.findByRole('link', { name: /2\s*Borrador/ })
    expect(borradores).toHaveAttribute('href', '/casos?estado=borrador')
    expect(screen.getByRole('link', { name: /0\s*En análisis/ })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Nuevo caso' })).toHaveAttribute('href', '/casos/nuevo')
  })

  it('muestra todas las secciones con enlaces a cada caso (CA1, CA3)', async () => {
    api(COMPLETO)
    renderizarEn('/')

    const pendientes = await screen.findByRole('region', { name: 'Pendientes' })
    expect(within(pendientes).getByText(/Carla Gómez te invitó a Estudio Pérez/)).toBeInTheDocument()
    expect(within(pendientes).getByText(/Dani Ruiz quiere transferirte el caso CASO-2026-000005/)).toBeInTheDocument()
    expect(within(pendientes).getByText(/se destruyen el 01\/11\/2026/)).toBeInTheDocument()
    expect(within(pendientes).getAllByRole('link', { name: 'Responder' }).map((e) => e.getAttribute('href'))).toEqual([
      '/organizaciones',
      '/casos',
    ])

    const enCurso = screen.getByRole('region', { name: 'Análisis en curso' })
    expect(within(enCurso).getByRole('link', { name: 'CASO-2026-000001' })).toHaveAttribute('href', '/casos/1')
    expect(within(enCurso).getByText(/3 imagen\(es\), en proceso/)).toBeInTheDocument()

    const compartidos = screen.getByRole('region', { name: 'Compartidos con vos recientemente' })
    expect(within(compartidos).getByText(/Beto Pérez te dio permiso de lectura el 19\/10\/2026/)).toBeInTheDocument()

    const recientes = screen.getByRole('region', { name: 'Casos recientes' })
    expect(within(recientes).getAllByRole('link').map((e) => e.getAttribute('href'))).toEqual([
      '/casos',
      '/casos/1',
      '/casos/2',
    ])

    // Cada contador abre la lista de casos con ese estado (028).
    const contadores = screen.getByRole('list', { name: 'Tus casos por estado' })
    expect(within(contadores).getByRole('link', { name: /2\s*Borrador/ })).toHaveAttribute('href', '/casos?estado=borrador')
  })

  it('muestra la actividad reciente con enlaces a los casos (CA2)', async () => {
    api(COMPLETO)
    renderizarEn('/')

    const actividad = await screen.findByRole('list', { name: 'Actividad reciente de tus casos' })
    // El enlace va solo en el número del caso (028).
    const enlaces = within(actividad).getAllByRole('link', { name: 'CASO-2026-000001' })
    expect(enlaces).toHaveLength(2)
    expect(enlaces[0]).toHaveAttribute('href', '/casos/1')
    expect(enlaces[0].closest('li')).toHaveTextContent('Ana López cargó la imagen «frente.jpg» en CASO-2026-000001')
  })

  it('con el panel vacío solo muestra el resumen de casos', async () => {
    api(VACIO)
    renderizarEn('/')

    expect(await screen.findByText(/Todavía no tenés casos/)).toBeInTheDocument()
    for (const titulo of ['Pendientes', 'Análisis en curso', 'Actividad reciente']) {
      expect(screen.queryByRole('region', { name: titulo })).not.toBeInTheDocument()
    }
  })

  it('muestra 5 eventos y despliega el resto a pedido', async () => {
    const eventos = Array.from({ length: 7 }, (_, i) => ({
      fecha: '2026-10-20T15:00:00',
      id_caso: 1,
      numero: 'CASO-2026-000001',
      accion: 'caso.edicion',
      texto: `Editaste los datos del caso CASO-2026-000001 (${i})`,
    }))
    api({ ...COMPLETO, actividad: eventos })
    const { usuario } = renderizarEn('/')
    const actividad = await screen.findByRole('list', { name: 'Actividad reciente de tus casos' })
    expect(within(actividad).getAllByRole('listitem')).toHaveLength(5)
    await usuario.click(screen.getByRole('button', { name: 'Ver toda la actividad' }))
    expect(within(actividad).getAllByRole('listitem')).toHaveLength(7)
  })

  it('muestra el error si no se puede cargar el panel', async () => {
    simularApi({ ...CON_SESION, 'GET /api/panel': { estado: 500, cuerpo: { mensaje: 'Error del servidor.' } } })
    renderizarEn('/')

    expect(await screen.findByText('Error del servidor.')).toBeInTheDocument()
  })
})
