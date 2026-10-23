const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const SESSION_KEY = 'nexo-api-token'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request(path, options = {}) {
  const token = sessionStorage.getItem(SESSION_KEY)
  const headers = new Headers(options.headers)
  if (options.body !== undefined) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  if (response.status === 204) return null
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const message = body?.message || `La API respondió con HTTP ${response.status}`
    if (response.status === 401) {
      clearSession()
      window.dispatchEvent(new Event('api-session-expired'))
    }
    throw new ApiError(message, response.status)
  }
  return body
}

export const saveSession = token => sessionStorage.setItem(SESSION_KEY, token)
export const clearSession = () => sessionStorage.removeItem(SESSION_KEY)
export const hasSession = () => Boolean(sessionStorage.getItem(SESSION_KEY))

export const login = credentials => request('/auth/login', {
  method: 'POST',
  body: JSON.stringify({ correo: credentials.correo, contrasena: credentials.password }),
}).then(result => ({ ...result, user: fromAuthUser(result.user) }))

export const register = account => request('/auth/register', {
  method: 'POST',
  body: JSON.stringify({ nombre: account.nombre, correo: account.correo, contrasena: account.password }),
}).then(result => ({ ...result, user: fromAuthUser(result.user) }))

export const getCurrentUser = () => request('/auth/me').then(fromAuthUser)

const fromAuthUser = user => ({
  id: user.id,
  usuarioId: user.id,
  nombre: user.nombre,
  correo: user.correo,
  rol: user.rol,
  estado: user.activo ? 'Activo' : 'Inactivo',
  creadoEl: user.fecha_registro?.slice(0, 10) || '',
})

const resourceNames = ['empresas', 'categorias', 'prioridades', 'usuarios', 'retos', 'registros']

const fromApiRecord = (resource, row) => {
  switch (resource) {
    case 'empresas':
      return { ...row, estado: row.activa ? 'Activa' : 'Inactiva' }
    case 'categorias':
      return { ...row, areaResponsable: row.area_responsable }
    case 'prioridades':
      return { ...row, diasMaxRespuesta: row.dias_max_respuesta }
    case 'usuarios':
      return {
        id: row.id,
        usuarioId: row.id,
        nombre: row.nombre,
        correo: row.correo,
        rol: row.rol,
        estado: row.activo ? 'Activo' : 'Inactivo',
        fechaRegistro: row.fecha_registro?.slice(0, 10) || '',
      }
    case 'retos':
      return {
        ...row,
        empresaId: row.id_empresa,
        categoriaId: row.id_categoria,
        prioridadId: row.id_prioridad,
        fechaInicio: row.fecha_inicio,
        fechaFin: row.fecha_fin,
      }
    case 'registros':
      return {
        ...row,
        usuarioId: row.id_usuario,
        retoId: row.id_reto,
        fechaRegistro: row.fecha_registro?.slice(0, 10) || '',
      }
    default:
      return row
  }
}

const toApiRecord = (resource, record) => {
  const { id, ...fields } = record
  switch (resource) {
    case 'empresas':
      return { ...fields, activa: fields.estado === 'Activa' || fields.estado === 'Activo', estado: undefined }
    case 'categorias':
      return { ...fields, area_responsable: fields.areaResponsable, areaResponsable: undefined }
    case 'prioridades':
      return { ...fields, dias_max_respuesta: fields.diasMaxRespuesta, diasMaxRespuesta: undefined }
    case 'usuarios':
      return {
        ...fields,
        activo: fields.estado === 'Activo',
        contrasena: fields.contrasena || undefined,
        fecha_registro: fields.fechaRegistro ? `${fields.fechaRegistro}T00:00:00` : undefined,
        estado: undefined,
        fechaRegistro: undefined,
      }
    case 'retos':
      return {
        ...fields,
        id_empresa: fields.empresaId,
        id_categoria: fields.categoriaId,
        id_prioridad: fields.prioridadId,
        fecha_inicio: fields.fechaInicio,
        fecha_fin: fields.fechaFin,
        empresaId: undefined,
        categoriaId: undefined,
        prioridadId: undefined,
        fechaInicio: undefined,
        fechaFin: undefined,
      }
    case 'registros':
      return {
        ...fields,
        id_usuario: fields.usuarioId,
        id_reto: fields.retoId,
        fecha_registro: fields.fechaRegistro ? `${fields.fechaRegistro}T00:00:00` : undefined,
        usuarioId: undefined,
        retoId: undefined,
        fechaRegistro: undefined,
      }
    default:
      return fields
  }
}

export async function loadPlatformData() {
  const rows = await Promise.all(resourceNames.map(resource => request(`/${resource}`)))
  return Object.fromEntries(resourceNames.map((resource, index) => [
    resource,
    rows[index].map(row => fromApiRecord(resource, row)),
  ]))
}

export async function createRecord(resource, record) {
  const result = await request(`/${resource}`, {
    method: 'POST',
    body: JSON.stringify(toApiRecord(resource, record)),
  })
  return fromApiRecord(resource, result)
}

export async function updateRecord(resource, record) {
  const result = await request(`/${resource}/${encodeURIComponent(record.id)}`, {
    method: 'PUT',
    body: JSON.stringify(toApiRecord(resource, record)),
  })
  return fromApiRecord(resource, result)
}

export const deleteRecord = (resource, id) => request(
  `/${resource}/${encodeURIComponent(id)}`,
  { method: 'DELETE' },
)

export async function updateCurrentUser(user) {
  const result = await request(`/usuarios/${encodeURIComponent(user.id)}`, {
    method: 'PUT',
    body: JSON.stringify({ nombre: user.nombre, correo: user.correo }),
  })
  return fromApiRecord('usuarios', result)
}
