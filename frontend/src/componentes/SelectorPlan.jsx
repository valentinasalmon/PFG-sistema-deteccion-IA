/**
 * Elección del plan de un estudio jurídico o de una aseguradora: Básico o
 * Profesional, con sus límites y el precio (funcionalidad 032, frame 10b).
 *
 * El precio vacío se muestra «A confirmar», hasta que la autora lo defina. Es
 * un grupo de botones de opción nativos con forma de tarjeta: se elige con
 * clic, con toque o con las flechas del teclado.
 *
 * Realiza: RF19, RF20; RNF10.
 */
import { textoDelPrecio } from '../utilidades/planes.js'

function Limites({ plan }) {
  return (
    <ul className="plan-tarjeta__limites">
      <li>
        Hasta <strong>{plan.miembros} miembros</strong>
      </li>
      <li>{plan.analisis_mes} análisis por mes</li>
      <li>{plan.imagenes_por_caso} imágenes por caso</li>
      {plan.almacenamiento_gb && <li>{plan.almacenamiento_gb} GB de almacenamiento</li>}
      <li>Casos compartidos con permisos</li>
    </ul>
  )
}

export default function SelectorPlan({ planes, valor, onChange, error, nombre = 'plan' }) {
  return (
    <fieldset
      className="selector-plan"
      aria-labelledby="titulo-paso"
      aria-describedby={error ? `error-${nombre}` : undefined}
    >
      {planes.map((plan) => {
        const elegido = valor === plan.codigo
        return (
          <label key={plan.codigo} className={`plan-tarjeta${elegido ? ' plan-tarjeta--elegida' : ''}`}>
            <input
              type="radio"
              name={nombre}
              value={plan.codigo}
              checked={elegido}
              onChange={onChange}
              className="plan-tarjeta__control"
            />
            <span className="plan-tarjeta__nombre">{plan.nombre}</span>
            <span className="plan-tarjeta__precio">
              <strong>{textoDelPrecio(plan.precio)}</strong> por mes
            </span>
            <Limites plan={plan} />
          </label>
        )
      })}
      {error && (
        <p id={`error-${nombre}`} className="campo__error">
          {error}
        </p>
      )}
    </fieldset>
  )
}
