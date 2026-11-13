import React from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './PlatformApp.jsx'
import * as api from '../services/platformApi.js'
import { account, buildData } from '../../../test/fixtures.js'

vi.mock('../services/platformApi.js', () => ({
  clearSession: vi.fn(),
  createRecord: vi.fn(),
  deleteRecord: vi.fn(),
  getCurrentUser: vi.fn(),
  hasSession: vi.fn(),
  loadPlatformData: vi.fn(),
  loadPublicDashboard: vi.fn(),
  login: vi.fn(),
  register: vi.fn(),
  saveSession: vi.fn(),
  updateCurrentUser: vi.fn(),
  updateRecord: vi.fn(),
}))

beforeEach(() => {
  window.location.hash = ''
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {})
  api.hasSession.mockReturnValue(false)
  api.getCurrentUser.mockResolvedValue(account)
  api.loadPlatformData.mockResolvedValue(buildData())
  api.loadPublicDashboard.mockResolvedValue(buildData())
  api.login.mockResolvedValue({ token: 'token-123', user: account })
  api.register.mockResolvedValue({ token: 'token-123', user: account })
  api.createRecord.mockResolvedValue({})
  api.updateRecord.mockResolvedValue({})
  api.deleteRecord.mockResolvedValue(null)
  api.updateCurrentUser.mockResolvedValue(account)
})

const renderAt = async (hash, { loggedIn = false } = {}) => {
  window.location.hash = hash
  api.hasSession.mockReturnValue(loggedIn)
  const user = userEvent.setup()
  render(<App/>)
  await waitFor(() => expect(screen.queryByText('Verificando sesión...')).not.toBeInTheDocument())
  return user
}

const toast = () => screen.findByRole('status')
const dialog = () => screen.getByRole('dialog')
const sidebarButton = name => within(screen.getByRole('navigation', { name: 'Navegación principal' })).getByRole('button', { name })

describe('PlatformApp · visitante', () => {
  it('muestra el resumen público con los módulos bloqueados', async () => {
    await renderAt('')

    expect(await screen.findByText(/Inicia sesión para habilitar la gestión/)).toBeInTheDocument()
    expect(api.loadPublicDashboard).toHaveBeenCalled()
    expect(api.loadPlatformData).not.toHaveBeenCalled()
    expect(sidebarButton('Resumen')).toBeEnabled()
    expect(sidebarButton('Retos')).toBeDisabled()
    expect(sidebarButton('Empresas')).toBeDisabled()
    expect(screen.getByRole('textbox', { name: 'Buscar retos globalmente' })).toBeDisabled()
  })

  it('redirige al login si intenta abrir un módulo protegido', async () => {
    await renderAt('#empresas')

    expect(await screen.findByRole('heading', { name: '¡Qué bueno verte de nuevo!' })).toBeInTheDocument()
    expect(window.location.hash).toBe('#login')
  })

  it('una página desconocida lleva al resumen', async () => {
    await renderAt('#no-existe')

    await waitFor(() => expect(window.location.hash).toBe('#dashboard'))
  })

  it('muestra el error si el resumen público no carga', async () => {
    api.loadPublicDashboard.mockRejectedValue(new Error('Sin conexión'))
    await renderAt('')

    expect(await screen.findByText('No se pudieron cargar los datos')).toBeInTheDocument()
    expect(screen.getByText('Sin conexión')).toBeInTheDocument()
  })

  it('muestra la página "Sobre el proyecto"', async () => {
    await renderAt('#acerca')

    expect(screen.getByRole('heading', { name: 'Sobre Nexo' })).toBeInTheDocument()
    expect(screen.getByText(/Inicia sesión para consultar los datos/)).toBeInTheDocument()
  })
})

