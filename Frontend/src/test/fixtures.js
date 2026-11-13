// Datos de prueba compartidos con el formato que usa el frontend (camelCase).

export const todayKey = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

export const account = {
  id: 'u1', usuarioId: 'u1', nombre: 'Ana Pérez', correo: 'ana@nexo.co',
  rol: 'Administrador', estado: 'Activo', creadoEl: '2026-10-01',
}

export const buildData = () => ({
  empresas: [
    { id: 'e1', nombre: 'Acme', nit: '900123456-7', sector: 'Tecnología', contacto: 'Luis', correo: 'acme@acme.co', telefono: '3001234567', estado: 'Activa' },
    { id: 'e2', nombre: 'Beta Logística', nit: '900765432-1', sector: 'Transporte', contacto: 'Eva', correo: 'eva@beta.co', telefono: '', estado: 'Inactiva' },
  ],
  categorias: [
    { id: 'c1', nombre: 'Logística', descripcion: 'Transporte y entregas', areaResponsable: 'Operaciones' },
    { id: 'c2', nombre: 'Finanzas', descripcion: 'Costos y presupuestos', areaResponsable: '' },
  ],
  prioridades: [
    { id: 'p1', nombre: 'Alta', nivel: 1, diasMaxRespuesta: 5 },
    { id: 'p2', nombre: 'Baja', nivel: 3, diasMaxRespuesta: 30 },
  ],
  usuarios: [
    { id: 'u1', usuarioId: 'u1', nombre: 'Ana Pérez', correo: 'ana@nexo.co', rol: 'Administrador', estado: 'Activo', fechaRegistro: '2026-10-01' },
    { id: 'u2', usuarioId: 'u2', nombre: 'Luis Gómez', correo: 'luis@nexo.co', rol: 'Participante', estado: 'Inactivo', fechaRegistro: '2026-10-05' },
  ],
  retos: [
    { id: 'r1', nombre: 'Reducir tiempos de entrega', descripcion: 'Optimizar rutas', empresaId: 'e1', categoriaId: 'c1', prioridadId: 'p1', estado: 'Abierto', fechaInicio: '2026-01-01', fechaFin: '2026-12-31' },
    { id: 'r2', nombre: 'Bajar costos operativos', descripcion: 'Revisar proveedores', empresaId: 'e1', categoriaId: 'c1', prioridadId: 'p2', estado: 'Cerrado', fechaInicio: '2026-02-01', fechaFin: '2026-03-31' },
  ],
  registros: [
    { id: 'g1', usuarioId: 'u1', retoId: 'r1', fechaRegistro: '2025-10-20', estado: 'Aprobado', observacion: '' },
    { id: 'g2', usuarioId: 'u2', retoId: 'r1', fechaRegistro: '2025-10-22', estado: 'Pendiente', observacion: 'Falta documento' },
  ],
})
