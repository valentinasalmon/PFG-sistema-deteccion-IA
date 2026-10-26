/**
 * Casilla de aceptación expresa de los Términos de Uso y de la Política de
 * Privacidad, obligatoria para crear una cuenta (RF01 CA2, RNF08).
 *
 * Realiza: RF01 (CA2), RF52 (CA1); RNF08.
 */
import { Link } from 'react-router'

export default function AceptacionTerminos({ aceptado, onChange, error }) {
  return (
    <div className="campo">
      <label className="opcion">
        <input
          type="checkbox"
          name="acepta_terminos"
          checked={aceptado}
          onChange={onChange}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? 'error-terminos' : undefined}
        />
        <span>
          Leí y acepto los{' '}
          <Link to="/terminos" target="_blank" rel="noopener">
            Términos de Uso
          </Link>{' '}
          y la{' '}
          <Link to="/privacidad" target="_blank" rel="noopener">
            Política de Privacidad
          </Link>
          .
        </span>
      </label>
      {error && (
        <p id="error-terminos" className="campo__error">
          {error}
        </p>
      )}
    </div>
  )
}
