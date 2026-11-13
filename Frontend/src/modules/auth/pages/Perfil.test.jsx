import React from 'react'
import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ProfilePage from './Perfil.jsx'
import { account, buildData } from '../../../test/fixtures.js'

const renderProfile = (props = {}) => {
  const handlers = {
    navigate: vi.fn(),
    onSave: vi.fn().mockResolvedValue({ ok: true }),
    onLogout: vi.fn(),
    onView: vi.fn(),
  }
  const data = props.data || buildData()
  const view = render(<ProfilePage account={account} data={data} {...handlers} {...props}/>)
  return {
    ...view,
    ...handlers,
    ...props,
    data,
    nombre: screen.getByLabelText('Nombre completo'),
    correo: screen.getByLabelText('Correo electrónico'),
    submit: () => fireEvent.submit(view.container.querySelector('form')),
  }
}

const statValue = label => screen.getByText(label).previousElementSibling.textContent

describe('ProfilePage', () => {
  it('muestra los datos de la cuenta y las estadísticas de sus inscripciones', () => {
    renderProfile()

    expect(screen.getByRole('heading', { name: /Ana Pérez/ })).toBeInTheDocument()
    expect(screen.getByText('AP')).toBeInTheDocument()
    expect(screen.getByText('Administrador')).toBeInTheDocument()
    expect(statValue('Retos en los que participas')).toBe('1')
    expect(statValue('Inscripciones realizadas')).toBe('1')
    expect(statValue('Inscripciones aprobadas')).toBe('1')
  })

  it('los campos están bloqueados hasta pulsar "Editar perfil"', async () => {
    const user = userEvent.setup()
    const { nombre, correo } = renderProfile()

    expect(nombre).toBeDisabled()
    expect(correo).toBeDisabled()
    await user.click(screen.getByRole('button', { name: /editar perfil/i }))

    expect(nombre).toBeEnabled()
    expect(correo).toBeEnabled()
    expect(screen.getByText('Editando')).toBeInTheDocument()
  })

  it('guarda los cambios válidos y sale del modo edición', async () => {
    const user = userEvent.setup()
    const { nombre, onSave } = renderProfile()

    await user.click(screen.getByRole('button', { name: /editar perfil/i }))
    await user.clear(nombre)
    await user.type(nombre, 'Ana María Pérez')
    await user.click(screen.getByRole('button', { name: /guardar cambios/i }))

    expect(onSave).toHaveBeenCalledWith({ nombre: 'Ana María Pérez', correo: 'ana@nexo.co' })
    expect(nombre).toBeDisabled()
  })

  it.each([
    ['nombre', 'An', 'El nombre debe tener al menos 3 caracteres.'],
    ['correo', 'ana@', 'Ingresa un correo electrónico válido.'],
  ])('valida el campo %s', async (field, value, message) => {
    const user = userEvent.setup()
    const view = renderProfile()

    await user.click(screen.getByRole('button', { name: /editar perfil/i }))
    fireEvent.change(view[field], { target: { name: field, value } })
    view.submit()

    expect(screen.getByRole('alert')).toHaveTextContent(message)
    expect(view.onSave).not.toHaveBeenCalled()
  })

  it('muestra el error del backend y se mantiene en edición', async () => {
    const user = userEvent.setup()
    const { nombre } = renderProfile({ onSave: vi.fn().mockResolvedValue({ ok: false, message: 'Correo en uso' }) })

    await user.click(screen.getByRole('button', { name: /editar perfil/i }))
    await user.click(screen.getByRole('button', { name: /guardar cambios/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Correo en uso')
    expect(nombre).toBeEnabled()
  })

  it('al cancelar restaura los valores originales', async () => {
    const user = userEvent.setup()
    const { nombre } = renderProfile()

    await user.click(screen.getByRole('button', { name: /editar perfil/i }))
    await user.clear(nombre)
    await user.type(nombre, 'Otro nombre')
    const [, footerCancel] = screen.getAllByRole('button', { name: /cancelar/i })
    await user.click(footerCancel)

    expect(nombre).toHaveValue('Ana Pérez')
    expect(nombre).toBeDisabled()
  })

  it('abre el detalle del reto desde "Mis inscripciones"', async () => {
    const user = userEvent.setup()
    const { onView, data } = renderProfile()

    await user.click(screen.getByRole('button', { name: /Reducir tiempos de entrega/ }))

    expect(onView).toHaveBeenCalledWith(data.retos[0])
  })

  it('sin inscripciones invita a explorar retos', async () => {
    const user = userEvent.setup()
    const { navigate } = renderProfile({ data: { ...buildData(), registros: [] } })

    expect(screen.getByText('Aún no tienes inscripciones')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /explorar retos/i }))

    expect(navigate).toHaveBeenCalledWith('retos')
  })

  it('cierra sesión con el botón "Cerrar sesión"', async () => {
    const user = userEvent.setup()
    const { onLogout } = renderProfile()

    await user.click(screen.getByRole('button', { name: /cerrar sesión/i }))

    expect(onLogout).toHaveBeenCalledOnce()
  })
})
