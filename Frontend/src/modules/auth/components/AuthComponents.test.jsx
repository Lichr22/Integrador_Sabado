import React from 'react'
import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormError, PasswordInput, emailPattern, fieldChange } from './AuthComponents.jsx'

describe('emailPattern', () => {
  it.each(['ana@nexo.co', 'luis.gomez@empresa.com.co'])('acepta "%s"', email => {
    expect(emailPattern.test(email)).toBe(true)
  })

  it.each(['', 'ana', 'ana@nexo', 'ana @nexo.co', '@nexo.co'])('rechaza "%s"', email => {
    expect(emailPattern.test(email)).toBe(false)
  })
})

describe('fieldChange', () => {
  it('actualiza solo el campo indicado por el name del input', () => {
    const setter = vi.fn()

    fieldChange(setter)({ target: { name: 'correo', value: 'ana@nexo.co' } })

    const update = setter.mock.calls[0][0]
    expect(update({ correo: '', password: 'x' })).toEqual({ correo: 'ana@nexo.co', password: 'x' })
  })
})

describe('FormError', () => {
  it('no muestra nada sin mensaje', () => {
    const { container } = render(<FormError message=""/>)

    expect(container).toBeEmptyDOMElement()
  })

  it('muestra el mensaje como alerta', () => {
    render(<FormError message="Algo salió mal"/>)

    expect(screen.getByRole('alert')).toHaveTextContent('Algo salió mal')
  })
})

describe('PasswordInput', () => {
  it('alterna entre ocultar y mostrar la contraseña', async () => {
    const user = userEvent.setup()
    render(<PasswordInput value="secreta" onChange={() => {}}/>)
    const input = screen.getByPlaceholderText('••••••••')

    expect(input).toHaveAttribute('type', 'password')
    await user.click(screen.getByRole('button', { name: 'Mostrar contraseña' }))
    expect(input).toHaveAttribute('type', 'text')
    await user.click(screen.getByRole('button', { name: 'Ocultar contraseña' }))
    expect(input).toHaveAttribute('type', 'password')
  })
})
