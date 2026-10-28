/**
 * Fila de un caso en una lista (funcionalidad 028).
 *
 * Es la misma en el inicio y en la lista de casos: número (que no se corta),
 * lugar, datos y estado. Toda la fila responde al enlace del número.
 *
 * - Completa (lista de casos): columnas fijas de tipo, espacio y fecha del hecho.
 * - Compacta (inicio): una sola línea de detalle bajo el número.
 *
 * El permiso solo se aclara si el caso fue compartido con la persona: ser
 * Responsable es lo habitual y no necesita etiqueta.
 *
 * Realiza: RF26, RF48 (interfaz); RNF10.
 */
import { Link } from 'react-router'
import { formatearDia, formatearFecha } from '../utilidades/fechas.js'
import EtiquetaEstado from './EtiquetaEstado.jsx'
import Icono from './Icono.jsx'

function Compartido({ caso }) {
  if (!caso.mi_permiso || caso.mi_permiso === 'responsable') return null
  return <span className="fila-caso__permiso">Compartido · {caso.mi_permiso_nombre}</span>
}

export default function FilaCaso({ caso, compacta = false }) {
  const numero = (
    <Link to={`/casos/${caso.id}`} className="fila-caso__numero">
      {caso.numero}
    </Link>
  )
  if (compacta) {
    return (
      <li className="fila-caso fila-caso--compacta">
        <div className="fila-caso__principal">
          {numero}
          <span className="fila-caso__lugar">
            {[caso.lugar, caso.tipo_nombre, `actualizado el ${formatearFecha(caso.actualizado_en)}`]
              .filter(Boolean)
              .join(' · ')}
          </span>
        </div>
        <EtiquetaEstado estado={caso.estado}>{caso.estado_nombre}</EtiquetaEstado>
        <Icono nombre="derecha" tamanio={18} />
      </li>
    )
  }
  return (
    <li className="fila-caso">
      <div className="fila-caso__principal">
        {numero}
        <span className="fila-caso__lugar">
          {caso.lugar}
          {caso.expediente && ` · ${caso.expediente}`}
        </span>
        <Compartido caso={caso} />
      </div>
      <span className="fila-caso__dato" data-titulo="Tipo">
        {caso.tipo_nombre}
      </span>
      <span className="fila-caso__dato" data-titulo="Espacio">
        {caso.espacio?.nombre}
      </span>
      <span className="fila-caso__dato" data-titulo="Hecho">
        {formatearDia(caso.fecha_hecho)}
      </span>
      <EtiquetaEstado estado={caso.estado}>{caso.estado_nombre}</EtiquetaEstado>
      <Icono nombre="derecha" tamanio={18} />
    </li>
  )
}
