/**
 * Etiqueta breve para destacar un estado o un rol, por ejemplo "Referente".
 *
 * @param {{children: import('react').ReactNode, tipo?: 'destacada' | 'neutra' | 'alerta'}} propiedades
 */
export default function Etiqueta({ children, tipo = 'neutra' }) {
  return <span className={`etiqueta etiqueta--${tipo}`}>{children}</span>
}