describe('PlatformApp · autenticación', () => {
  it('inicia sesión, guarda el token y abre el perfil', async () => {
    const user = await renderAt('#login')

    await user.type(screen.getByPlaceholderText('nombre@ejemplo.com'), 'ana@nexo.co')
    await user.type(screen.getByPlaceholderText('••••••••'), 'secreta')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(api.login).toHaveBeenCalledWith({ correo: 'ana@nexo.co', password: 'secreta' })
    expect(api.saveSession).toHaveBeenCalledWith('token-123')
    expect(await screen.findByRole('heading', { name: 'Mi perfil' })).toBeInTheDocument()
    expect(window.location.hash).toBe('#perfil')
    expect(await toast()).toHaveTextContent('¡Bienvenido, Ana!')
    expect(api.loadPlatformData).toHaveBeenCalled()
  })

  it('muestra el error del backend si el login falla', async () => {
    api.login.mockRejectedValue(new Error('Correo o contraseña incorrectos'))
    const user = await renderAt('#login')

    await user.type(screen.getByPlaceholderText('nombre@ejemplo.com'), 'ana@nexo.co')
    await user.type(screen.getByPlaceholderText('••••••••'), 'mala')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Correo o contraseña incorrectos')
    expect(api.saveSession).not.toHaveBeenCalled()
  })

  it('registra una cuenta y lleva al resumen', async () => {
    const user = await renderAt('#registro')

    await user.type(screen.getByPlaceholderText('Tu nombre y apellido'), 'Ana Pérez')
    await user.type(screen.getByPlaceholderText('nombre@ejemplo.com'), 'ana@nexo.co')
    const [password, confirm] = screen.getAllByPlaceholderText('••••••••')
    await user.type(password, 'secreta123')
    await user.type(confirm, 'secreta123')
    await user.click(screen.getByRole('checkbox'))
    await user.click(screen.getByRole('button', { name: /crear mi cuenta/i }))

    expect(api.register).toHaveBeenCalledWith(expect.objectContaining({ nombre: 'Ana Pérez', correo: 'ana@nexo.co' }))
    expect(api.saveSession).toHaveBeenCalledWith('token-123')
    expect(await toast()).toHaveTextContent('Cuenta creada correctamente.')
    await waitFor(() => expect(window.location.hash).toBe('#dashboard'))
  })

  it('restaura la sesión guardada y abre el módulo solicitado', async () => {
    await renderAt('#retos', { loggedIn: true })

    expect(await screen.findByRole('heading', { name: 'Retos empresariales' })).toBeInTheDocument()
    expect(api.getCurrentUser).toHaveBeenCalled()
    expect(sidebarButton('Empresas')).toBeEnabled()
  })

  it('un usuario autenticado que abre #login va a su perfil', async () => {
    await renderAt('#login', { loggedIn: true })

    expect(await screen.findByRole('heading', { name: 'Mi perfil' })).toBeInTheDocument()
  })

  it('si la sesión guardada no es válida la elimina y avisa', async () => {
    api.getCurrentUser.mockRejectedValue(new Error('Token vencido'))
    await renderAt('#retos', { loggedIn: true })

    expect(api.clearSession).toHaveBeenCalled()
    expect(await toast()).toHaveTextContent('No se pudo restaurar la sesión: Token vencido')
    expect(window.location.hash).toBe('#login')
  })

  it('cierra la sesión desde el menú de cuenta', async () => {
    const user = await renderAt('#retos', { loggedIn: true })
    await screen.findByRole('heading', { name: 'Retos empresariales' })

    await user.click(screen.getByRole('button', { name: 'Abrir menú de cuenta' }))
    await user.click(screen.getByRole('menuitem', { name: /cerrar sesión/i }))

    expect(api.clearSession).toHaveBeenCalled()
    expect(await screen.findByRole('heading', { name: '¡Qué bueno verte de nuevo!' })).toBeInTheDocument()
    expect(await toast()).toHaveTextContent('Sesión cerrada.')
  })

  it('vuelve al login cuando la API avisa que la sesión expiró', async () => {
    await renderAt('#retos', { loggedIn: true })
    await screen.findByRole('heading', { name: 'Retos empresariales' })

    act(() => window.dispatchEvent(new Event('api-session-expired')))

    expect(await screen.findByRole('heading', { name: '¡Qué bueno verte de nuevo!' })).toBeInTheDocument()
    expect(await toast()).toHaveTextContent('La sesión expiró. Inicia sesión nuevamente.')
  })

  it('un 401 al cargar los datos cierra la sesión', async () => {
    api.loadPlatformData.mockRejectedValue(Object.assign(new Error('No autorizado'), { status: 401 }))
    await renderAt('#retos', { loggedIn: true })

    await waitFor(() => expect(api.clearSession).toHaveBeenCalled())
    expect(await screen.findByRole('heading', { name: '¡Qué bueno verte de nuevo!' })).toBeInTheDocument()
  })

  it('permite reintentar si los datos no cargan', async () => {
    api.loadPlatformData.mockRejectedValueOnce(Object.assign(new Error('Servidor caído'), { status: 500 }))
    const user = await renderAt('#retos', { loggedIn: true })

    expect(await screen.findByText('Servidor caído')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Reintentar' }))

    expect(await screen.findByRole('heading', { name: 'Retos empresariales' })).toBeInTheDocument()
  })

  it('actualiza el perfil del usuario', async () => {
    api.updateCurrentUser.mockResolvedValue({ ...account, nombre: 'Ana María Pérez' })
    const user = await renderAt('#perfil', { loggedIn: true })
    await screen.findByRole('heading', { name: 'Mi perfil' })

    await user.click(screen.getByRole('button', { name: /editar perfil/i }))
    const nombre = screen.getByLabelText('Nombre completo')
    await user.clear(nombre)
    await user.type(nombre, 'Ana María Pérez')
    await user.click(screen.getByRole('button', { name: /guardar cambios/i }))

    expect(api.updateCurrentUser).toHaveBeenCalledWith({ id: 'u1', nombre: 'Ana María Pérez', correo: 'ana@nexo.co' })
    expect(await toast()).toHaveTextContent('Perfil actualizado correctamente.')
    expect(screen.getByRole('heading', { name: /Ana María Pérez/ })).toBeInTheDocument()
  })
})

describe('PlatformApp · gestión de registros', () => {
  const openModule = async (hash, heading) => {
    const user = await renderAt(hash, { loggedIn: true })
    await screen.findByRole('heading', { name: heading })
    return user
  }

  it('crea una empresa con los datos del formulario', async () => {
    const user = await openModule('#empresas', 'Empresas')

    await user.click(screen.getByRole('button', { name: /nuevo empresa/i }))
    const modal = within(dialog())
    await user.type(modal.getByLabelText(/Nombre de la empresa/), 'Gamma')
    await user.type(modal.getByLabelText(/^NIT/), '901')
    await user.type(modal.getByLabelText(/^Sector/), 'Salud')
    await user.type(modal.getByLabelText(/Persona de contacto/), 'Eva')
    await user.type(modal.getByLabelText(/Correo de contacto/), 'gamma@salud.co')
    await user.click(modal.getByRole('button', { name: /crear registro/i }))

    expect(api.createRecord).toHaveBeenCalledWith('empresas', {
      nombre: 'Gamma', nit: '901', sector: 'Salud', contacto: 'Eva', telefono: '', correo: 'gamma@salud.co', estado: 'Activa',
    })
    expect(await toast()).toHaveTextContent('Empresa creado correctamente.')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(api.loadPlatformData).toHaveBeenCalledTimes(2)
  })

  it('indica el primer campo obligatorio vacío', async () => {
    const user = await openModule('#empresas', 'Empresas')

    await user.click(screen.getByRole('button', { name: /nuevo empresa/i }))
    fireEvent.submit(dialog().querySelector('form'))

    expect(within(dialog()).getByRole('alert')).toHaveTextContent('Completa el campo «Nombre de la empresa».')
    expect(api.createRecord).not.toHaveBeenCalled()
  })

  it('rechaza un usuario con correo ya registrado', async () => {
    const user = await openModule('#usuarios', 'Usuarios')

    await user.click(screen.getByRole('button', { name: /nuevo usuario/i }))
    const modal = within(dialog())
    await user.type(modal.getByLabelText(/Nombre completo/), 'Ana Duplicada')
    await user.type(modal.getByLabelText(/Correo electrónico/), 'ANA@nexo.co')
    await user.click(modal.getByRole('button', { name: /crear registro/i }))

    expect(modal.getByRole('alert')).toHaveTextContent('Ese correo ya está registrado.')
    expect(api.createRecord).not.toHaveBeenCalled()
  })

  it('rechaza un reto cuya fecha de cierre es anterior al inicio', async () => {
    const user = await openModule('#retos', 'Retos empresariales')

    await user.click(screen.getByRole('button', { name: /nuevo reto/i }))
    const modal = within(dialog())
    await user.type(modal.getByLabelText(/Nombre del reto/), 'Nuevo reto')
    await user.type(modal.getByLabelText(/Descripción/), 'Algo')
    await user.selectOptions(modal.getByLabelText(/^Empresa/), 'e1')
    await user.selectOptions(modal.getByLabelText(/^Categoría/), 'c1')
    await user.selectOptions(modal.getByLabelText(/^Prioridad/), 'p1')
    fireEvent.change(modal.getByLabelText(/Fecha de inicio/), { target: { value: '2026-05-10' } })
    fireEvent.change(modal.getByLabelText(/Fecha de cierre/), { target: { value: '2026-05-01' } })
    await user.click(modal.getByRole('button', { name: /crear registro/i }))

    expect(modal.getByRole('alert')).toHaveTextContent('La fecha de cierre no puede ser anterior a la fecha de inicio.')
    expect(api.createRecord).not.toHaveBeenCalled()
  })

  it('edita un registro existente con PUT y conserva su ID', async () => {
    const user = await openModule('#empresas', 'Empresas')

    await user.click(screen.getByRole('button', { name: 'Editar Acme' }))
    const modal = within(dialog())
    const nombre = modal.getByLabelText(/Nombre de la empresa/)
    expect(nombre).toHaveValue('Acme')
    await user.clear(nombre)
    await user.type(nombre, 'Acme SAS')
    await user.click(modal.getByRole('button', { name: /guardar cambios/i }))

    expect(api.updateRecord).toHaveBeenCalledWith('empresas', expect.objectContaining({ id: 'e1', nombre: 'Acme SAS' }))
    expect(await toast()).toHaveTextContent('Empresa actualizado correctamente.')
  })

  it('muestra en el formulario el error devuelto por la API', async () => {
    api.updateRecord.mockRejectedValue(new Error('El NIT ya existe'))
    const user = await openModule('#empresas', 'Empresas')

    await user.click(screen.getByRole('button', { name: 'Editar Acme' }))
    await user.click(within(dialog()).getByRole('button', { name: /guardar cambios/i }))

    expect(await within(dialog()).findByRole('alert')).toHaveTextContent('El NIT ya existe')
  })

  it('cierra el formulario con Escape o con "Cancelar"', async () => {
    const user = await openModule('#categorias', 'Categorías')

    await user.click(screen.getByRole('button', { name: /nuevo categoría/i }))
    await user.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /nuevo categoría/i }))
    await user.click(within(dialog()).getByRole('button', { name: 'Cancelar' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('no permite eliminar una empresa con retos relacionados', async () => {
    const user = await openModule('#empresas', 'Empresas')

    await user.click(screen.getByRole('button', { name: 'Eliminar Acme' }))
    const modal = within(dialog())

    expect(modal.getByText('Este registro está en uso')).toBeInTheDocument()
    expect(modal.getByText(/2 retos relacionados/)).toBeInTheDocument()
    expect(modal.queryByRole('button', { name: 'Eliminar' })).not.toBeInTheDocument()
  })

  it('elimina una categoría sin dependencias', async () => {
    const user = await openModule('#categorias', 'Categorías')

    await user.click(screen.getByRole('button', { name: 'Eliminar Finanzas' }))
    await user.click(within(dialog()).getByRole('button', { name: 'Eliminar' }))

    expect(api.deleteRecord).toHaveBeenCalledWith('categorias', 'c2')
    expect(await toast()).toHaveTextContent('Registro eliminado correctamente.')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('avisa si la API no permite eliminar', async () => {
    api.deleteRecord.mockRejectedValue(new Error('No se pudo eliminar'))
    const user = await openModule('#categorias', 'Categorías')

    await user.click(screen.getByRole('button', { name: 'Eliminar Finanzas' }))
    await user.click(within(dialog()).getByRole('button', { name: 'Eliminar' }))

    expect(await toast()).toHaveTextContent('No se pudo eliminar')
  })

  it('al eliminar la propia cuenta cierra la sesión', async () => {
    const data = buildData()
    data.registros = data.registros.filter(reg => reg.usuarioId !== 'u1')
    api.loadPlatformData.mockResolvedValue(data)
    const user = await openModule('#usuarios', 'Usuarios')

    await user.click(screen.getByRole('button', { name: 'Eliminar Ana Pérez' }))
    await user.click(within(dialog()).getByRole('button', { name: 'Eliminar' }))

    expect(api.deleteRecord).toHaveBeenCalledWith('usuarios', 'u1')
    expect(api.clearSession).toHaveBeenCalled()
    expect(await screen.findByRole('heading', { name: '¡Qué bueno verte de nuevo!' })).toBeInTheDocument()
  })

  it('muestra el detalle de un reto e inscribe usuarios desde él', async () => {
    const user = await openModule('#retos', 'Retos empresariales')

    await user.click(screen.getByRole('button', { name: 'Reducir tiempos de entrega' }))
    let modal = within(dialog())
    expect(modal.getByText('DETALLE DEL RETO')).toBeInTheDocument()
    expect(modal.getByText('Presentado por Acme')).toBeInTheDocument()
    expect(modal.getByText('2 inscritos')).toBeInTheDocument()
    expect(modal.getByText('Luis Gómez')).toBeInTheDocument()

    await user.click(modal.getByRole('button', { name: /inscribir usuario/i }))
    modal = within(dialog())
    expect(modal.getByRole('heading', { name: 'Nuevo registro' })).toBeInTheDocument()
    expect(modal.getByLabelText(/^Reto/)).toHaveValue('r1')
  })

  it('no permite inscribir dos veces al mismo usuario en un reto', async () => {
    const user = await openModule('#registros', 'Registros')

    await user.click(screen.getByRole('button', { name: /nuevo registro/i }))
    const modal = within(dialog())
    await user.selectOptions(modal.getByLabelText(/^Usuario/), 'u1')
    await user.selectOptions(modal.getByLabelText(/^Reto/), 'r1')
    await user.click(modal.getByRole('button', { name: /crear registro/i }))

    expect(modal.getByRole('alert')).toHaveTextContent('Este usuario ya está inscrito en ese reto.')
    expect(api.createRecord).not.toHaveBeenCalled()
  })

  it('la búsqueda global lleva a retos y filtra el listado', async () => {
    const user = await openModule('#empresas', 'Empresas')

    await user.type(screen.getByRole('textbox', { name: 'Buscar retos globalmente' }), 'Bajar')

    expect(await screen.findByRole('heading', { name: 'Retos empresariales' })).toBeInTheDocument()
    expect(screen.getByText('1 registro')).toBeInTheDocument()
  })

  it('navega entre módulos desde la barra lateral', async () => {
    const user = await openModule('#retos', 'Retos empresariales')

    await user.click(sidebarButton('Prioridades'))

    expect(screen.getByRole('heading', { name: 'Prioridades' })).toBeInTheDocument()
    expect(window.location.hash).toBe('#prioridades')
  })
})
