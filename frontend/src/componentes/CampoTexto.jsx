/**
 * Campo de formulario accesible: etiqueta, control, ayuda y mensaje de error.
 *
 * El error se anuncia a los lectores de pantalla y queda asociado al control
 * con aria-describedby, para que se sepa qué dato corregir (RNF10).
 * ``idDescripcion`` asocia además un elemento externo, como la lista de
 * condiciones de la contraseña.
 */
import { useId } from 'react'

export default function CampoTexto({
  etiqueta,
  nombre,
  error,
  ayuda,
  tipo = 'text',
  opcional = false,
  idDescripcion,
  ...propiedades
}) {
  const id = useId()
  const idAyuda = `${id}-ayuda`
  const idError = `${id}-error`
  const descripciones = [ayuda && idAyuda, idDescripcion, error && idError]
    .filter(Boolean)
    .join(' ')

  return (
    <div className="campo">
      <label htmlFor={id} className="campo__etiqueta">
        {etiqueta}
        {opcional && <span className="campo__opcional"> (opcional)</span>}
      </label>
      <input
        id={id}
        name={nombre}
        type={tipo}
        className={error ? 'campo__control campo__control--error' : 'campo__control'}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={descripciones || undefined}
        {...propiedades}
      />
      {ayuda && (
        <p id={idAyuda} className="campo__ayuda">
          {ayuda}
        </p>
      )}
      {error && (
        <p id={idError} className="campo__error">
          {error}
        </p>
      )}
    </div>
  )
}
