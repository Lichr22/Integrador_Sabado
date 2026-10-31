import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  ApiError, clearSession, createRecord, deleteRecord, hasSession, loadPublicDashboard,
  login, saveSession, updateRecord,
} from './platformApi.js'

const jsonResponse = (body, status = 200) => new Response(JSON.stringify(body), {
  status,
  headers: { 'Content-Type': 'application/json' },
})

let fetchMock

beforeEach(() => {
  fetchMock = vi.fn()
  vi.stubGlobal('fetch', fetchMock)
})

const lastRequest = () => {
  const [url, options] = fetchMock.mock.calls.at(-1)
  return { url, options, body: options.body && JSON.parse(options.body) }
}

describe('sesión', () => {
  it('guarda, detecta y elimina el token en sessionStorage', () => {
    expect(hasSession()).toBe(false)
    saveSession('abc')
    expect(hasSession()).toBe(true)
    clearSession()
    expect(hasSession()).toBe(false)
  })

  it('envía el token como Authorization Bearer cuando hay sesión', async () => {
    saveSession('token-123')
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }))

    await deleteRecord('empresas', 'e1')

    expect(lastRequest().options.headers.get('Authorization')).toBe('Bearer token-123')
  })
})

describe('login', () => {
  it('envía correo y contraseña con los nombres que espera la API', async () => {
    fetchMock.mockResolvedValue(jsonResponse({
      token: 't',
      user: { id: 'u1', nombre: 'Ana', correo: 'ana@nexo.co', rol: 'admin', activo: true, fecha_registro: '2026-10-01T08:30:00' },
    }))

    await login({ correo: 'ana@nexo.co', password: 'secreta' })

    const { url, options, body } = lastRequest()
    expect(url).toBe('/api/auth/login')
    expect(options.method).toBe('POST')
    expect(options.headers.get('Content-Type')).toBe('application/json')
    expect(body).toEqual({ correo: 'ana@nexo.co', contrasena: 'secreta' })
  })

  it('convierte el usuario de la API al formato del frontend', async () => {
    fetchMock.mockResolvedValue(jsonResponse({
      token: 't',
      user: { id: 'u1', nombre: 'Ana', correo: 'ana@nexo.co', rol: 'admin', activo: false, fecha_registro: '2026-10-01T08:30:00' },
    }))

    const result = await login({ correo: 'ana@nexo.co', password: 'x' })

    expect(result.token).toBe('t')
    expect(result.user).toEqual({
      id: 'u1', usuarioId: 'u1', nombre: 'Ana', correo: 'ana@nexo.co',
      rol: 'admin', estado: 'Inactivo', creadoEl: '2026-10-01',
    })
  })

  it('un 401 en el login no se trata como sesión expirada', async () => {
    saveSession('token-anterior')
    const expired = vi.fn()
    window.addEventListener('api-session-expired', expired)
    fetchMock.mockResolvedValue(jsonResponse({ message: 'Credenciales inválidas' }, 401))

    await expect(login({ correo: 'a@b.co', password: 'x' })).rejects.toThrow('Credenciales inválidas')

    expect(expired).not.toHaveBeenCalled()
    expect(hasSession()).toBe(true)
    window.removeEventListener('api-session-expired', expired)
  })
})

describe('manejo de errores', () => {
  it('lanza ApiError con el mensaje y el código de la API', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ message: 'Empresa no encontrada' }, 404))

    const error = await deleteRecord('empresas', 'x').catch(caught => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(404)
    expect(error.message).toBe('Empresa no encontrada')
  })

  it('usa un mensaje genérico si la respuesta no trae JSON', async () => {
    fetchMock.mockResolvedValue(new Response('Internal error', { status: 500 }))

    await expect(deleteRecord('empresas', 'x')).rejects.toThrow('La API respondió con HTTP 500')
  })

  it('un 401 con sesión activa cierra la sesión y emite api-session-expired', async () => {
    saveSession('token-vencido')
    const expired = vi.fn()
    window.addEventListener('api-session-expired', expired)
    fetchMock.mockResolvedValue(jsonResponse({ message: 'La sesión expiró o no es válida' }, 401))

    await expect(deleteRecord('retos', 'r1')).rejects.toBeInstanceOf(ApiError)

    expect(hasSession()).toBe(false)
    expect(expired).toHaveBeenCalledOnce()
    window.removeEventListener('api-session-expired', expired)
  })
})

