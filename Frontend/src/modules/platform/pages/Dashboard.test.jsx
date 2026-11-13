import React from 'react'
import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Dashboard from './Dashboard.jsx'
import { buildData, todayKey } from '../../../test/fixtures.js'

const renderDashboard = (props = {}) => {
  const handlers = { navigate: vi.fn(), onView: vi.fn(), onCreate: vi.fn(), onRegister: vi.fn() }
  const data = props.data || buildData()
  const view = render(<Dashboard data={data} {...handlers} {...props}/>)
  return { ...view, ...handlers, data }
}

const statValue = label => screen.getByText(label).closest('.stat-card').querySelector('.stat-value').textContent

const companyAnalysis = {
  estadisticas: {
    totalRetos: 5, retosAbiertos: 3, empresasConRetos: 2, totalEmpresas: 3, empresasSinRetos: 1,
    promedioRetos: 1.6667, medianaRetos: 2, desviacionEstandar: 1.25, maxRetos: 3,
    empresaLider: { nombre: 'Acme' }, retosSinEmpresa: 1, nombresCorregidos: 0, gruposConNombreDuplicado: 0,
  },
  empresas: [
    { empresaId: 'e1', nombre: 'Acme', retos: 3, retosAbiertos: 2, porcentaje: 60 },
    { empresaId: 'e2', nombre: 'Beta Logística', retos: 1, retosAbiertos: 1, porcentaje: 20 },
  ],
}

describe('Dashboard', () => {
  it('calcula los indicadores a partir de los datos cuando no hay resumen público', () => {
    renderDashboard()

    expect(statValue('Empresas aliadas')).toBe('02')
    expect(statValue('Retos abiertos')).toBe('01')
    expect(statValue('Usuarios activos')).toBe('01')
    expect(statValue('Participaciones')).toBe('02')
  })

  it('prioriza los totales del resumen público', () => {
    const data = { ...buildData(), publicSummary: { openChallenges: 7, activeUsers: 12, totalRegistrations: 40 } }
    renderDashboard({ data })

    expect(statValue('Retos abiertos')).toBe('07')
    expect(statValue('Usuarios activos')).toBe('12')
    expect(statValue('Participaciones')).toBe('40')
  })

  it('destaca solo los retos abiertos (máximo 3), sin importar mayúsculas o espacios', () => {
    const data = buildData()
    data.retos = [
      ...data.retos,
      { ...data.retos[0], id: 'r3', nombre: 'Reto tres', estado: ' ABIERTO ' },
      { ...data.retos[0], id: 'r4', nombre: 'Reto cuatro' },
      { ...data.retos[0], id: 'r5', nombre: 'Reto cinco' },
    ]
    const { container } = renderDashboard({ data })

    const titles = [...container.querySelectorAll('.featured-title')].map(node => node.textContent)
    expect(titles).toEqual(['Reducir tiempos de entrega', 'Reto tres', 'Reto cuatro'])
  })

  it('muestra un mensaje si no hay retos abiertos', () => {
    renderDashboard({ data: { ...buildData(), retos: [] } })

    expect(screen.getByText('Aún no hay retos abiertos.')).toBeInTheDocument()
  })

  it('ordena las categorías por cantidad de retos', () => {
    const data = { ...buildData(), publicSummary: { challengeCountsByCategory: { c1: 1, c2: 4 } } }
    const { container } = renderDashboard({ data })

    const labels = [...container.querySelectorAll('.category-label')].map(node => node.textContent)
    expect(labels).toEqual(['Finanzas4', 'Logística1'])
  })

  it('muestra la actividad reciente ordenada por fecha', () => {
    const { container } = renderDashboard()

    const names = [...container.querySelectorAll('.activity-copy strong')].map(node => node.textContent)
    expect(names).toEqual(['Luis Gómez', 'Ana Pérez'])
  })

  it('usa el nombre que trae el registro público si existe', () => {
    const data = buildData()
    data.registros = [{ id: 'g9', usuarioId: 'u99', retoId: 'r99', usuarioNombre: 'Invitada', retoNombre: 'Reto público', fechaRegistro: '2026-10-25', estado: 'Pendiente' }]
    renderDashboard({ data })

    expect(screen.getByText('Invitada')).toBeInTheDocument()
    expect(screen.getByText('Reto público')).toBeInTheDocument()
  })

  it('cuenta las inscripciones de hoy en la participación semanal', () => {
    const data = buildData()
    data.registros.push({ id: 'g3', usuarioId: 'u2', retoId: 'r2', fechaRegistro: todayKey(), estado: 'Pendiente' })
    renderDashboard({ data })

    expect(screen.getByText('1 en total')).toBeInTheDocument()
    expect(screen.getByTitle(`${todayKey()}: 1 registros`)).toBeInTheDocument()
  })

  it('indica cuando el análisis de empresas no está disponible', () => {
    renderDashboard()

    expect(screen.getByText('El análisis de empresas no está disponible en este momento.')).toBeInTheDocument()
  })

  it('muestra el análisis estadístico por empresa', () => {
    const data = { ...buildData(), publicSummary: { companyChallengeAnalysis: companyAnalysis } }
    const { container } = renderDashboard({ data })

    expect(screen.getByText('Acme lidera')).toBeInTheDocument()
    expect(screen.getByText('1,67')).toBeInTheDocument()
    expect(container.querySelectorAll('.company-ranking-row')).toHaveLength(2)
    expect(screen.getByText('2 abiertos · 60%')).toBeInTheDocument()
    expect(screen.getByText('1 abierto · 20%')).toBeInTheDocument()
    expect(screen.getByText(/1 retos no tienen una empresa asignada/)).toBeInTheDocument()
    expect(screen.queryByText(/Limpieza aplicada/)).not.toBeInTheDocument()
  })

  it('informa la limpieza de nombres aplicada en el análisis', () => {
    const analysis = { ...companyAnalysis, estadisticas: { ...companyAnalysis.estadisticas, nombresCorregidos: 2, gruposConNombreDuplicado: 1 } }
    renderDashboard({ data: { ...buildData(), publicSummary: { companyChallengeAnalysis: analysis } } })

    expect(screen.getByText(/Limpieza aplicada al mostrar: 2 nombres/)).toBeInTheDocument()
  })

  it('con sesión permite navegar, ver retos y crear uno nuevo', async () => {
    const user = userEvent.setup()
    const { navigate, onView, onCreate, data } = renderDashboard()

    await user.click(screen.getByRole('button', { name: /explorar retos/i }))
    await user.click(screen.getByRole('button', { name: /ver registros/i }))
    await user.click(screen.getByTitle('Ver reto'))
    await user.click(screen.getByRole('button', { name: /crear un nuevo reto/i }))

    expect(navigate).toHaveBeenNthCalledWith(1, 'retos')
    expect(navigate).toHaveBeenNthCalledWith(2, 'registros')
    expect(onView).toHaveBeenCalledWith(data.retos[0])
    expect(onCreate).toHaveBeenCalledWith('retos')
    expect(screen.getByText(/Datos cargados desde la API/)).toBeInTheDocument()
  })

  it('en modo solo lectura deshabilita las acciones', () => {
    renderDashboard({ readOnly: true })

    expect(screen.getByRole('button', { name: /explorar retos/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /ver todos/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /crear un nuevo reto/i })).toBeDisabled()
    expect(screen.getByTitle('Ver reto')).toBeDisabled()
    expect(screen.getByText(/Inicia sesión para habilitar la gestión/)).toBeInTheDocument()
  })
})
