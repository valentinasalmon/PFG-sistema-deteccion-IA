/**
 * Pantalla "Administración": aseguradoras pendientes de aprobación.
 *
 * Solo para el Administrador de la plataforma. Muestra la denominación, el
 * CUIT y quién registró cada aseguradora, y permite aprobarla o rechazarla
 * con un motivo que se informa por correo. El tablero completo llega con la
 * funcionalidad 014.
 *
 * Realiza: RN37; CA7 a CA9 de la funcionalidad 021.
 */
import { useState } from 'react'
import {
  aprobarAseguradora,
  listarAseguradorasPendientes,
  rechazarAseguradora,
} from '../api/administracion.js'
import Aviso from '../componentes/Aviso.jsx'
import BotonConfirmar from '../componentes/BotonConfirmar.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { formatearFecha } from '../utilidades/fechas.js'

function FormularioRechazo({ aseguradora, alTerminar }) {
  const [motivo, setMotivo] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    if (!motivo.trim()) {
      setError('Indicá el motivo: se lo enviamos por correo a quien la registró.')
      return
    }
    setEnviando(true)
    try {
      const respuesta = await rechazarAseguradora(aseguradora.id, motivo)
      await alTerminar({ tipo: 'exito', texto: respuesta.mensaje })
    } catch (errorApi) {
      setError(errorApi.message)
      setEnviando(false)
    }
  }

  return (
    <form onSubmit={manejarEnvio} className="formulario formulario--compacto" noValidate>
      <CampoTexto
        etiqueta={`Motivo del rechazo de ${aseguradora.nombre}`}
        nombre="motivo"
        value={motivo}
        onChange={(evento) => setMotivo(evento.target.value)}
        error={error}
        required
      />
      <div className="acciones-en-linea">
        <button type="submit" className="boton boton--peligro boton--chico" disabled={enviando}>
          Rechazar la aseguradora
        </button>
        <button
          type="button"
          className="boton boton--secundario boton--chico"
          onClick={() => alTerminar(null)}
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}

function Pendientes() {
  const { datos, error, cargando, recargar } = useDatos(listarAseguradorasPendientes)
  const [aviso, setAviso] = useState(null)
  const [rechazando, setRechazando] = useState(null)

  async function terminar(resultado) {
    setRechazando(null)
    setAviso(resultado)
    if (resultado) await recargar()
  }

  async function aprobar(aseguradora) {
    try {
      const respuesta = await aprobarAseguradora(aseguradora.id)
      await terminar({ tipo: 'exito', texto: respuesta.mensaje })
    } catch (errorApi) {
      setAviso({ tipo: 'error', texto: errorApi.message })
    }
  }

  if (cargando) return <Cargando texto="Cargando las aseguradoras pendientes…" />
  if (error) return <Aviso tipo="error">{error.message}</Aviso>

  return (
    <section className="seccion" aria-labelledby="titulo-pendientes">
      <h2 id="titulo-pendientes">Aseguradoras pendientes de aprobación</h2>
      <p className="nota">
        Antes de aprobar, comprobá que la persona trabaje en la aseguradora (por ejemplo, con el
        dominio de su correo o comunicándote con la empresa).
      </p>
      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
      {datos.length === 0 ? (
        <p className="nota">No hay aseguradoras pendientes.</p>
      ) : (
        <ul className="lista-tarjetas">
          {datos.map((aseguradora) => (
            <li key={aseguradora.id} className="tarjeta-item">
              <div className="tarjeta-item__principal">
                <span className="tarjeta-item__titulo">{aseguradora.nombre}</span>
                <span className="tarjeta-item__detalle">
                  CUIT {aseguradora.cuit} · Registrada el {formatearFecha(aseguradora.creada_en)}
                </span>
                <span className="tarjeta-item__detalle">
                  Por {aseguradora.referente.nombre} ({aseguradora.referente.correo})
                  {!aseguradora.referente.verificado && ' · correo sin verificar'}
                </span>
              </div>
              {rechazando === aseguradora.id ? (
                <FormularioRechazo aseguradora={aseguradora} alTerminar={terminar} />
              ) : (
                <div className="acciones-en-linea">
                  <BotonConfirmar
                    texto="Aprobar"
                    pregunta={`¿Aprobar ${aseguradora.nombre}?`}
                    textoConfirmar="Aprobar"
                    onConfirmar={() => aprobar(aseguradora)}
                  />
                  <button
                    type="button"
                    className="boton boton--secundario-peligro boton--chico"
                    onClick={() => {
                      setAviso(null)
                      setRechazando(aseguradora.id)
                    }}
                    aria-label={`Rechazar ${aseguradora.nombre}`}
                  >
                    Rechazar
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default function PaginaAdministracion() {
  const { usuario } = useSesion()
  return (
    <>
      <h1>Administración</h1>
      {usuario.rol === 'administrador' ? (
        <Pendientes />
      ) : (
        <Aviso tipo="error">Solo el Administrador de la plataforma puede ver esta pantalla.</Aviso>
      )}
    </>
  )
}
