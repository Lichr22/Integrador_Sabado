import { describe, expect, it } from 'vitest'
import { displayCount, formatDate, getName, initials } from './formatters.js'

describe('getName', () => {
  const data = { empresas: [{ id: 'e1', nombre: 'Acme' }, { id: 'e2', nombre: 'Globex' }] }

  it('devuelve el nombre de la entidad relacionada por ID', () => {
    expect(getName(data, 'empresas', 'e2')).toBe('Globex')
  })

  it('devuelve "No encontrado" si el ID no existe', () => {
    expect(getName(data, 'empresas', 'x')).toBe('No encontrado')
  })

  it('devuelve "No encontrado" si la colección no está cargada', () => {
    expect(getName(data, 'categorias', 'e1')).toBe('No encontrado')
  })
})

describe('formatDate', () => {
  it('formatea una fecha ISO sin desfase por zona horaria', () => {
    expect(formatDate('2026-03-01')).toMatch(/^01 .+ 2026$/)
  })

  it('muestra un guion cuando no hay fecha', () => {
    expect(formatDate('')).toBe('—')
    expect(formatDate(null)).toBe('—')
  })
})

describe('initials', () => {
  it('toma las iniciales de las dos primeras palabras en mayúscula', () => {
    expect(initials('ana maría pérez')).toBe('AM')
  })

  it('ignora espacios repetidos', () => {
    expect(initials('  Luis   Gómez ')).toBe('LG')
  })

  it('usa "?" cuando no hay nombre', () => {
    expect(initials('')).toBe('?')
    expect(initials(undefined)).toBe('?')
  })
})

describe('displayCount', () => {
  it('completa con cero a la izquierda hasta dos dígitos', () => {
    expect(displayCount(7)).toBe('07')
    expect(displayCount(0)).toBe('00')
  })

  it('no recorta números de más de dos dígitos', () => {
    expect(displayCount(128)).toBe('128')
  })
})
