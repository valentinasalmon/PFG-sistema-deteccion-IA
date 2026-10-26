/**
 * Escala de lectura de los niveles de indicio, la misma del informe PDF.
 *
 * Coincide con las bandas del backend (app/informes/informe_analisis.py) para
 * que la pantalla y el informe digan exactamente lo mismo (RN27, RNF10).
 */
export const BANDAS_DE_INDICIO = [
  { desde: 70, nombre: 'Indicios fuertes', clase: 'fuerte', rango: '70 % a 100 %',
    texto: 'Señales claras de edición o de generación. Requiere revisión profesional.' },
  { desde: 45, nombre: 'Indicios moderados', clase: 'moderado', rango: '45 % a 69 %',
    texto: 'Señales que conviene revisar; pueden tener explicaciones legítimas.' },
  { desde: 1, nombre: 'Indicios débiles', clase: 'debil', rango: '1 % a 44 %',
    texto: 'Señales menores, frecuentes también en imágenes sin editar.' },
  { desde: 0, nombre: 'Sin indicios', clase: 'ninguno', rango: '0 %',
    texto: 'La capa no encontró señales. No garantiza que la imagen no haya sido modificada.' },
]

/** Banda que corresponde a un nivel de 0 a 100. */
export function bandaDeIndicio(nivel) {
  return BANDAS_DE_INDICIO.find((banda) => (nivel ?? 0) >= banda.desde)
}
