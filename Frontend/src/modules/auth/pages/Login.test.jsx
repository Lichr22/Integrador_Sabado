import React from 'react'
import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginPage from './Login.jsx'

const renderLogin = (props = {}) => {
  const navigate = vi.fn()
  const onLogin = vi.fn().mockResolvedValue({ ok: true })
  const view = render(<LoginPage navigate={navigate} onLogin={onLogin} {...props}/>)
  return {
    ...view,
    navigate,
    onLogin: props.onLogin || onLogin,
    email: screen.getByPlaceholderText('nombre@ejemplo.com'),
    password: screen.getByPlaceholderText('••••••••'),
    submit: () => fireEvent.submit(view.container.querySelector('form')),
  }
}

describe('LoginPage', () => {
  it('muestra un error y no llama al backend si el correo no es válido', () => {
    const { email, submit, onLogin } = renderLogin()

    fireEvent.change(email, { target: { name: 'correo', value: 'correo-invalido' } })
    submit()

    expect(screen.getByRole('alert')).toHaveTextContent('Ingresa un correo electrónico válido.')
    expect(onLogin).not.toHaveBeenCalled()
  })

  it('pide la contraseña si está vacía', () => {
    const { email, submit, onLogin } = renderLogin()

    fireEvent.change(email, { target: { name: 'correo', value: 'ana@nexo.co' } })
    submit()

    expect(screen.getByRole('alert')).toHaveTextContent('Escribe tu contraseña.')
    expect(onLogin).not.toHaveBeenCalled()
  })

  it('envía el correo y la contraseña al iniciar sesión', async () => {
    const user = userEvent.setup()
    const { email, password, onLogin } = renderLogin()

    await user.type(email, 'ana@nexo.co')
    await user.type(password, 'secreta')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(onLogin).toHaveBeenCalledWith('ana@nexo.co', 'secreta')
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('muestra el mensaje del backend cuando las credenciales son incorrectas', async () => {
    const user = userEvent.setup()
    const onLogin = vi.fn().mockResolvedValue({ ok: false, message: 'Correo o contraseña incorrectos' })
    const { email, password } = renderLogin({ onLogin })

    await user.type(email, 'ana@nexo.co')
    await user.type(password, 'mala')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Correo o contraseña incorrectos')
  })

  it('muestra un error genérico si la petición falla', async () => {
    const user = userEvent.setup()
    const onLogin = vi.fn().mockRejectedValue(new Error('Network'))
    const { email, password } = renderLogin({ onLogin })

    await user.type(email, 'ana@nexo.co')
    await user.type(password, 'secreta')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('No fue posible validar la cuenta')
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeEnabled()
  })

  it('deshabilita el botón mientras valida', async () => {
    const user = userEvent.setup()
    const onLogin = vi.fn(() => new Promise(() => {}))
    const { email, password } = renderLogin({ onLogin })

    await user.type(email, 'ana@nexo.co')
    await user.type(password, 'secreta')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(screen.getByRole('button', { name: /validando/i })).toBeDisabled()
  })

  it('navega al registro desde el enlace "Regístrate gratis"', async () => {
    const user = userEvent.setup()
    const { navigate } = renderLogin()

    await user.click(screen.getByRole('button', { name: 'Regístrate gratis' }))

    expect(navigate).toHaveBeenCalledWith('registro')
  })

  it('muestra la sesión actual si ya hay una cuenta', () => {
    renderLogin({ account: { nombre: 'Ana Pérez' } })

    expect(screen.getByText('Ana Pérez')).toBeInTheDocument()
  })
})
