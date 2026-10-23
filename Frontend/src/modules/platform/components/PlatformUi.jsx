import {
  ArrowUpRight, CalendarDays, TrendingUp, Target
} from 'lucide-react'
import { displayCount, formatDate, getName, initials } from '../../core/utils/formatters.js'

const statusColors = {
  'Abierto':'green', 'En revisión':'amber', 'Cerrado':'neutral',
  'Aprobado':'green', 'Pendiente':'amber', 'Rechazado':'rose',
  'Activo':'green', 'Inactivo':'neutral',
}
const priorityColors = {'Alta':'rose','Media':'amber','Baja':'blue'}

export function IconBubble({icon:Icon,variant='rose',size=18}) {
  return <span className={`icon-bubble ${variant}`}><Icon size={size} strokeWidth={2}/></span>
}

export function StatusBadge({value,priority=false}) {
  return <span className={`status-badge ${priority ? (priorityColors[value]||'neutral') : (statusColors[value]||'neutral')}`}>
    <span className="status-dot"/>{value||'—'}
  </span>
}

export function Avatar({name,size='regular',index=0}){
  return <span className={`avatar ${size} av-${index%6}`} title={name}>{initials(name)}</span>
}

export function SectionHeading({eyebrow,title,subtitle,right}){
  return <div className="section-heading"><div><div className="eyebrow">{eyebrow}</div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{right}</div>
}

export function StatCard({icon:Icon,label,value,change,variant}){
  return <div className="stat-card">
    <div className="stat-heading"><IconBubble icon={Icon} variant={variant}/><ArrowUpRight size={17} className="stat-arrow"/></div>
    <strong className="stat-value">{displayCount(value)}</strong>
    <span className="stat-label">{label}</span>
    <div className="stat-footer"><span className={`stat-trend ${variant}`}><TrendingUp size={13}/>{change}</span><span>datos de plataforma</span></div>
  </div>
}

export function ChallengeCard({reto,data,onView,index=0}) {
  const empresa=getName(data,'empresas',reto.empresaId)
  const prioridad=getName(data,'prioridades',reto.prioridadId)
  const categoria=getName(data,'categorias',reto.categoriaId)
  return <article className="challenge-card">
    <div className="challenge-card-head"><span className={`challenge-icon challenge-tone-${index%5}`}><Target size={21}/></span><StatusBadge value={reto.estado}/></div>
    <div className="challenge-company">{empresa}</div>
    <button className="challenge-title" onClick={()=>onView(reto)}>{reto.nombre}</button>
    <p>{reto.descripcion}</p>
    <div className="challenge-tags"><span>{categoria}</span><StatusBadge priority value={prioridad}/></div>
    <div className="challenge-card-footer"><span><CalendarDays size={15}/> Hasta {formatDate(reto.fechaFin)}</span><button onClick={()=>onView(reto)} aria-label={`Ver detalle de ${reto.nombre}`}><ArrowUpRight size={20}/></button></div>
  </article>
}
