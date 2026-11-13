import React from 'react'
import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RegisterPage from './Registro.jsx'

const renderRegister = (props = {}) => {
  const navigate = vi.fn()
  const onRegister = vi.fn().mockResolvedValue({ ok: true })
  const view = render(<RegisterPage navigate={navigate} onRegister={onRegister} {...props}/>)
  const [password, confirmPassword] = screen.getAllByPlaceholderText('••••••••')
  const fill = values => {
    const fields = { nombre: 'Ana Pérez', correo: 'ana@nexo.co', password: 'secreta123', confirmPassword: 'secreta123', ...values }
    fireEvent.change(screen.getByPlaceholderText('Tu nombre y apellido'), { target: { name: 'nombre', value: fields.nombre } })
    fireEvent.change(screen.getByPlaceholderText('nombre@ejemplo.com'), { target: { name: 'correo', value: fields.correo } })
    fireEvent.change(password, { target: { name: 'password', value: fields.password } })
    fireEvent.change(confirmPassword, { target: { name: 'confirmPassword', value: fields.confirmPassword } })
  }
  return {
    ...view,
    navigate,
    onRegister: props.onRegister || onRegister,
    fill,
    agree: () => fireEvent.click(screen.getByRole('checkbox')),
    submit: () => fireEvent.submit(view.container.querySelector('form')),
  }
}

describe('RegisterPage', () => {
  it.each([
    [{ nombre: 'An' }, 'Escribe tu nombre completo (mínimo 3 caracteres).'],
    [{ correo: 'ana@nexo' }, 'Ingresa un correo electrónico válido.'],
    [{ password: 'corta', confirmPassword: 'corta' }, 'La contraseña debe contener al menos 8 caracteres.'],
    [{ confirmPassword: 'otra-clave' }, 'Las contraseñas no coinciden.'],
  ])('valida el formulario %o antes de llamar al backend', (values, message) => {
    const { fill, agree, submit, onRegister } = renderRegister()

    fill(values)
    agree()
    submit()

    expect(screen.getByRole('alert')).toHaveTextContent(message)
    expect(onRegister).not.toHaveBeenCalled()
  })

  it('exige aceptar el envío de datos', () => {
    const { fill, submit, onRegister } = renderRegister()

    fill()
    submit()

    expect(screen.getByRole('alert')).toHaveTextContent('Confirma que autorizas el envío de tus datos')
    expect(onRegister).not.toHaveBeenCalled()
  })

  it('envía el formulario completo cuando todo es válido', async () => {
    const { fill, agree, submit, onRegister } = renderRegister()

    fill()
    agree()
    submit()

    expect(onRegister).toHaveBeenCalledWith({
      nombre: 'Ana Pérez', correo: 'ana@nexo.co', password: 'secreta123', confirmPassword: 'secreta123',
    })
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('limpia el error al escribir en un campo', () => {
    const { fill, submit } = renderRegister()

    submit()
    expect(screen.getByRole('alert')).toBeInTheDocument()

    fill()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('muestra el mensaje del backend si el registro es rechazado', async () => {
    const onRegister = vi.fn().mockResolvedValue({ ok: false, message: 'El correo ya está registrado' })
    const { fill, agree, submit } = renderRegister({ onRegister })

    fill()
    agree()
    submit()

    expect(await screen.findByRole('alert')).toHaveTextContent('El correo ya está registrado')
  })

  it('muestra un error genérico si la petición falla y reactiva el botón', async () => {
    const onRegister = vi.fn().mockRejectedValue(new Error('Network'))
    const { fill, agree, submit } = renderRegister({ onRegister })

    fill()
    agree()
    submit()

    expect(await screen.findByRole('alert')).toHaveTextContent('No fue posible crear la cuenta')
    expect(screen.getByRole('button', { name: /crear mi cuenta/i })).toBeEnabled()
  })

  it('deshabilita el botón mientras crea la cuenta', async () => {
    const onRegister = vi.fn(() => new Promise(() => {}))
    const { fill, agree, submit } = renderRegister({ onRegister })

    fill()
    agree()
    submit()

    expect(await screen.findByRole('button', { name: /creando cuenta/i })).toBeDisabled()
  })

  it('navega al login y al inicio desde los enlaces', async () => {
    const user = userEvent.setup()
    const { navigate } = renderRegister()

    await user.click(screen.getByRole('button', { name: 'Inicia sesión' }))
    await user.click(screen.getByRole('button', { name: /volver al inicio/i }))

    expect(navigate).toHaveBeenNthCalledWith(1, 'login')
    expect(navigate).toHaveBeenNthCalledWith(2, 'dashboard')
  })
})
