import React, { useState } from 'react'
import { beforeAll, describe, expect, it, vi } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import EntityPage from './EntityPage.jsx'
import Reto from '../pages/Reto.jsx'
import Empresa from '../pages/Empresa.jsx'
import Categoria from '../pages/Categoria.jsx'
import Prioridad from '../pages/Prioridad.jsx'
import Usuario from '../pages/Usuario.jsx'
import Registro from '../pages/Registro.jsx'
import { buildData } from '../../../test/fixtures.js'

// EntityPage recibe búsqueda, filtro y vista como estado controlado desde PlatformApp.
function Harness({ Page = EntityPage, initialViewMode = 'table', ...props }) {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('')
  const [viewMode, setViewMode] = useState(initialViewMode)
  return <Page search={search} setSearch={setSearch} filter={filter} setFilter={setFilter} viewMode={viewMode} setViewMode={setViewMode} {...props}/>
}

const renderPage = (props = {}) => {
  const handlers = {
    onCreate: vi.fn(), onEdit: vi.fn(), onDelete: vi.fn(), onView: vi.fn(), onRegister: vi.fn(), onNotify: vi.fn(),
  }
  const data = props.data || buildData()
  // Las páginas envoltorio (Reto, Empresa…) fijan su propio type.
  const type = props.Page ? {} : { type: 'retos' }
  render(<Harness {...type} data={data} {...handlers} {...props}/>)
  return { ...handlers, data }
}

const bodyRows = () => screen.getAllByRole('row').slice(1)
const firstCells = () => bodyRows().map(row => within(row).getAllByRole('cell')[0].textContent)

