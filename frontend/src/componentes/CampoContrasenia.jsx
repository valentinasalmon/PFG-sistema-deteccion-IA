/**
 * Campo de contraseña con el botón «Mostrar» para ver lo escrito
 * (funcionalidad 028, frame 9a).
 *
 * Ver la contraseña evita errores de tipeo, sobre todo en el celular, sin
 * bajar la seguridad: se oculta de nuevo con el mismo botón. Al lado de la
 * etiqueta puede ir un enlace, por ejemplo «¿La olvidaste?».
 *
 * Realiza: RNF10 (formularios); CA8 de la funcionalidad 002.
 */
import { useId, useState } from 'react'

export default function CampoContrasenia({ etiqueta, nombre, error, ayuda, enlace, ...propiedades }) {
  const id = useId()
  const [visible, setVisible] = useState(false)
  const idAyuda = `${id}-ayuda`
  const idError = `${id}-error`
  const descripciones = [ayuda && idAyuda, error && idError].filter(Boolean).join(' ')

  return (
    <div className="campo">
      <div className="campo__cabecera">
        <label htmlFor={id} className="campo__etiqueta">
          {etiqueta}
        </label>
        {enlace}
      </div>
      <div className="campo-contrasenia">
        <input
          id={id}
          name={nombre}
          type={visible ? 'text' : 'password'}
          className={error ? 'campo__control campo__control--error' : 'campo__control'}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={descripciones || undefined}
          {...propiedades}
        />
        <button
          type="button"
          className="campo-contrasenia__mostrar"
          aria-label={`${visible ? 'Ocultar' : 'Mostrar'} la contraseña`}
          aria-pressed={visible}
          aria-controls={id}
          onClick={() => setVisible(!visible)}
        >
          {visible ? 'Ocultar' : 'Mostrar'}
        </button>
      </div>
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
