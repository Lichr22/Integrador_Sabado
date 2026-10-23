export const getName = (data, source, id) => data[source]?.find(item => item.id === id)?.nombre ?? 'No encontrado'
export const formatDate = value => value ? new Date(`${value}T12:00:00`).toLocaleDateString('es-CO',{day:'2-digit',month:'short',year:'numeric'}) : '—'
export const initials = name => (name || '?').trim().split(/\s+/).slice(0,2).map(word=>word[0]).join('').toUpperCase()
export const displayCount = count => String(count).padStart(2,'0')
