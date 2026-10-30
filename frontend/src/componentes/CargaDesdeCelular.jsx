/**
 * "Desde tu celular": muestra un código QR de un solo uso para subir fotos
 * desde la galería o la cámara del celular a este caso (funcionalidad 024).
 *
 * Mientras el código está abierto, la lista de imágenes se actualiza sola
 * cada pocos segundos, así las fotos aparecen en la computadora a medida que
 * se suben. Al cerrarlo, el enlace se cancela.
 *
 * Desde la funcionalidad 028 el botón que abre el código está en la tarjeta
 * "Desde tu celular" de la etapa de carga, y el panel con el QR se muestra
 * debajo de las tres opciones: por eso el estado vive en el hook
 * ``useEnlaceCelular``.
 *
 * Realiza: RF53 (CA2).
 */
import Aviso from './Aviso.jsx'

function formatearRestante(segundos) {
  const minutos = Math.floor(segundos / 60)
  return `${minutos}:${String(segundos % 60).padStart(2, '0')}`
}

/** Panel con el código QR, los pasos y el tiempo que le queda al enlace. */
export default function CargaDesdeCelular({ enlace, error, restante, abrir, cerrar }) {
  if (!enlace) return error ? <Aviso tipo="error">{error}</Aviso> : null
  return (
    <section className="panel-carga carga-celular" aria-labelledby="titulo-carga-celular">
      <h3 id="titulo-carga-celular">Cargar desde el celular</h3>
      {restante > 0 ? (
        <div className="carga-celular__contenido">
          <div className="visor carga-celular__qr">
            <img src={enlace.qr} alt="Código QR para cargar fotos desde el celular" />
          </div>
          <ol className="carga-celular__pasos">
            <li>Abrí la cámara del celular y apuntá al código.</li>
            <li>Tocá el enlace que aparece.</li>
            <li>Elegí las fotos de la galería o sacá una en el momento.</li>
          </ol>
          <p className="nota">
            Las fotos aparecen acá a medida que se suben. El código vence en{' '}
            <strong aria-live="off">{formatearRestante(restante)}</strong> y solo sirve para este caso. Podés
            subir todas las fotos que quieras, dentro del límite de tu plan.
          </p>
        </div>
      ) : (
        <Aviso tipo="info">El código venció. Generá uno nuevo para seguir cargando fotos.</Aviso>
      )}
      <div className="acciones-en-linea">
        {restante === 0 && (
          <button type="button" className="boton" onClick={abrir}>
            Generar otro código
          </button>
        )}
        <button type="button" className="boton boton--fantasma" onClick={cerrar}>
          {restante > 0 ? 'Cancelar' : 'Cerrar'}
        </button>
      </div>
    </section>
  )
}
