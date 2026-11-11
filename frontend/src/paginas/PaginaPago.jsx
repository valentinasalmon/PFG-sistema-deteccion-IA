/**
 * Página del enlace de pago del plan (funcionalidad 032).
 *
 * Se abre al crear un estudio desde Mi perfil, al cambiar de plan o al
 * retomar un pago pendiente. No requiere sesión: el enlace es la credencial.
 * Cuando el pago se acredita, muestra cómo sigue según la organización.
 *
 * Realiza: RF20 (CA2); CP-34.
 */
import { useState } from 'react'
import { Link, useParams } from 'react-router'
import PanelPago from '../componentes/PanelPago.jsx'
import ResultadoPago from '../componentes/ResultadoPago.jsx'
import { useSesion } from '../hooks/useSesion.js'

export default function PaginaPago() {
  const { token } = useParams()
  const { usuario } = useSesion()
  const [acreditado, setAcreditado] = useState(null)

  if (acreditado) {
    const idOrganizacion = acreditado.organizacion.id
    return (
      <div className="registro-ancho">
        <ResultadoPago cobro={acreditado}>
          <div className="acciones-en-linea">
            {usuario && idOrganizacion ? (
              <Link to={`/organizaciones/${idOrganizacion}`} className="boton">
                Ir a la organización
              </Link>
            ) : (
              <Link to="/iniciar-sesion" className="boton">
                Iniciar sesión
              </Link>
            )}
          </div>
        </ResultadoPago>
      </div>
    )
  }
  return (
    <div className="registro-ancho">
      <PanelPago token={token} alAcreditar={setAcreditado} />
      {/* 037: con sesión, se puede volver sin pagar todavía; el pago se retoma desde la organización. */}
      {usuario && (
        <p className="enlaces-secundarios">
          <Link to="/organizaciones">Volver a mis organizaciones</Link>
        </p>
      )}
    </div>
  )
}
