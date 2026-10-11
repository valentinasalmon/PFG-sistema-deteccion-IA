/**
 * Pruebas de los componentes de presentación: avisos, campos de formulario,
 * indicador de carga y reglas de contraseña (RNF10 y CA4 de la funcionalidad 002).
 */
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import Aviso from './Aviso.jsx'
import AvisoProvisorio from './AvisoProvisorio.jsx'
import CampoTexto from './CampoTexto.jsx'
import Cargando from './Cargando.jsx'
import ReglasContrasenia from './ReglasContrasenia.jsx'

afterEach(() => {
  cleanup()
})

describe('Aviso', () => {
  it('anuncia los errores de inmediato con role="alert"', () => {
    render(<Aviso tipo="error">Algo salió mal</Aviso>)
    expect(screen.getByRole('alert')).toHaveTextContent('Algo salió mal')
    expect(screen.getByRole('alert')).toHaveClass('aviso--error')
  })

  it('usa role="status" para los avisos informativos y de éxito', () => {
    render(<Aviso tipo="exito">Listo</Aviso>)
    expect(screen.getByRole('status')).toHaveClass('aviso--exito')
  })

  it('por defecto es informativo', () => {
    render(<Aviso>Dato</Aviso>)
    expect(screen.getByRole('status')).toHaveClass('aviso--info')
  })
})

describe('CampoTexto', () => {
  it('asocia la etiqueta con el control', () => {
    render(<CampoTexto etiqueta="Correo electrónico" nombre="correo" tipo="email" />)
    const control = screen.getByLabelText('Correo electrónico')
    expect(control).toHaveAttribute('type', 'email')
    expect(control).toHaveAttribute('name', 'correo')
    expect(control).not.toHaveAttribute('aria-invalid')
  })

  it('marca el error y lo asocia con aria-describedby', () => {
    render(<CampoTexto etiqueta="Nombre" nombre="nombre" error="Este campo es obligatorio." />)
    const control = screen.getByLabelText('Nombre')
    expect(control).toHaveAttribute('aria-invalid', 'true')
    expect(control).toHaveAccessibleDescription('Este campo es obligatorio.')
  })

  it('muestra la ayuda, la marca de opcional y una descripción externa', () => {
    render(
      <>
        <CampoTexto
          etiqueta="Empresa"
          nombre="empresa"
          opcional
          ayuda="Texto de ayuda"
          idDescripcion="externa"
        />
        <p id="externa">Descripción externa</p>
      </>,
    )
    expect(screen.getByText('(opcional)')).toBeInTheDocument()
    expect(screen.getByLabelText(/Empresa/)).toHaveAccessibleDescription(
      'Texto de ayuda Descripción externa',
    )
  })
})

describe('Cargando', () => {
  it('muestra un texto por defecto o el indicado', () => {
    render(<Cargando />)
    expect(screen.getByRole('status')).toHaveTextContent('Cargando…')
    cleanup()
    render(<Cargando texto="Verificando…" />)
    expect(screen.getByRole('status')).toHaveTextContent('Verificando…')
  })
})

describe('ReglasContrasenia', () => {
  it('marca como cumplidas solo las reglas que se cumplen (CA4)', () => {
    render(<ReglasContrasenia contrasenia="abc" id="reglas" />)
    expect(screen.getByText(/Al menos una letra/).closest('li')).toHaveClass('reglas__item--cumplida')
    expect(screen.getByText(/Al menos un número/).closest('li')).not.toHaveClass(
      'reglas__item--cumplida',
    )
    expect(screen.getAllByText(/\(pendiente\)/)).toHaveLength(2)
  })
})

describe('AvisoProvisorio', () => {
  it('muestra la versión vigente de los textos legales', () => {
    render(<AvisoProvisorio />)
    expect(screen.getByText(/Versión 1.0/)).toHaveTextContent('Texto provisorio')
  })
})
