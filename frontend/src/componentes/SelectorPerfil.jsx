/**
 * Elección del perfil al registrarse: abogado o aseguradora (RN01).
 *
 * El perfil no cambia después del registro. Lo usan el registro común y el
 * registro con Google (027), que también exige elegirlo la primera vez.
 *
 * Realiza: RF01, RF52 (CA1); RN01; CA1 de la funcionalidad 020.
 */
import OpcionTarjeta from './OpcionTarjeta.jsx'

export default function SelectorPerfil({ valor, onChange, error }) {
  return (
    <fieldset
      className="opciones-tarjeta"
      aria-labelledby="titulo-paso"
      aria-describedby={error ? 'ayuda-perfil error-perfil' : 'ayuda-perfil'}
    >
      <OpcionTarjeta
        nombre="perfil"
        valor="abogado"
        seleccionada={valor === 'abogado'}
        onChange={onChange}
        titulo="Abogado o abogada"
        descripcion="Trabajás de forma individual. Si querés, después podés crear un estudio jurídico e invitar a tu equipo."
      />
      <OpcionTarjeta
        nombre="perfil"
        valor="aseguradora"
        seleccionada={valor === 'aseguradora'}
        onChange={onChange}
        titulo="Registrar mi aseguradora"
        descripcion="Para quien va a administrar la cuenta de la empresa. Tus compañeros se suman por invitación."
      />
      <p id="ayuda-perfil" className="campo__ayuda">
        El perfil no puede cambiarse después del registro.
      </p>
      {error && (
        <p id="error-perfil" className="campo__error">
          {error}
        </p>
      )}
    </fieldset>
  )
}
