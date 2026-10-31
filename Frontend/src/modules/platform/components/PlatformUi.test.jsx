import React from 'react'
import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Target } from 'lucide-react'
import { Avatar, ChallengeCard, StatCard, StatusBadge } from './PlatformUi.jsx'

describe('StatusBadge', () => {
  it.each([
    ['Abierto', 'green'],
    ['En revisión', 'amber'],
    ['Rechazado', 'rose'],
    ['Desconocido', 'neutral'],
  ])('el estado "%s" usa el color %s', (value, color) => {
    render(<StatusBadge value={value}/>)

    expect(screen.getByText(value)).toHaveClass('status-badge', color)
  })

  it('usa los colores de prioridad cuando priority=true', () => {
    render(<StatusBadge priority value="Baja"/>)

    expect(screen.getByText('Baja')).toHaveClass('blue')
  })

  it('muestra un guion si no hay valor', () => {
    render(<StatusBadge/>)

    expect(screen.getByText('—')).toBeInTheDocument()
  })
})

describe('Avatar', () => {
  it('muestra las iniciales y el nombre completo como título', () => {
    render(<Avatar name="Ana Pérez" index={7}/>)

    const avatar = screen.getByTitle('Ana Pérez')
    expect(avatar).toHaveTextContent('AP')
    expect(avatar).toHaveClass('av-1')
  })
})

describe('StatCard', () => {
  it('muestra el valor con dos dígitos y su etiqueta', () => {
    render(<StatCard icon={Target} label="Retos abiertos" value={4} change="+2" variant="green"/>)

    expect(screen.getByText('04')).toBeInTheDocument()
    expect(screen.getByText('Retos abiertos')).toBeInTheDocument()
  })
})

describe('ChallengeCard', () => {
  const data = {
    empresas: [{ id: 'e1', nombre: 'Acme' }],
    categorias: [{ id: 'c1', nombre: 'Logística' }],
    prioridades: [{ id: 'p1', nombre: 'Alta' }],
  }
  const reto = {
    id: 'r1', nombre: 'Reducir tiempos de entrega', descripcion: 'Optimizar rutas',
    estado: 'Abierto', empresaId: 'e1', categoriaId: 'c1', prioridadId: 'p1', fechaFin: '2026-12-31',
  }

  it('muestra los nombres de empresa, categoría y prioridad relacionadas', () => {
    render(<ChallengeCard reto={reto} data={data} onView={() => {}}/>)

    expect(screen.getByText('Acme')).toBeInTheDocument()
    expect(screen.getByText('Logística')).toBeInTheDocument()
    expect(screen.getByText('Alta')).toHaveClass('rose')
    expect(screen.getByText('Optimizar rutas')).toBeInTheDocument()
  })

  it('abre el detalle desde el título y desde el botón de flecha', async () => {
    const user = userEvent.setup()
    const onView = vi.fn()
    render(<ChallengeCard reto={reto} data={data} onView={onView}/>)

    await user.click(screen.getByRole('button', { name: 'Reducir tiempos de entrega' }))
    await user.click(screen.getByRole('button', { name: 'Ver detalle de Reducir tiempos de entrega' }))

    expect(onView).toHaveBeenCalledTimes(2)
    expect(onView).toHaveBeenCalledWith(reto)
  })
})
