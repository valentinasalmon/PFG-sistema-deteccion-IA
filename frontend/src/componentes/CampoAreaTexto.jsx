/**
 * Campo de texto de varias líneas, con la misma estructura accesible que
 * CampoTexto: etiqueta, ayuda y error asociados al control (RNF10).
 */
import { useId } from 'react'

export default function CampoAreaTexto({ etiqueta, nombre, error, ayuda, opcional = false, ...propiedades }) {
  const id = useId()
  const descripciones = [ayuda && `${id}-ayuda`, error && `${id}-error`].filter(Boolean).join(' ')
  return (
    <div className="campo">
      <label htmlFor={id} className="campo__etiqueta">
        {etiqueta}
        {opcional && <span className="campo__opcional"> (opcional)</span>}
      </label>
      <textarea
        id={id}
        name={nombre}
        rows={4}
        className={error ? 'campo__control campo__control--error' : 'campo__control'}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={descripciones || undefined}
        {...propiedades}
      />
      {ayuda && (
        <p id={`${id}-ayuda`} className="campo__ayuda">
          {ayuda}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className="campo__error">
          {error}
        </p>
      )}
    </div>
  )
}
