/**
 * Paso del registro que pide la institución según el perfil (020, 021 y 027):
 * el colegio de abogados (opcional) o la aseguradora del catálogo de la SSN.
 *
 * Lo usan el registro común y el registro con Google.
 *
 * Realiza: RF01, RF52; RN36.
 */
import { listarAseguradoras } from '../api/cuentas.js'
import { useDatos } from '../hooks/useDatos.js'
import Aviso from './Aviso.jsx'
import Cargando from './Cargando.jsx'
import CampoTexto from './CampoTexto.jsx'
import SelectorAseguradora from './SelectorAseguradora.jsx'

export default function PasoInstitucion({ valores, errores, cambiar, setValores }) {
  const { datos: aseguradoras, error, cargando } = useDatos(listarAseguradoras)

  if (valores.perfil === 'abogado') {
    return (
      <CampoTexto
        etiqueta="Colegio de abogados"
        nombre="colegio"
        opcional
        ayuda="Podés dejarlo vacío y completarlo después desde tu perfil."
        value={valores.colegio}
        onChange={cambiar}
        error={errores.colegio}
      />
    )
  }
  if (cargando) return <Cargando texto="Cargando el listado de aseguradoras…" />
  if (error) return <Aviso tipo="error">{error.message}</Aviso>
  return (
    <>
      <p className="nota">
        El listado es el de la Superintendencia de Seguros de la Nación. Vas a quedar como
        Referente de la aseguradora y el Administrador de la plataforma va a revisar el registro
        antes de que puedas invitar a tu equipo.
      </p>
      <SelectorAseguradora
        aseguradoras={aseguradoras}
        elegida={valores.id_aseguradora}
        onElegir={(id) => setValores((anteriores) => ({ ...anteriores, id_aseguradora: id }))}
        error={errores.id_aseguradora}
      />
    </>
  )
}
