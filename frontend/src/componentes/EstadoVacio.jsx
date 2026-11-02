/**
 * Pantalla o sección sin contenido, con una ilustración de la marca, qué pasó
 * y cómo seguir (funcionalidad 034).
 *
 * Reemplaza los íconos sueltos de los vacíos y los errores: ninguna pantalla
 * queda sin una acción o una salida (CA1).
 *
 * Realiza: CA1 de la funcionalidad 034; RNF10.
 *
 * @param {{Ilustracion: Function, titulo: string, texto?: string,
 *   encabezado?: boolean, children?: React.ReactNode}} props
 *   ``encabezado`` muestra el título como ``h1`` (páginas enteras).
 */
export default function EstadoVacio({ Ilustracion, titulo, texto, encabezado = false, children }) {
  const Titulo = encabezado ? 'h1' : 'p'
  return (
    <div className={`estado-vacio${encabezado ? ' estado-vacio--pagina' : ''}`}>
      <Ilustracion clase="estado-vacio__ilustracion" />
      <Titulo className="estado-vacio__titulo">{titulo}</Titulo>
      {texto && <p>{texto}</p>}
      {children && <div className="estado-vacio__acciones">{children}</div>}
    </div>
  )
}
