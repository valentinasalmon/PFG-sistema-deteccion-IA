/**
 * Búsqueda en el catálogo de aseguradoras de la SSN (funcionalidad 021).
 */

function normalizar(texto) {
  return texto
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
}

/**
 * Aseguradoras cuya denominación contiene el texto buscado (sin distinguir
 * mayúsculas ni tildes) o cuyo CUIT contiene los dígitos buscados (desde 3).
 *
 * @param {Array<{denominacion: string, cuit: string}>} aseguradoras
 * @param {string} busqueda
 */
export function filtrarAseguradoras(aseguradoras, busqueda) {
  const termino = normalizar(busqueda.trim())
  if (!termino) return []
  const digitos = termino.replace(/\D/g, '')
  return aseguradoras.filter(
    (aseguradora) =>
      normalizar(aseguradora.denominacion).includes(termino) ||
      (digitos.length >= 3 && aseguradora.cuit.includes(digitos)),
  )
}
