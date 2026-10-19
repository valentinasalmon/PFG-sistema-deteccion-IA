/**
 * Lista de condiciones de la contraseña que se marcan a medida que se cumplen.
 *
 * Realiza: CA4 de la funcionalidad 002 (orientación previa al envío).
 */
import { evaluarContrasenia } from '../utilidades/contrasenia.js'

export default function ReglasContrasenia({ contrasenia, id }) {
  return (
    <ul className="reglas" id={id}>
      {evaluarContrasenia(contrasenia).map(({ id: regla, texto, cumplida }) => (
        <li key={regla} className={cumplida ? 'reglas__item reglas__item--cumplida' : 'reglas__item'}>
          <span aria-hidden="true">{cumplida ? '✓' : '•'}</span> {texto}
          <span className="solo-lectores">{cumplida ? ' (cumplida)' : ' (pendiente)'}</span>
        </li>
      ))}
    </ul>
  )
}
