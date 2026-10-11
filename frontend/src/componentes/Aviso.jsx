/**
 * Mensaje destacado para informar el resultado de una acción.
 *
 * Los errores usan role="alert" para que el lector de pantalla los lea de
 * inmediato; el resto usa role="status".
 *
 * @param {{tipo?: 'exito' | 'error' | 'info', children: React.ReactNode}} props
 */
export default function Aviso({ tipo = 'info', children }) {
  return (
    <div className={`aviso aviso--${tipo}`} role={tipo === 'error' ? 'alert' : 'status'}>
      {children}
    </div>
  )
}
