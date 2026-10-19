/**
 * Reglas de la política de contraseñas para orientar a la persona mientras
 * escribe. El backend vuelve a validarlas y además controla la lista de
 * contraseñas comunes (RNF01 CA1, CA4 de la funcionalidad 002).
 */

export const LONGITUD_MINIMA = 10
/** bcrypt solo admite 72 bytes; las letras con tilde ocupan 2. */
export const BYTES_MAXIMOS = 72

const codificador = new TextEncoder()

/** Condiciones de la política con su descripción para mostrar. */
export const REGLAS_CONTRASENIA = [
  {
    id: 'longitud',
    texto: `Al menos ${LONGITUD_MINIMA} caracteres`,
    cumple: (c) => c.length >= LONGITUD_MINIMA,
  },
  { id: 'letra', texto: 'Al menos una letra', cumple: (c) => /\p{L}/u.test(c) },
  { id: 'numero', texto: 'Al menos un número', cumple: (c) => /\d/.test(c) },
  {
    id: 'maximo',
    texto: 'Como máximo 72 caracteres',
    cumple: (c) => c.length > 0 && codificador.encode(c).length <= BYTES_MAXIMOS,
  },
]

/**
 * Indica qué reglas cumple una contraseña.
 *
 * @param {string} contrasenia
 * @returns {Array<{id: string, texto: string, cumplida: boolean}>}
 */
export function evaluarContrasenia(contrasenia) {
  return REGLAS_CONTRASENIA.map(({ id, texto, cumple }) => ({
    id,
    texto,
    cumplida: cumple(contrasenia),
  }))
}
