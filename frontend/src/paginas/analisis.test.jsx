/**
 * Pruebas de la selección de imágenes, el pedido de análisis, el progreso y
 * los resultados por capa (funcionalidad 007).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

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
const imagen = (id, nombre, analizada = false) => ({
  id,
  nombre,
  formato: 'PNG',
  tamanio: 2048,
  ancho: 64,
  alto: 48,
  huella: String(id).repeat(64).slice(0, 64),
  cargada_en: '2026-10-19T15:00:00',
  cargada_por: 'Ana López',
  en_informe: false,
  analizada,
  miniatura: `/api/archivos/m${id}`,
})
const IMAGENES = {
  imagenes: [imagen(1, 'frente.png', true), imagen(2, 'lateral.png')],
  limite: 20,
  tamanio_maximo: 20 * 1024 * 1024,
  puede_modificar: true,
}
const RESUMEN = {
  id: 5,
  estado: 'finalizado',
  estado_nombre: 'Finalizado',
  en_curso: false,
  solicitante: 'Ana López',
  creado_en: '2026-10-19T15:10:00',
  finalizado_en: '2026-10-19T15:10:05',
  cantidad_imagenes: 1,
  progreso: { imagen_actual: 1, capa_actual: null },
  motivo_falla: null,
}
const RESULTADO = {
  capa: 'metadatos',
  estado: 'completado',
  nivel: 90,
  conclusion: 'Los metadatos presentan indicios fuertes. Se recomienda consultar a un perito especializado.',
  motivo: null,
  version: '1.0 (ExifTool 12.76)',
  detalle: { tabla: [{ campo: 'Software', valor: 'Adobe Photoshop 25.0' }], sin_metadatos: false },
  anomalias: [
    {
      campo: 'Software',
      valor: 'Adobe Photoshop 25.0',
      descripcion: 'El archivo declara procesamiento con «Adobe Photoshop 25.0».',
      severidad: 'directo',
    },
  ],
}
const DETALLE = {
  ...RESUMEN,
  versiones: { metadatos: '1.0 (ExifTool 12.76)' },
  imagenes: [{ id_imagen: 1, nombre: 'frente.png', huella: 'a', integridad: 'verificada', resultados: [RESULTADO] }],
}

function api({ caso = CASO, imagenes = IMAGENES, historial = [], detalle = DETALLE, extra = {} } = {}) {
  const respuesta = (valor, clave) => (typeof valor === 'function' ? () => ({ cuerpo: { [clave]: valor() } }) : { cuerpo: { [clave]: valor } })
  return simularApi({
    ...CON_SESION,
    'GET /api/casos/7': typeof caso === 'function' ? () => ({ cuerpo: { caso: caso(), accesos: [] } }) : { cuerpo: { caso, accesos: [] } },
    'GET /api/casos/7/imagenes': { cuerpo: imagenes },
    'GET /api/casos/7/analisis': respuesta(historial, 'analisis'),
    'GET /api/casos/7/analisis/5': respuesta(detalle, 'analisis'),
    'GET /api/casos/7/informes': { cuerpo: { informes: [] } },
    ...extra,
  })
}

const seccionImagenes = () => screen.getByRole('region', { name: /^Imágenes/ })

describe('pedir el análisis', () => {
  it('elige por defecto las imágenes no analizadas y pide el análisis (CA1)', async () => {
    let estado = 'borrador'
    const { solicitudes } = api({
      caso: () => ({ ...CASO, estado, estado_nombre: estado === 'borrador' ? 'Borrador' : 'En análisis' }),
      extra: {
        'POST /api/casos/7/analisis': () => {
          estado = 'en_analisis'
          return { estado: 202, cuerpo: { analisis: { ...RESUMEN, estado: 'en_cola' }, mensaje: 'En cola.' } }
        },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    const zona = await screen.findByRole('region', { name: /^Imágenes/ })
    const casillas = await within(zona).findAllByRole('checkbox', { name: 'Incluir en el análisis' })
    expect(casillas.map((c) => c.checked)).toEqual([false, true])
    expect(within(zona).getByText('Ya analizada')).toBeInTheDocument()

    await usuario.click(within(zona).getByRole('button', { name: 'Analizar (1)' }))

    expect(solicitudes.find((s) => s.metodo === 'POST').cuerpo).toEqual({ imagenes: [2] })
    expect(await screen.findByText('En análisis')).toBeInTheDocument()
  })

  it('sin imágenes elegidas el botón queda deshabilitado (CA2)', async () => {
    api()
    const { usuario } = renderizarEn('/casos/7')

    await screen.findAllByRole('checkbox', { name: 'Incluir en el análisis' })
    await usuario.click(within(seccionImagenes()).getByRole('button', { name: 'Ninguna' }))
    expect(within(seccionImagenes()).getByRole('button', { name: 'Analizar (0)' })).toBeDisabled()

    await usuario.click(within(seccionImagenes()).getByRole('button', { name: 'Elegir todas' }))
    expect(within(seccionImagenes()).getByRole('button', { name: 'Analizar (2)' })).toBeEnabled()
    await usuario.click(within(seccionImagenes()).getAllByRole('checkbox')[0])
    expect(within(seccionImagenes()).getByText('1 de 2 elegidas')).toBeInTheDocument()
  })

  it('muestra el error del pedido', async () => {
    api({
      extra: {
        'POST /api/casos/7/analisis': {
          estado: 409,
          cuerpo: { mensaje: 'El caso ya tiene un análisis en curso.', codigo: 'analisis_en_curso' },
        },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.click(await screen.findByRole('button', { name: 'Analizar (1)' }))

    expect(await screen.findByText('El caso ya tiene un análisis en curso.')).toBeInTheDocument()
  })

  it('el Lector no elige ni pide análisis', async () => {
    api({ imagenes: { ...IMAGENES, puede_modificar: false } })
    renderizarEn('/casos/7')

    await screen.findByRole('img', { name: 'Vista previa de frente.png' })
    expect(screen.queryByRole('checkbox', { name: 'Incluir en el análisis' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Analizar/ })).not.toBeInTheDocument()
  })
})

describe('progreso y resultados', () => {
  it('muestra el progreso y, al terminar, los resultados sin recargar la página (CA5)', async () => {
    let consultas = 0
    const enCurso = {
      ...DETALLE,
      estado: 'en_proceso',
      estado_nombre: 'En proceso',
      en_curso: true,
      progreso: { imagen_actual: 1, capa_actual: 'Metadatos' },
      imagenes: [],
    }
    api({
      caso: { ...CASO, estado: 'en_analisis', estado_nombre: 'En análisis' },
      historial: [{ ...RESUMEN, estado: 'en_proceso', en_curso: true }],
      detalle: () => {
        consultas += 1
        return consultas === 1 ? enCurso : DETALLE
      },
    })
    renderizarEn('/casos/7')

    expect(await screen.findByText('Analizando la imagen 1 de 1 · capa Metadatos…')).toBeInTheDocument()
    expect(await screen.findByText('90 %', {}, { timeout: 4000 })).toBeInTheDocument()
    expect(consultas).toBeGreaterThanOrEqual(2)
  })

  it('muestra cada capa con nivel, conclusión, hallazgos y metadatos (CA12, CA14)', async () => {
    api({ historial: [RESUMEN] })
    renderizarEn('/casos/7')

    const analisis = await screen.findByRole('region', { name: 'Análisis' })
    expect(await within(analisis).findByRole('heading', { name: 'frente.png' })).toBeInTheDocument()
    expect(within(analisis).getByRole('meter', { name: 'Nivel de indicio' })).toHaveAttribute('value', '90')
    expect(within(analisis).getByText(/Se recomienda consultar a un perito/)).toBeInTheDocument()
    const hallazgos = within(analisis).getByRole('list', { name: 'Hallazgos de la capa Metadatos' })
    expect(within(hallazgos).getByText('Directo')).toBeInTheDocument()
    expect(within(analisis).getByText('Metadatos extraídos')).toBeInTheDocument()
    expect(within(analisis).getByText('Versión: 1.0 (ExifTool 12.76)')).toBeInTheDocument()
    expect(within(analisis).getByText(/no se combinan en un puntaje único/)).toBeInTheDocument()
  })

  it('muestra la capa de credenciales con el estado de la firma (009 CA4, CA7)', async () => {
    const credenciales = {
      capa: 'c2pa',
      estado: 'completado',
      nivel: 100,
      conclusion: 'La imagen tiene credenciales de contenido con firma confiable. Es el indicio más fuerte.',
      motivo: null,
      version: '1.0 (c2pa-python 0.38.0, lista de confianza abc/def)',
      detalle: {
        tabla: [{ campo: 'Firmante', valor: 'OpenAI OpCo, LLC · OpenAI Media Service' }],
        sin_credenciales: false,
        estado_firma: 'confiable',
      },
      anomalias: [{ campo: 'Origen declarado (C2PA)', valor: 'x', descripcion: 'Declaran IA.', severidad: 'directo' }],
    }
    const sinCredenciales = {
      ...credenciales,
      nivel: 0,
      conclusion: 'Sin credenciales de contenido.',
      detalle: { tabla: [], sin_credenciales: true, estado_firma: null },
      anomalias: [],
    }
    api({
      historial: [RESUMEN],
      detalle: {
        ...DETALLE,
        imagenes: [
          { ...DETALLE.imagenes[0], resultados: [RESULTADO, credenciales] },
          { id_imagen: 2, nombre: 'lateral.png', huella: 'b', integridad: 'verificada', resultados: [sinCredenciales] },
        ],
      },
    })
    renderizarEn('/casos/7')

    const analisis = await screen.findByRole('region', { name: 'Análisis' })
    expect(await within(analisis).findByRole('heading', { name: 'Credenciales de contenido (C2PA) Firma confiable' })).toBeInTheDocument()
    expect(within(analisis).getByText('100 %')).toBeInTheDocument()
    expect(within(analisis).getByText('Datos de las credenciales')).toBeInTheDocument()
    expect(within(analisis).getByText('OpenAI OpCo, LLC · OpenAI Media Service')).toBeInTheDocument()
    expect(within(analisis).getByRole('heading', { name: 'Credenciales de contenido (C2PA) Sin credenciales' })).toBeInTheDocument()
    expect(within(analisis).getByText('Sin credenciales de contenido.')).toBeInTheDocument()
  })

  it('marca como alerta una firma que no se pudo confirmar', async () => {
    api({
      historial: [RESUMEN],
      detalle: {
        ...DETALLE,
        imagenes: [{
          ...DETALLE.imagenes[0],
          resultados: [{ ...RESULTADO, capa: 'c2pa', nivel: 55, detalle: { tabla: [], estado_firma: 'contenido_modificado' } }],
        }],
      },
    })
    renderizarEn('/casos/7')

    expect(await screen.findByText('Modificada después de firmarse')).toBeInTheDocument()
  })

  it('informa una capa no disponible y una imagen alterada (CA4, CA13)', async () => {
    api({
      historial: [RESUMEN],
      detalle: {
        ...DETALLE,
        imagenes: [
          { ...DETALLE.imagenes[0], resultados: [{ ...RESULTADO, estado: 'no_disponible', nivel: null, motivo: 'ExifTool no está instalado.' }] },
          { id_imagen: 2, nombre: 'lateral.png', huella: 'b', integridad: 'alterada', resultados: [] },
        ],
      },
    })
    renderizarEn('/casos/7')

    expect(await screen.findByRole('heading', { name: 'Metadatos: no disponible' })).toBeInTheDocument()
    expect(screen.getByText('ExifTool no está instalado.')).toBeInTheDocument()
    expect(screen.getByText(/se excluyó del análisis por una anomalía de integridad/)).toBeInTheDocument()
  })

  it('informa un análisis fallido (CA6)', async () => {
    api({
      historial: [{ ...RESUMEN, estado: 'fallido', estado_nombre: 'Fallido' }],
      detalle: { ...DETALLE, estado: 'fallido', motivo_falla: 'El procesamiento se interrumpió.', imagenes: [] },
    })
    renderizarEn('/casos/7')

    expect(await screen.findByText('El análisis no pudo completarse: El procesamiento se interrumpió.')).toBeInTheDocument()
  })

  it('permite ver un análisis anterior del historial', async () => {
    api({
      historial: [RESUMEN, { ...RESUMEN, id: 4, creado_en: '2026-10-18T10:00:00', cantidad_imagenes: 2 }],
      extra: {
        'GET /api/casos/7/analisis/4': {
          cuerpo: { analisis: { ...DETALLE, id: 4, imagenes: [{ ...DETALLE.imagenes[0], nombre: 'anterior.png' }] } },
        },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    const historial = await screen.findByRole('list', { name: 'Historial de análisis' })
    await usuario.click(within(historial).getByRole('button', { name: /18\/10\/2026 · 2 imagen/ }))

    expect(await screen.findByRole('heading', { name: 'anterior.png' })).toBeInTheDocument()
  })

  it('no muestra la sección si el caso no tiene análisis', async () => {
    api()
    renderizarEn('/casos/7')

    await screen.findByRole('img', { name: 'Vista previa de frente.png' })
    expect(screen.queryByRole('region', { name: 'Análisis' })).not.toBeInTheDocument()
  })

  it('muestra el error del historial', async () => {
    api({ extra: { 'GET /api/casos/7/analisis': { estado: 500, cuerpo: { mensaje: 'Error del servidor.' } } } })
    renderizarEn('/casos/7')

    expect(await screen.findByText('Error del servidor.')).toBeInTheDocument()
  })
})