describe('CRUD de registros', () => {
  it('deleteRecord devuelve null ante un 204 y codifica el ID en la URL', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }))

    await expect(deleteRecord('retos', 'a/b')).resolves.toBeNull()

    expect(lastRequest().url).toBe('/api/retos/a%2Fb')
    expect(lastRequest().options.method).toBe('DELETE')
  })

  it('createRecord convierte un reto a snake_case, sin ID, y la respuesta a camelCase', async () => {
    fetchMock.mockResolvedValue(jsonResponse({
      id: 'r1', nombre: 'Reto', id_empresa: 'e1', id_categoria: 'c1', id_prioridad: 'p1',
      fecha_inicio: '2026-01-01', fecha_fin: '2026-06-30',
    }))

    const result = await createRecord('retos', {
      id: '', nombre: 'Reto', empresaId: 'e1', categoriaId: 'c1', prioridadId: 'p1',
      fechaInicio: '2026-01-01', fechaFin: '2026-06-30',
    })

    expect(lastRequest().body).toEqual({
      nombre: 'Reto', id_empresa: 'e1', id_categoria: 'c1', id_prioridad: 'p1',
      fecha_inicio: '2026-01-01', fecha_fin: '2026-06-30',
    })
    expect(result).toMatchObject({
      id: 'r1', empresaId: 'e1', categoriaId: 'c1', prioridadId: 'p1', fechaFin: '2026-06-30',
    })
  })

  it.each([
    ['Activa', true],
    ['Activo', true],
    ['Inactiva', false],
  ])('createRecord de empresa con estado "%s" envía activa=%s', async (estado, activa) => {
    fetchMock.mockResolvedValue(jsonResponse({ id: 'e1', nombre: 'Acme', activa }))

    const result = await createRecord('empresas', { nombre: 'Acme', estado })

    expect(lastRequest().body).toEqual({ nombre: 'Acme', activa })
    expect(result.estado).toBe(activa ? 'Activa' : 'Inactiva')
  })

  it('updateRecord de usuario usa PUT y no envía la contraseña vacía', async () => {
    fetchMock.mockResolvedValue(jsonResponse({
      id: 'u1', nombre: 'Ana', correo: 'ana@nexo.co', rol: 'admin', activo: true, fecha_registro: '2026-10-01T00:00:00',
    }))

    const result = await updateRecord('usuarios', {
      id: 'u1', nombre: 'Ana', correo: 'ana@nexo.co', rol: 'admin', estado: 'Activo', contrasena: '', fechaRegistro: '2026-10-01',
    })

    const { url, options, body } = lastRequest()
    expect(url).toBe('/api/usuarios/u1')
    expect(options.method).toBe('PUT')
    expect(body).toEqual({
      nombre: 'Ana', correo: 'ana@nexo.co', rol: 'admin', activo: true, fecha_registro: '2026-10-01T00:00:00',
    })
    expect(result).toMatchObject({ estado: 'Activo', fechaRegistro: '2026-10-01' })
  })
})

describe('loadPublicDashboard', () => {
  it('mapea el resumen público y elimina usuarios repetidos', async () => {
    fetchMock.mockResolvedValue(jsonResponse({
      empresas: [{ id: 'e1', nombre: 'Acme' }],
      categorias: [],
      prioridades: [],
      retos: [{ id: 'r1', id_empresa: 'e1', id_categoria: 'c1', id_prioridad: 'p1', fecha_inicio: '2026-01-01', fecha_fin: '2026-02-01' }],
      registrosRecientes: [
        { id: 'g1', id_usuario: 'u1', id_reto: 'r1', usuario_nombre: 'Ana', reto_nombre: 'Reto', estado: 'Aprobado', fecha_registro: '2026-10-20T10:00:00' },
        { id: 'g2', id_usuario: 'u1', id_reto: 'r2', usuario_nombre: 'Ana', reto_nombre: 'Otro', estado: 'Pendiente', fecha_registro: '2026-10-21T10:00:00' },
      ],
      actividadSemanal: [{ dia: '2026-10-20T00:00:00', cantidad: '3' }],
      retosPorCategoria: [{ categoria_id: 'c1', cantidad: '5' }],
      usuariosActivos: 10,
      totalRegistros: 2,
      retosAbiertos: 1,
      analisisEmpresas: { estadisticas: {} },
    }))

    const result = await loadPublicDashboard()

    expect(lastRequest().url).toBe('/api/public/dashboard')
    expect(result.usuarios).toEqual([{ id: 'u1', nombre: 'Ana' }])
    expect(result.registros[0]).toMatchObject({ usuarioNombre: 'Ana', retoId: 'r1', fechaRegistro: '2026-10-20' })
    expect(result.retos[0]).toMatchObject({ empresaId: 'e1', fechaFin: '2026-02-01' })
    expect(result.publicSummary).toEqual({
      activeUsers: 10,
      totalRegistrations: 2,
      openChallenges: 1,
      weeklyCounts: { '2026-10-20': 3 },
      challengeCountsByCategory: { c1: 5 },
      companyChallengeAnalysis: { estadisticas: {} },
    })
  })
})
