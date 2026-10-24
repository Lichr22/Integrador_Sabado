import { Building2, Target, UsersRound, ClipboardList, CalendarDays, Sparkles, ArrowUpRight, SlidersHorizontal, ChevronRight, ArrowRight, TrendingUp, Plus, BarChart3 } from 'lucide-react'
import { formatDate, getName } from '../../core/utils/formatters.js'
import { Avatar, StatusBadge, StatCard } from '../components/PlatformUi.jsx'
import './Dashboard.css'

const colors = ['#f1a3bf','#94a9f8','#9bdcca','#fed69a','#b5a3e9','#c1c8d7']
const isOpenChallenge = challenge => challenge.estado?.trim().toLocaleLowerCase('es-CO') === 'abierto'

export default function Dashboard({data,readOnly=false,navigate,onView,onCreate,onRegister}){
  const openRetos=data.retos.filter(isOpenChallenge)
  const counts={companies:data.empresas.length,retos:data.publicSummary?.openChallenges??openRetos.length,users:data.publicSummary?.activeUsers??data.usuarios.filter(u=>u.estado==='Activo').length,regs:data.publicSummary?.totalRegistrations??data.registros.length}
  const categories=data.categorias.map((c,index)=>({name:c.nombre,count:data.publicSummary?.challengeCountsByCategory?.[c.id]??data.retos.filter(r=>r.categoriaId===c.id).length,color:colors[index%colors.length]})).sort((a,b)=>b.count-a.count)
  const most=Math.max(1,...categories.map(item=>item.count))
  const recent=[...data.registros].sort((a,b)=>b.fechaRegistro.localeCompare(a.fechaRegistro)).slice(0,5)
  const now=new Date()
  const week=Array.from({length:7},(_,i)=>{
    const date=new Date(now.getFullYear(),now.getMonth(),now.getDate()-(6-i))
    const key=`${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`
    return {day:date.toLocaleDateString('es-CO',{weekday:'short'}).replace('.',''),key,count:data.publicSummary?.weeklyCounts?.[key]??data.registros.filter(r=>r.fechaRegistro===key).length}
  })
  const maxWeek=Math.max(1,...week.map(item=>item.count))
  const companyAnalysis=data.publicSummary?.companyChallengeAnalysis
  const companyStats=companyAnalysis?.estadisticas
  const companiesByChallenges=companyAnalysis?.empresas||[]
  const maxCompanyChallenges=Math.max(1,...companiesByChallenges.map(company=>company.retos))
  const numberFormat=new Intl.NumberFormat('es-CO',{maximumFractionDigits:2})
  return <div className="page dashboard-page">
    <div className="dashboard-greeting"><div><div className="eyebrow"><span className="eyebrow-line"/> PANEL DE CONTROL</div><h1>¡Hola, equipo! <span className="hello-wave">✳</span></h1><p>Este es el pulso de la innovación en tu comunidad.</p></div><span className="date-chip"><CalendarDays size={16}/>{new Date().toLocaleDateString('es-CO',{month:'long',year:'numeric'})}</span></div>
    <section className="hero-banner">
      <div className="hero-content"><span className="hero-kicker"><Sparkles size={14}/> INNOVACIÓN COLABORATIVA</span><h2>Las buenas ideas<br/>nacen de grandes <em>retos.</em></h2><p>Descubre oportunidades, conecta talento y transforma desafíos empresariales en soluciones reales.</p><button className="btn btn-white" disabled={readOnly} onClick={()=>navigate('retos')}>Explorar retos <ArrowUpRight size={18}/></button></div>
      <div className="hero-art" aria-hidden="true"><div className="orbit orbit-outer"/><div className="orbit orbit-mid"/><div className="orbit orbit-inner"/><div className="art-star star-one">✦</div><div className="art-star star-two">✦</div><div className="art-center"><span className="art-spark">✳</span></div><div className="art-pill pill-one">IDEAS</div><div className="art-pill pill-two">IMPACTO ↗</div></div>
    </section>
    <div className="stats-grid"><StatCard icon={Building2} label="Empresas aliadas" value={counts.companies} change="Aliados" variant="rose"/><StatCard icon={Target} label="Retos abiertos" value={counts.retos} change="Disponibles" variant="blue"/><StatCard icon={UsersRound} label="Usuarios activos" value={counts.users} change="En comunidad" variant="purple"/><StatCard icon={ClipboardList} label="Participaciones" value={counts.regs} change="Registros" variant="green"/></div>
    <div className="content-grid">
      <div className="content-panel recent-panel"><div className="panel-heading"><div><h3>Retos destacados</h3><p>Oportunidades listas para crear impacto</p></div><button className="text-action" disabled={readOnly} onClick={()=>navigate('retos')}>Ver todos <ArrowRight size={16}/></button></div>
        <div className="featured-challenges">{openRetos.slice(0,3).map((reto,index)=><div key={reto.id} className="featured-item"><span className={`featured-icon tone-${index%3}`}><Target size={21}/></span><div className="featured-main"><div className="featured-title">{reto.nombre}</div><div className="featured-company">{getName(data,'empresas',reto.empresaId)} <span>•</span> {getName(data,'categorias',reto.categoriaId)}</div></div><StatusBadge priority value={getName(data,'prioridades',reto.prioridadId)}/><button className="row-view" title="Ver reto" disabled={readOnly} onClick={()=>onView(reto)}><ChevronRight size={19}/></button></div>)}
          {openRetos.length===0&&<div className="empty-mini">Aún no hay retos abiertos.</div>}</div>
      </div>
      <div className="content-panel categories-panel"><div className="panel-heading"><div><h3>Retos por categoría</h3><p>Distribución actual de desafíos</p></div><span className="mini-top-icon"><SlidersHorizontal size={17}/></span></div>
        <div className="category-bars">{categories.map(item=><div className="category-bar" key={item.name}><div className="category-label"><span>{item.name}</span><strong>{item.count}</strong></div><div className="bar-track"><span style={{width:`${item.count/most*100}%`,background:item.color}}/></div></div>)}</div>
      </div>
    </div>
    <section className="content-panel company-analysis">
      <div className="panel-heading company-analysis-heading">
        <div><span className="company-analysis-kicker"><BarChart3 size={14}/> ANÁLISIS ESTADÍSTICO · PYTHON</span><h3>Retos por empresa</h3><p>Distribución completa según la empresa relacionada a cada reto.</p></div>
        {companyStats?.empresaLider&&<span className="company-leader"><TrendingUp size={15}/>{companyStats.empresaLider.nombre} lidera</span>}
      </div>
      {companyStats?<>
        <div className="company-stat-grid">
          <div className="company-stat"><span>Retos totales</span><strong>{numberFormat.format(companyStats.totalRetos)}</strong><small>{numberFormat.format(companyStats.retosAbiertos)} abiertos</small></div>
          <div className="company-stat"><span>Empresas con retos</span><strong>{numberFormat.format(companyStats.empresasConRetos)} <small>/ {numberFormat.format(companyStats.totalEmpresas)}</small></strong><small>{numberFormat.format(companyStats.empresasSinRetos)} sin retos</small></div>
          <div className="company-stat"><span>Promedio por empresa</span><strong>{numberFormat.format(companyStats.promedioRetos)}</strong><small>Retos por empresa registrada</small></div>
          <div className="company-stat"><span>Mediana</span><strong>{numberFormat.format(companyStats.medianaRetos)}</strong><small>Desviación estándar: {numberFormat.format(companyStats.desviacionEstandar)}</small></div>
          <div className="company-stat"><span>Máximo por empresa</span><strong>{numberFormat.format(companyStats.maxRetos)}</strong><small>{companyStats.empresaLider?.nombre||'Sin empresa líder'}</small></div>
        </div>
        <div className="company-analysis-body">
          <div className="company-ranking-heading"><strong>Distribución por empresa</strong><span>Empresa · retos abiertos · participación del total</span></div>
          {companiesByChallenges.length?companiesByChallenges.map((company,index)=><div className="company-ranking-row" key={company.empresaId}>
            <span className="company-rank">{String(index+1).padStart(2,'0')}</span>
            <div className="company-ranking-main"><div className="company-ranking-label"><strong title={company.nombre}>{company.nombre}</strong><span>{numberFormat.format(company.retosAbiertos)} {company.retosAbiertos===1?'abierto':'abiertos'} · {numberFormat.format(company.porcentaje)}%</span></div><div className="company-ranking-track"><span style={{width:`${company.retos/maxCompanyChallenges*100}%`}}/></div></div>
            <strong className="company-ranking-count">{numberFormat.format(company.retos)}</strong>
          </div>):<div className="empty-mini">No hay empresas registradas para comparar.</div>}
          {companyStats.retosSinEmpresa>0&&<p className="company-data-note">{numberFormat.format(companyStats.retosSinEmpresa)} retos no tienen una empresa asignada y se excluyen del ranking por empresa.</p>}
          {(companyStats.nombresCorregidos>0||companyStats.gruposConNombreDuplicado>0)&&<p className="company-data-note">Limpieza aplicada al mostrar: {numberFormat.format(companyStats.nombresCorregidos)} nombres vacíos o con espacios se normalizaron; se detectaron {numberFormat.format(companyStats.gruposConNombreDuplicado)} grupos con nombres duplicados. Las empresas se mantienen separadas por su ID, sin modificar la base de datos.</p>}
        </div>
      </>:<div className="empty-mini">El análisis de empresas no está disponible en este momento.</div>}
    </section>
    <div className="content-grid lower-grid">
      <div className="content-panel activity-panel"><div className="panel-heading"><div><h3>Actividad reciente</h3><p>Últimas inscripciones registradas</p></div><button className="text-action" disabled={readOnly} onClick={()=>navigate('registros')}>Ver registros <ArrowRight size={16}/></button></div>
        <div className="activity-list">{recent.map((reg,index)=><div className="activity-item" key={reg.id}><Avatar name={reg.usuarioNombre||getName(data,'usuarios',reg.usuarioId)} index={index}/><div className="activity-copy"><strong>{reg.usuarioNombre||getName(data,'usuarios',reg.usuarioId)}</strong><span>Se registró en <b>{reg.retoNombre||getName(data,'retos',reg.retoId)}</b></span></div><span className="activity-date">{formatDate(reg.fechaRegistro)}</span></div>)}{recent.length===0&&<div className="empty-mini">No se han registrado participaciones.</div>}</div>
      </div>
      <div className="content-panel chart-panel"><div className="panel-heading"><div><h3>Participación semanal</h3><p>Inscripciones de los últimos 7 días</p></div><span className="chart-mini-tag"><TrendingUp size={14}/> {week.reduce((s,d)=>s+d.count,0)} en total</span></div>
        <div className="bar-chart" aria-label="Registros de los últimos siete días">{week.map(item=><div className="chart-column" key={item.key} title={`${item.key}: ${item.count} registros`}><span className="chart-count">{item.count||''}</span><span className="chart-vertical"><span style={{height:`${Math.max(7,item.count/maxWeek*100)}%`}} className={item.count?'filled':''}/></span><span className="chart-day">{item.day}</span></div>)}</div>
      </div>
    </div>
    <div className="dashboard-end"><div><span className="mini-live"/>{readOnly?' Inicia sesión para habilitar la gestión de la plataforma.':' Datos cargados desde la API de la plataforma.'}</div><button disabled={readOnly} onClick={()=>onCreate('retos')}><Plus size={16}/> Crear un nuevo reto</button></div>
  </div>
}