describe('EntityPage', () => {
  it('muestra el título, el conteo y los nombres de las relaciones', () => {
    renderPage()

    expect(screen.getByRole('heading', { name: 'Retos empresariales' })).toBeInTheDocument()
    expect(screen.getByText('2 registros')).toBeInTheDocument()
    const [row] = bodyRows()
    expect(within(row).getByText('Acme')).toBeInTheDocument()
    expect(within(row).getByText('Logística')).toBeInTheDocument()
    expect(within(row).getByText('Alta')).toHaveClass('rose')
  })

  it('busca también por el nombre de las entidades relacionadas', async () => {
    const user = userEvent.setup()
    const data = buildData()
    data.retos[1].empresaId = 'e2'
    renderPage({ data })

    await user.type(screen.getByRole('textbox', { name: 'Buscar retos' }), 'beta log')

    expect(firstCells()).toEqual(['Bajar costos operativos'])
    expect(screen.getByText('1 registro')).toBeInTheDocument()
  })

  it('filtra por estado', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.selectOptions(screen.getByRole('combobox', { name: 'Filtrar por estado' }), 'Cerrado')

    expect(firstCells()).toEqual(['Bajar costos operativos'])
  })

  it('no muestra el filtro de estado en entidades sin estado', () => {
    renderPage({ type: 'categorias' })

    expect(screen.queryByRole('combobox', { name: 'Filtrar por estado' })).not.toBeInTheDocument()
  })

  it('muestra un estado vacío y permite limpiar los filtros', async () => {
    const user = userEvent.setup()
    renderPage()
    const search = screen.getByRole('textbox', { name: 'Buscar retos' })

    await user.type(search, 'no existe')
    expect(screen.getByText('No encontramos resultados')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Limpiar filtros' }))

    expect(search).toHaveValue('')
    expect(bodyRows()).toHaveLength(2)
  })

  it('limpia la búsqueda con el botón X', async () => {
    const user = userEvent.setup()
    renderPage()
    const search = screen.getByRole('textbox', { name: 'Buscar retos' })

    await user.type(search, 'Bajar')
    await user.click(screen.getByRole('button', { name: 'Limpiar búsqueda' }))

    expect(search).toHaveValue('')
  })

  it('ordena ascendente y descendente al pulsar la cabecera', async () => {
    const user = userEvent.setup()
    renderPage()
    const header = screen.getByTitle('Ordenar por Reto')

    await user.click(header)
    expect(firstCells()).toEqual(['Bajar costos operativos', 'Reducir tiempos de entrega'])
    expect(header).toHaveTextContent('↑')

    await user.click(header)
    expect(firstCells()).toEqual(['Reducir tiempos de entrega', 'Bajar costos operativos'])
    expect(header).toHaveTextContent('↓')
  })

  it('ordena numéricamente', async () => {
    const user = userEvent.setup()
    const data = buildData()
    data.prioridades.push({ id: 'p3', nombre: 'Media', nivel: 10, diasMaxRespuesta: 15 })
    renderPage({ type: 'prioridades', data })

    await user.click(screen.getByTitle('Ordenar por Nivel'))

    expect(firstCells()).toEqual(['Alta', 'Baja', 'Media'])
  })

  it('muestra 10 filas y carga 10 más con "Mostrar más"', async () => {
    const user = userEvent.setup()
    const data = buildData()
    data.categorias = Array.from({ length: 12 }, (_, i) => ({ id: `c${i}`, nombre: `Categoría ${i}`, descripcion: '', areaResponsable: '' }))
    renderPage({ type: 'categorias', data })

    expect(bodyRows()).toHaveLength(10)
    expect(screen.getByText('Mostrando 10 de 12 resultados')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /mostrar más/i }))

    expect(bodyRows()).toHaveLength(12)
    expect(screen.getByText('Fin del listado')).toBeInTheDocument()
  })

  it('llama a crear, editar, eliminar y ver con el registro correcto', async () => {
    const user = userEvent.setup()
    const { onCreate, onEdit, onDelete, onView, data } = renderPage()
    const reto = data.retos[0]

    await user.click(screen.getByRole('button', { name: /nuevo reto/i }))
    await user.click(screen.getByRole('button', { name: `Ver ${reto.nombre}` }))
    await user.click(screen.getByRole('button', { name: `Editar ${reto.nombre}` }))
    await user.click(screen.getByRole('button', { name: `Eliminar ${reto.nombre}` }))

    expect(onCreate).toHaveBeenCalledWith('retos')
    expect(onView).toHaveBeenCalledWith(reto)
    expect(onEdit).toHaveBeenCalledWith('retos', reto)
    expect(onDelete).toHaveBeenCalledWith('retos', reto)
  })

  it('solo los retos tienen botón de detalle e inscripción', () => {
    renderPage({ type: 'empresas' })

    expect(screen.queryByRole('button', { name: /^Ver / })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /nueva inscripción/i })).not.toBeInTheDocument()
  })

  it('abre una nueva inscripción desde la cabecera de retos', async () => {
    const user = userEvent.setup()
    const { onRegister } = renderPage()

    await user.click(screen.getByRole('button', { name: /nueva inscripción/i }))

    expect(onRegister).toHaveBeenCalledOnce()
  })

  it('alterna entre la vista de tarjetas y la de tabla', async () => {
    const user = userEvent.setup()
    renderPage({ initialViewMode: 'cards' })

    expect(screen.queryByRole('table')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ver detalle de Reducir tiempos de entrega' })).toBeInTheDocument()

    await user.click(screen.getByTitle('Vista de tabla'))
    expect(screen.getByRole('table')).toBeInTheDocument()

    await user.click(screen.getByTitle('Vista de tarjetas'))
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  describe('exportar CSV', () => {
    let blobs

    beforeAll(() => {
      URL.createObjectURL = blob => { blobs.push(blob); return 'blob:nexo' }
      URL.revokeObjectURL = () => {}
    })

    const readBlob = blob => new Promise(resolve => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result)
      reader.readAsText(blob)
    })

    it('descarga los registros filtrados con los nombres de las relaciones', async () => {
      blobs = []
      const user = userEvent.setup()
      const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
      const { onNotify } = renderPage()

      await user.selectOptions(screen.getByRole('combobox', { name: 'Filtrar por estado' }), 'Abierto')
      await user.click(screen.getByRole('button', { name: /exportar csv/i }))

      expect(click).toHaveBeenCalledOnce()
      expect(click.mock.contexts[0].download).toMatch(/^nexo-retos-\d{4}-\d{2}-\d{2}\.csv$/)
      expect(onNotify).toHaveBeenCalledWith('CSV de retos generado correctamente.')
      const lines = (await readBlob(blobs[0])).replace('﻿', '').split('\r\n')
      expect(lines).toEqual([
        '"Reto";"Empresa";"Categoría";"Prioridad";"Estado";"Cierre"',
        '"Reducir tiempos de entrega";"Acme";"Logística";"Alta";"Abierto";"2026-12-31"',
      ])
    })
  })
})

describe('páginas de entidades', () => {
  it.each([
    [Reto, 'Retos empresariales', 'Nuevo reto'],
    [Empresa, 'Empresas', 'Nuevo empresa'],
    [Categoria, 'Categorías', 'Nuevo categoría'],
    [Prioridad, 'Prioridades', 'Nuevo prioridad'],
    [Usuario, 'Usuarios', 'Nuevo usuario'],
    [Registro, 'Registros', 'Nuevo registro'],
  ])('%o muestra su propia entidad', (Page, title, createLabel) => {
    renderPage({ Page })

    expect(screen.getByRole('heading', { name: title })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: createLabel })).toBeInTheDocument()
  })

  it('Registros muestra el participante y el reto por nombre', () => {
    renderPage({ Page: Registro })

    const [row] = bodyRows()
    expect(within(row).getByText('Ana Pérez')).toBeInTheDocument()
    expect(within(row).getByText('Reducir tiempos de entrega')).toBeInTheDocument()
  })
})
