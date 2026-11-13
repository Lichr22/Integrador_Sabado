import { describe, expect, it } from 'vitest'
import { entityConfig, navItems } from './data.js'

const entities = Object.entries(entityConfig)

describe('navItems', () => {
  it('cada opción del menú, salvo el resumen, tiene configuración de entidad', () => {
    const ids = navItems.map(item => item.id)

    expect(ids[0]).toBe('dashboard')
    expect(ids.slice(1).sort()).toEqual(Object.keys(entityConfig).sort())
  })

  it('los IDs del menú no se repiten', () => {
    const ids = navItems.map(item => item.id)

    expect(new Set(ids).size).toBe(ids.length)
  })
})

describe('entityConfig', () => {
  it.each(entities)('%s tiene título, singular, columnas y campos', (_, cfg) => {
    expect(cfg.title).toBeTruthy()
    expect(cfg.singular).toBeTruthy()
    expect(cfg.columns.length).toBeGreaterThan(0)
    expect(cfg.fields.length).toBeGreaterThan(0)
  })

  it.each(entities)('las relaciones de %s apuntan a entidades existentes', (_, cfg) => {
    const sources = [
      ...cfg.columns.filter(col => col.relation).map(col => col.relation),
      ...cfg.fields.filter(field => field.type === 'relation').map(field => field.source),
    ]

    sources.forEach(source => expect(entityConfig).toHaveProperty(source))
  })

  it.each(entities)('los campos select de %s tienen opciones', (_, cfg) => {
    cfg.fields.filter(field => field.type === 'select').forEach(field => {
      expect(field.options.length).toBeGreaterThan(0)
    })
  })

  it.each(entities)('los nombres de campos y columnas de %s no se repiten', (_, cfg) => {
    const fields = cfg.fields.map(field => field.name)
    const columns = cfg.columns.map(col => col.field)

    expect(new Set(fields).size).toBe(fields.length)
    expect(new Set(columns).size).toBe(columns.length)
  })

  it('los estados coinciden con los que entiende la API', () => {
    const options = type => entityConfig[type].fields.find(field => field.name === 'estado').options

    expect(options('empresas')).toEqual(['Activa', 'Inactiva'])
    expect(options('usuarios')).toEqual(['Activo', 'Inactivo'])
    expect(options('retos')).toEqual(['Abierto', 'En revisión', 'Cerrado'])
    expect(options('registros')).toEqual(['Pendiente', 'Aprobado', 'Rechazado'])
  })
})
