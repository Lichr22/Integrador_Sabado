import { useEffect, useMemo, useState } from 'react'
import { ChevronRight, Plus, CalendarDays, LayoutGrid, List, Download, SlidersHorizontal, ChevronDown, Search, X, Sparkles, Eye, Pencil, Trash2, ArrowRight } from 'lucide-react'
import { entityConfig } from '../lib/data.js'
import { formatDate, getName, initials } from '../../core/utils/formatters.js'
import { Avatar, ChallengeCard, SectionHeading, StatusBadge } from './PlatformUi.jsx'

const todayString = () => {
  const d=new Date()
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}
const csvValue = value => `"${String(value ?? '').replace(/"/g,'""')}"`
export default function EntityPage({type,data,onCreate,onEdit,onDelete,onView,onRegister,search,setSearch,filter,setFilter,viewMode,setViewMode,onNotify}){
  const cfg=entityConfig[type]
  const [sort,setSort]=useState({field:'',direction:'asc'})
  const [visibleCount,setVisibleCount]=useState(10)
  useEffect(()=>{setSort({field:'',direction:'asc'});setVisibleCount(10)},[type])
  const records=useMemo(()=>{
    const term=search.toLocaleLowerCase('es').trim()
    const filtered=data[type].filter(item=>{
      const values=[...Object.values(item),...cfg.columns.filter(col=>col.relation).map(col=>getName(data,col.relation,item[col.field]))]
      const matchesSearch=values.some(value=>String(value??'').toLocaleLowerCase('es').includes(term))
      const matchesFilter=!filter||item.estado===filter
      return matchesSearch&&matchesFilter
    })
    if(sort.field) filtered.sort((a,b)=>{
      const col=cfg.columns.find(c=>c.field===sort.field)
      const val=item=>col?.relation ? getName(data,col.relation,item[sort.field]) : (item[sort.field]??'')
      return String(val(a)).localeCompare(String(val(b)),'es',{numeric:true})*(sort.direction==='asc'?1:-1)
    })
    return filtered
  },[data,type,search,filter,sort,cfg])
  const hasStatus=cfg.fields.some(field=>field.name==='estado')
  const statuses=cfg.fields.find(field=>field.name==='estado')?.options??[]
  const exportCsv=()=>{
    const rows=[cfg.columns.map(col=>col.label),...records.map(item=>cfg.columns.map(col=>col.relation?getName(data,col.relation,item[col.field]):item[col.field]))]
    const contents='\uFEFF'+rows.map(row=>row.map(csvValue).join(';')).join('\r\n')
    const url=URL.createObjectURL(new Blob([contents],{type:'text/csv;charset=utf-8;'}))
    const link=document.createElement('a');link.href=url;link.download=`nexo-${type}-${todayString()}.csv`;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)
    onNotify(`CSV de ${type} generado correctamente.`)
  }
  const toggleSort=field=>setSort(prev=>({field,direction:prev.field===field&&prev.direction==='asc'?'desc':'asc'}))
  const primaryColumn=cfg.columns[0]?.field
  const renderCell=(item,col)=>{
    const value=col.relation?getName(data,col.relation,item[col.field]):item[col.field]
    if(col.field==='estado') return <StatusBadge value={value}/>
    if(col.field==='prioridadId') return <StatusBadge priority value={value}/>
    if(col.type==='date') return <span className="cell-date"><CalendarDays size={14}/>{formatDate(value)}</span>
    if(col.field==='nombre'&&type==='usuarios') return <span className="cell-person"><Avatar name={value} size="small" index={data.usuarios.findIndex(u=>u.id===item.id)}/><span><strong>{value}</strong></span></span>
    if(col.field==='nombre'&&type==='empresas') return <span className="cell-company"><span className="company-monogram">{initials(value)}</span><strong>{value}</strong></span>
    if(col.field===primaryColumn) return <span className="cell-primary" title={String(value)}>{value}</span>
    if(col.field==='correo') return <span className="cell-email" title={value}>{value}</span>
    if(col.field==='descripcion'||col.field==='observacion')return <span className="cell-truncate" title={value}>{value||'—'}</span>
    return <span title={String(value??'')}>{value||'—'}</span>
  }
  return <div className="page entity-page">
    <div className="page-breadcrumb"><span>Espacio de trabajo</span><ChevronRight size={14}/><strong>{cfg.title}</strong></div>
    <SectionHeading eyebrow="GESTIÓN DE LA PLATAFORMA" title={cfg.title} subtitle={cfg.description} right={<button className="btn btn-primary" onClick={()=>onCreate(type)}><Plus size={18}/> Nuevo {cfg.singular}</button>}/>
    {type==='retos'&&<div className="retos-intro"><div className="retos-intro-icon"><Sparkles size={21}/></div><div><strong>Transforma desafíos en oportunidades</strong><p>Organiza retos reales de empresas e invita a la comunidad a proponer soluciones.</p></div><button onClick={()=>onRegister()}><Plus size={17}/> Nueva inscripción</button></div>}
    <div className="management-card">
      <div className="table-title-row"><div className="table-title"><h3>Listado de {type}</h3><span className="count-badge">{records.length} {records.length===1?'registro':'registros'}</span></div><div className="table-actions">{type==='retos'&&<div className="view-toggle"><button onClick={()=>setViewMode('cards')} title="Vista de tarjetas" className={viewMode==='cards'?'selected':''}><LayoutGrid size={17}/></button><button onClick={()=>setViewMode('table')} title="Vista de tabla" className={viewMode==='table'?'selected':''}><List size={19}/></button></div>}<button className="btn btn-outline btn-small" onClick={exportCsv}><Download size={17}/> Exportar CSV</button></div></div>
      <div className="filters-row"><label className="search-field"><Search size={18}/><input aria-label={`Buscar ${type}`} placeholder={`Buscar ${cfg.singular}, nombre o palabra clave...`} value={search} onChange={event=>setSearch(event.target.value)}/>{search&&<button onClick={()=>setSearch('')} aria-label="Limpiar búsqueda"><X size={16}/></button>}</label>{hasStatus&&<label className="filter-select"><SlidersHorizontal size={17}/><select value={filter} onChange={event=>setFilter(event.target.value)} aria-label="Filtrar por estado"><option value="">Todos los estados</option>{statuses.map(s=><option key={s}>{s}</option>)}</select><ChevronDown size={15}/></label>}</div>
      {type==='retos'&&viewMode==='cards' ? <div className="challenge-grid">{records.slice(0,visibleCount).map((reto,index)=><ChallengeCard key={reto.id} reto={reto} data={data} onView={onView} index={index} onRegister={onRegister}/>)}</div> : <div className="table-wrap"><table className="data-table"><thead><tr>{cfg.columns.map(col=><th key={col.field}><button onClick={()=>toggleSort(col.field)} title={`Ordenar por ${col.label}`} className={sort.field===col.field?'sorted':''}>{col.label}{sort.field===col.field?<span>{sort.direction==='asc'?'↑':'↓'}</span>:null}</button></th>)}<th className="actions-header">Acciones</th></tr></thead><tbody>{records.slice(0,visibleCount).map(item=><tr key={item.id}>{cfg.columns.map(col=><td key={col.field}>{renderCell(item,col)}</td>)}<td><div className="row-actions">{type==='retos'&&<button className="action-button" title="Ver detalle" aria-label={`Ver ${item.nombre}`} onClick={()=>onView(item)}><Eye size={17}/></button>}<button className="action-button" title="Editar" aria-label={`Editar ${item.nombre||item.id}`} onClick={()=>onEdit(type,item)}><Pencil size={16}/></button><button className="action-button danger" title="Eliminar" aria-label={`Eliminar ${item.nombre||item.id}`} onClick={()=>onDelete(type,item)}><Trash2 size={16}/></button></div></td></tr>)}</tbody></table></div>}
      {records.length===0&&<div className="empty-state"><span><Search size={31}/></span><strong>No encontramos resultados</strong><p>Prueba con otro término, cambia los filtros o crea un nuevo registro.</p><button className="btn btn-outline" onClick={()=>{setSearch('');setFilter('')}}>Limpiar filtros</button></div>}
      {records.length>0&&<div className="table-footer"><span>Mostrando {Math.min(visibleCount,records.length)} de {records.length} resultados</span>{records.length>visibleCount?<button className="text-action" onClick={()=>setVisibleCount(c=>c+10)}>Mostrar más <ArrowRight size={16}/></button>:<span>Fin del listado</span>}</div>}
    </div>
  </div>
}

