import React, { useEffect, useMemo, useRef, useState } from 'react'
import {
  LayoutDashboard, Target, Building2, Tags, Flag, UsersRound, ClipboardList, Search,
  ChevronDown, ChevronRight, ArrowUpRight, Plus, ArrowRight, CalendarDays,
  ArrowLeft, Check, CheckCircle2, Clock3, CircleAlert, X, Menu, Pencil, Trash2,
  Eye, Sparkles, Layers3, Zap, BookOpen, LockKeyhole, UserRound,
  Mail, Info, ShieldCheck, LogIn, LogOut, UserPlus, Save, BadgeCheck
} from 'lucide-react'
import {
  navItems, entityConfig
} from '../lib/data.js'
import LoginPage from '../../auth/pages/Login.jsx'
import RegisterPage from '../../auth/pages/Registro.jsx'
import ProfilePage from '../../auth/pages/Perfil.jsx'
import { formatDate, getName, initials } from '../../core/utils/formatters.js'
import { Avatar, IconBubble, SectionHeading, StatusBadge } from './PlatformUi.jsx'
import {
  clearSession, createRecord, deleteRecord, getCurrentUser, hasSession,
  loadPlatformData, loadPublicDashboard, login as loginRequest, register as registerRequest,
  saveSession, updateCurrentUser, updateRecord
} from '../services/platformApi.js'
import Dashboard from '../pages/Dashboard.jsx'
import Retos from '../pages/Reto.jsx'
import Empresas from '../pages/Empresa.jsx'
import Categorias from '../pages/Categoria.jsx'
import Prioridades from '../pages/Prioridad.jsx'
import Usuarios from '../pages/Usuario.jsx'
import Registros from '../pages/Registro.jsx'

const icons = {LayoutDashboard,Target,Building2,Tags,Flag,UsersRound,ClipboardList}
const relationBlocking = {
  empresas:[['retos','empresaId','retos']],
  categorias:[['retos','categoriaId','retos']],
  prioridades:[['retos','prioridadId','retos']],
  usuarios:[['registros','usuarioId','registros']],
  retos:[['registros','retoId','registros']],
}
const emptyData = {empresas:[],categorias:[],prioridades:[],usuarios:[],retos:[],registros:[]}
const todayString = () => {
  const d=new Date()
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}
function Logo(){
  return <div className="brand-logo"><span className="brand-glyph"><span/><span/><span/><span/></span><span className="brand-name">nexo<span className="brand-dot">.</span></span></div>
}
function ModalShell({children,onClose,size='medium'}){
  useEffect(()=>{
    const handleKey=event=>{if(event.key==='Escape') onClose()}
    window.addEventListener('keydown',handleKey)
    document.body.style.overflow='hidden'
    return ()=>{window.removeEventListener('keydown',handleKey); document.body.style.overflow=''}
  },[onClose])
  return <div className="modal-overlay" onMouseDown={event=>{if(event.target===event.currentTarget) onClose()}}>
    <div className={`modal modal-${size}`} role="dialog" aria-modal="true" aria-label="Diálogo de Nexo">{children}</div>
  </div>
}

function AccountMenu({account,navigate,onLogout}){
  const [open,setOpen]=useState(false)
  const menuRef=useRef(null)
  useEffect(()=>{
    if(!open)return
    const outside=event=>{if(!menuRef.current?.contains(event.target))setOpen(false)}
    const escape=event=>{if(event.key==='Escape')setOpen(false)}
    document.addEventListener('pointerdown',outside)
    document.addEventListener('keydown',escape)
    return ()=>{document.removeEventListener('pointerdown',outside);document.removeEventListener('keydown',escape)}
  },[open])
  const go=page=>{setOpen(false);navigate(page)}
  return <div className="account-menu" ref={menuRef}>
    <button className={`account-trigger ${open?'is-open':''}`} onClick={()=>setOpen(value=>!value)} aria-expanded={open} aria-haspopup="menu" aria-label="Abrir menú de cuenta" title="Menú de cuenta">
      <Avatar name={account?.nombre||'Invitado'} index={1}/><ChevronDown size={14}/>
    </button>
    {open&&<div className="account-dropdown" role="menu" aria-label="Opciones de cuenta">
      <div className="dropdown-user"><Avatar name={account?.nombre||'Invitado'} index={1}/><div><strong>{account?.nombre||'Invitado'}</strong><span>{account?.correo||'Sin sesión iniciada'}</span></div></div>
      <div className="dropdown-caption">MI CUENTA</div>
      <button role="menuitem" className="dropdown-action" onClick={()=>go('perfil')} disabled={!account}><UserRound size={17}/> Mi perfil <ChevronRight size={15}/></button>
      <button role="menuitem" className="dropdown-action" onClick={()=>{if(account){setOpen(false);onLogout()}else{go('login')}}}><LogIn size={17}/> {account?'Cambiar de cuenta':'Iniciar sesión'} <ChevronRight size={15}/></button>
      <button role="menuitem" className="dropdown-action" onClick={()=>go('registro')}><UserPlus size={17}/> Registrarse <ChevronRight size={15}/></button>
      {account&&<><div className="dropdown-separator"/><button role="menuitem" className="dropdown-action logout" onClick={()=>{setOpen(false);onLogout()}}><LogOut size={17}/> Cerrar sesión</button></>}
      <div className="dropdown-bottom"><span className="mini-live"/> {account?'Sesión autenticada en el backend':'Inicia sesión para conectarte al backend'}</div>
    </div>}
  </div>
}

function Sidebar({active,onNavigate,open,onClose,counts,account}){
  return <>
    {open && <div className="mobile-backdrop" onClick={onClose}/>}
    <aside className={`sidebar ${open?'open':''}`}>
      <div className="sidebar-top"><Logo/><button className="icon-only sidebar-close" onClick={onClose} aria-label="Cerrar menú"><X size={19}/></button></div>
      <div className="sidebar-workspace"><span className="workspace-icon"><Layers3 size={19}/></span><div><strong>Espacio de trabajo</strong><small>Proyecto integrador III</small></div><ChevronDown size={15}/></div>
      <div className="menu-caption">MENÚ PRINCIPAL</div>
      <nav aria-label="Navegación principal" className="nav-items">
        {navItems.map(nav=>{const Icon=icons[nav.icon];return <button key={nav.id} className={`nav-item ${active===nav.id?'active':''}`} disabled={!account&&nav.id!=='dashboard'} onClick={()=>{onNavigate(nav.id);onClose()}}>
          <Icon size={19} strokeWidth={1.95}/><span>{nav.label}</span>
          {nav.id==='registros'&& <span className="nav-count">{counts.registros}</span>}
        </button>})}
      </nav>
      <div className="sidebar-lower">
        <div className="menu-caption">TU ESPACIO</div>
        <button className="nav-item" onClick={()=>{onNavigate('acerca');onClose()}}><BookOpen size={19}/><span>Sobre el proyecto</span></button>
        <div className="sidebar-promo">
          <span className="sparkle-surface"><Sparkles size={22}/></span>
          <strong>Las grandes ideas empiezan con un reto.</strong>
          <p>Conecta empresas con soluciones que generan impacto.</p>
          <button disabled={!account} onClick={()=>{onNavigate('retos');onClose()}}>Explorar retos <ArrowUpRight size={15}/></button>
        </div>
        <div className="sidebar-profile">
          <button className="sidebar-account-link" disabled={!account} onClick={()=>{onNavigate('perfil');onClose()}} aria-label="Ir a mi perfil"><Avatar name={account?.nombre||'Invitado'} index={1}/>
          <span><strong>{account?.nombre||'Invitado'}</strong><small>{account?.rol||'Sin sesión'}{account?.estado?` · ${account.estado}`:''}</small></span></button>
        </div>
      </div>
    </aside>
  </>
}

function FormModal({type,item,data,onClose,onSave,initialValues}){
  const cfg=entityConfig[type]
  const initial=useMemo(()=>cfg.fields.reduce((acc,field)=>{
    acc[field.name]=item?.[field.name]??initialValues?.[field.name]??(field.name==='fechaRegistro'||field.name==='fechaInicio'?todayString():field.type==='select'?field.options[0]:'')
    return acc
  },{}),[cfg,item,initialValues])
  const [form,setForm]=useState(initial)
  const [error,setError]=useState('')
  const [saving,setSaving]=useState(false)
  const save=async event=>{
    event.preventDefault()
    const missing=cfg.fields.find(field=>field.required&&!String(form[field.name]??'').trim())
    if(missing){setError(`Completa el campo «${missing.label}».`);return}
    if(type==='retos'&&form.fechaFin<form.fechaInicio){setError('La fecha de cierre no puede ser anterior a la fecha de inicio.');return}
    if(type==='registros'&&data.registros.some(reg=>reg.usuarioId===form.usuarioId&&reg.retoId===form.retoId&&reg.id!==item?.id)){
      setError('Este usuario ya está inscrito en ese reto. Elige otra combinación.');return
    }
    if((type==='usuarios'||type==='empresas')&&form.correo&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.correo)){setError('Ingresa un correo electrónico válido.');return}
    if(type==='usuarios'&&data.usuarios.some(user=>user.correo.toLowerCase()===form.correo.toLowerCase()&&user.id!==item?.id)){setError('Ese correo ya está registrado.');return}
    const cleaned={...form}
    for(const field of cfg.fields){
      if(field.type==='number') cleaned[field.name]=String(form[field.name]??'').trim()?Number(form[field.name]):null
      else cleaned[field.name]=String(form[field.name]??'').trim()
    }
    setSaving(true)
    try{
      await onSave(type,{...cleaned,...(item?{id:item.id}:{})},Boolean(item))
    }catch(saveError){
      setError(saveError.message)
    }finally{
      setSaving(false)
    }
  }
  return <ModalShell onClose={onClose} size="large"><form onSubmit={save}>
    <div className="modal-header"><div><div className="eyebrow">{item?'EDITAR REGISTRO':'CREAR NUEVO REGISTRO'}</div><h2>{item?'Editar':'Nuevo'} {cfg.singular}</h2><p>Completa la información para {item?'actualizar':'agregar'} {type==='registros'?'la participación':`este ${cfg.singular}`}.</p></div><button type="button" className="modal-x" onClick={onClose} aria-label="Cerrar"><X size={21}/></button></div>
    <div className="modal-body"><div className="form-grid">{cfg.fields.map(field=><label key={field.name} className={`form-field ${field.span===2?'full':''}`}><span>{field.label}{field.required&&<em>*</em>}</span>{field.type==='textarea'?<textarea rows={4} value={form[field.name]??''} placeholder={field.placeholder??''} onChange={event=>{setForm(v=>({...v,[field.name]:event.target.value}));setError('')}}/>:field.type==='relation'?<select required={field.required} value={form[field.name]??''} onChange={event=>{setForm(v=>({...v,[field.name]:event.target.value}));setError('')}}><option value="">Selecciona {field.label.toLowerCase()}</option>{data[field.source].map(source=><option key={source.id} value={source.id}>{source.nombre}</option>)}</select>:field.type==='select'?<select required={field.required} value={form[field.name]??''} onChange={event=>{setForm(v=>({...v,[field.name]:event.target.value}));setError('')}}>{field.options.map(option=><option key={option}>{option}</option>)}</select>:<input required={field.required} type={field.type||'text'} min={field.min??undefined} placeholder={field.placeholder??''} value={form[field.name]??''} onChange={event=>{setForm(v=>({...v,[field.name]:event.target.value}));setError('')}}/>}</label>)}</div>
      {type==='registros'&&<div className="form-hint"><Info size={16}/> Cada usuario puede tener una inscripción por reto.</div>}
      {error&&<div className="form-error" role="alert"><CircleAlert size={17}/>{error}</div>}
    </div>
    <div className="modal-footer"><button className="btn btn-outline" type="button" onClick={onClose} disabled={saving}>Cancelar</button><button className="btn btn-primary" type="submit" disabled={saving}><Check size={18}/>{saving?'Guardando...':item?'Guardar cambios':'Crear registro'}</button></div>
  </form></ModalShell>
}

function DeleteModal({type,item,data,onClose,onConfirm}){
  const links=(relationBlocking[type]||[]).map(([table,field,label])=>({label,count:data[table].filter(r=>r[field]===item.id).length})).filter(row=>row.count>0)
  const canDelete=links.length===0
  return <ModalShell onClose={onClose} size="small"><div className="delete-body"><span className={`delete-icon ${canDelete?'':'blocked'}`}>{canDelete?<Trash2 size={27}/>:<LockKeyhole size={27}/>}</span><h2>{canDelete?'¿Eliminar registro?':'Este registro está en uso'}</h2><p>{canDelete?<>Vas a eliminar <strong>{item.nombre || `${getName(data,'usuarios',item.usuarioId)} · ${getName(data,'retos',item.retoId)}`}</strong>. Esta acción no se puede deshacer.</>:<>No puedes eliminar <strong>{item.nombre}</strong> porque tiene información relacionada. Primero elimina o reasigna los registros dependientes.</>}</p>{!canDelete&&<div className="dependency-list">{links.map(row=><span key={row.label}><CircleAlert size={16}/> {row.count} {row.label} relacionado{row.count===1?'':'s'}</span>)}</div>}</div><div className="modal-footer"><button className="btn btn-outline" onClick={onClose}>Cancelar</button>{canDelete&&<button className="btn btn-danger" onClick={()=>onConfirm(type,item.id)}><Trash2 size={17}/> Eliminar</button>}</div></ModalShell>
}

function DetailModal({item,data,onClose,onEdit,onRegister}){
  const company=data.empresas.find(e=>e.id===item.empresaId)
  const registros=data.registros.filter(r=>r.retoId===item.id)
  const priority=getName(data,'prioridades',item.prioridadId)
  return <ModalShell onClose={onClose} size="detail"><div className="modal-header detail-header"><div><div className="eyebrow">DETALLE DEL RETO</div><h2>{item.nombre}</h2><p>Presentado por {company?.nombre||'Empresa no disponible'}</p></div><button className="modal-x" onClick={onClose} aria-label="Cerrar"><X size={21}/></button></div><div className="detail-body">
    <div className="detail-badges"><StatusBadge value={item.estado}/><StatusBadge priority value={priority}/><span className="detail-category"><Tags size={15}/>{getName(data,'categorias',item.categoriaId)}</span></div>
    <div className="detail-section"><h3>Acerca del desafío</h3><p>{item.descripcion}</p></div>
    <div className="detail-facts"><div><CalendarDays size={20}/><span><small>Fecha de inicio</small><strong>{formatDate(item.fechaInicio)}</strong></span></div><div><Clock3 size={20}/><span><small>Fecha de cierre</small><strong>{formatDate(item.fechaFin)}</strong></span></div><div><Building2 size={20}/><span><small>Empresa</small><strong>{company?.nombre||'—'}</strong></span></div><div><UsersRound size={20}/><span><small>Participaciones</small><strong>{registros.length} inscrito{registros.length===1?'':'s'}</strong></span></div></div>
    <div className="detail-section detail-participants"><h3>Personas inscritas <span>{registros.length}</span></h3>{registros.length?registros.map((reg,index)=><div key={reg.id} className="participant-row"><Avatar name={getName(data,'usuarios',reg.usuarioId)} index={index} size="small"/><strong>{getName(data,'usuarios',reg.usuarioId)}</strong><StatusBadge value={reg.estado}/></div>):<p>Aún no hay inscripciones para este desafío.</p>}</div>
  </div><div className="modal-footer"><button className="btn btn-outline" onClick={()=>onEdit('retos',item)}><Pencil size={17}/> Editar reto</button><button className="btn btn-primary" onClick={()=>onRegister({retoId:item.id})}><Plus size={17}/> Inscribir usuario</button></div></ModalShell>
}

function AboutPage({navigate,data,readOnly}){
  return <div className="page about-page"><div className="page-breadcrumb">Espacio de trabajo <ChevronRight size={14}/> <strong>Sobre el proyecto</strong></div><SectionHeading eyebrow="PROYECTO INTEGRADOR III" title="Sobre Nexo" subtitle="Una propuesta frontend para conectar empresas, retos y talento."/>
    <div className="about-hero"><div className="eyebrow">UNA PLATAFORMA CONECTADA</div><h2>Innovación que conecta.</h2><p>Esta plataforma conecta empresas, retos y talento. La información se consulta y administra a través del backend conectado a Supabase.</p><button className="btn btn-white" disabled={readOnly} onClick={()=>navigate('retos')}>Explorar la plataforma <ArrowUpRight size={18}/></button></div>
    <div className="about-grid"><div className="content-panel"><IconBubble icon={Layers3} variant="rose" size={21}/><h3>6 entidades relacionadas</h3><p>Empresas, retos, categorías, prioridades, usuarios y registros vinculados a la base relacional.</p></div><div className="content-panel"><IconBubble icon={Zap} variant="blue" size={21}/><h3>Gestión conectada</h3><p>Crea, consulta, edita y elimina registros a través de la API REST del backend.</p></div><div className="content-panel"><IconBubble icon={ShieldCheck} variant="green" size={21}/><h3>Sesión autenticada</h3><p>Los módulos requieren una sesión válida para consultar y modificar los datos.</p></div></div>
    <div className="about-settings content-panel"><div><h3>Datos de la plataforma</h3><p>{readOnly?'Inicia sesión para consultar los datos actuales de la plataforma.':`Actualmente hay ${data.empresas.length} empresas, ${data.retos.length} retos, ${data.usuarios.length} usuarios y ${data.registros.length} inscripciones cargados desde la API.`}</p></div></div>
  </div>
}

export default function App(){
  const [data,setData]=useState(emptyData)
  const [dataLoaded,setDataLoaded]=useState(false)
  const [dataLoadError,setDataLoadError]=useState('')
  const [activeAccount,setActiveAccount]=useState(null)
  const [authReady,setAuthReady]=useState(false)
  const resolvePage=(isAuthenticated,requestedPage=window.location.hash.slice(1)||'dashboard')=>{
    const isKnownPage=requestedPage==='dashboard'||requestedPage==='acerca'||requestedPage==='login'||requestedPage==='registro'||requestedPage==='perfil'||entityConfig[requestedPage]
    const page=isKnownPage?requestedPage:'dashboard'
    if(isAuthenticated&&page==='login')return 'perfil'
    return !isAuthenticated&&!['login','registro','dashboard','acerca'].includes(page)?'login':page
  }
  const [page,setPage]=useState(()=>window.location.hash.slice(1)||'dashboard')
  const [sidebarOpen,setSidebarOpen]=useState(false)
  const [modal,setModal]=useState(null)
  const [searches,setSearches]=useState({})
  const [filters,setFilters]=useState({})
  const [viewMode,setViewMode]=useState('cards')
  const [toast,setToast]=useState('')
  const searchRef=useRef(null)
  const notify=message=>setToast(message)
  const refreshData=async()=>{
    const loaded=activeAccount?await loadPlatformData():await loadPublicDashboard()
    setData(loaded)
    setDataLoaded(true)
    setDataLoadError('')
  }
  useEffect(()=>{
    let mounted=true
    if(!hasSession()){
      setAuthReady(true)
      return()=>{mounted=false}
    }
    getCurrentUser().then(user=>{
      if(mounted)setActiveAccount(user)
    }).catch(error=>{
      clearSession()
      if(mounted){
        setActiveAccount(null)
        notify(`No se pudo restaurar la sesión: ${error.message}`)
      }
    }).finally(()=>{
      if(mounted)setAuthReady(true)
    })
    return()=>{mounted=false}
  },[])
  useEffect(()=>{
    if(!authReady)return
    const sync=()=>{
      const next=resolvePage(Boolean(activeAccount))
      if(window.location.hash.slice(1)!==next)window.location.hash=next
      setPage(next)
    }
    sync()
    window.addEventListener('hashchange',sync)
    return()=>window.removeEventListener('hashchange',sync)
  },[activeAccount,authReady])
  useEffect(()=>{
    if(authReady&&activeAccount&&page==='login'){
      window.location.hash='perfil'
      setPage('perfil')
    }
  },[activeAccount,authReady,page])
  useEffect(()=>{
    if(!authReady)return
    if(!activeAccount){
      setData(emptyData)
      setDataLoaded(false)
      setDataLoadError('')
      return
    }
    let mounted=true
    setDataLoaded(false)
    loadPlatformData().then(loaded=>{
      if(mounted){
        setData(loaded)
        setDataLoaded(true)
      }
    }).catch(error=>{
      if(mounted){
        setDataLoaded(false)
        setDataLoadError(error.message)
        notify(`No se pudieron cargar los datos del backend: ${error.message}`)
        if(error.status===401){
          clearSession()
          setActiveAccount(null)
        }
      }
    })
    return()=>{mounted=false}
  },[activeAccount?.id,authReady])
  useEffect(()=>{
    if(!authReady||activeAccount||page!=='dashboard')return
    let mounted=true
    const loadPublicData=()=>{
      loadPublicDashboard().then(loaded=>{
        if(mounted){
          setData(loaded)
          setDataLoaded(true)
          setDataLoadError('')
        }
      }).catch(error=>{
        if(mounted){
          setDataLoaded(false)
          setDataLoadError(error.message)
        }
      })
    }
    setData(emptyData)
    setDataLoaded(false)
    setDataLoadError('')
    loadPublicData()
    window.addEventListener('focus',loadPublicData)
    return()=>{
      mounted=false
      window.removeEventListener('focus',loadPublicData)
    }
  },[activeAccount,authReady,page])
  useEffect(()=>{
    const expire=()=>{
      setActiveAccount(null)
      setData(emptyData)
      setDataLoaded(false)
      setPage('login')
      window.location.hash='login'
      notify('La sesión expiró. Inicia sesión nuevamente.')
    }
    window.addEventListener('api-session-expired',expire)
    return()=>window.removeEventListener('api-session-expired',expire)
  },[])
  useEffect(()=>{const handler=event=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();if(page!=='retos')navigate('retos');setTimeout(()=>searchRef.current?.focus(),60)}};document.addEventListener('keydown',handler);return()=>document.removeEventListener('keydown',handler)},[page,activeAccount])
  useEffect(()=>{if(!toast)return;const timeout=setTimeout(()=>setToast(''),4200);return()=>clearTimeout(timeout)},[toast])
  const navigate=next=>{
    const destination=resolvePage(Boolean(activeAccount),next)
    window.location.hash=destination
    setPage(destination)
    window.scrollTo({top:0,behavior:'smooth'})
  }
  const navigateAfterAuthentication=next=>{
    window.location.hash=next
    setPage(next)
    window.scrollTo({top:0,behavior:'smooth'})
  }
  const login=async (email,password)=>{
    try{
      const result=await loginRequest({correo:email,password})
      saveSession(result.token)
      setActiveAccount(result.user)
      setAuthReady(true)
      navigateAfterAuthentication('perfil')
      notify(`¡Bienvenido, ${result.user.nombre.split(' ')[0]}!`)
      return {ok:true}
    }catch(error){
      return {ok:false,message:error.message}
    }
  }
  const logout=()=>{
    clearSession()
    setActiveAccount(null)
    setData(emptyData)
    setDataLoaded(false)
    setDataLoadError('')
    setAuthReady(true)
    navigateAfterAuthentication('login')
    notify('Sesión cerrada.')
  }
  const register=async form=>{
    try{
      const result=await registerRequest(form)
      saveSession(result.token)
      setActiveAccount(result.user)
      setAuthReady(true)
      navigateAfterAuthentication('dashboard')
      notify('Cuenta creada correctamente.')
      return {ok:true}
    }catch(error){
      return {ok:false,message:error.message}
    }
  }
  const saveProfile=async form=>{
    if(!activeAccount)return {ok:false,message:'Inicia sesión para editar tu perfil.'}
    try{
      const user=await updateCurrentUser({id:activeAccount.id,nombre:form.nombre,correo:form.correo})
      setActiveAccount(user)
      await refreshData()
      notify('Perfil actualizado correctamente.')
      return {ok:true}
    }catch(error){
      return {ok:false,message:error.message}
    }
  }
  const openCreate=(type,values)=>setModal({kind:'form',type,initialValues:values})
  const openEdit=(type,item)=>setModal({kind:'form',type,item})
  const openView=item=>setModal({kind:'detail',itemId:item.id})
  const openDelete=(type,item)=>setModal({kind:'delete',type,item})
  const save=async(type,row,isEdit)=>{
    try{
      if(isEdit) await updateRecord(type,row)
      else await createRecord(type,row)
      await refreshData()
      if(type==='usuarios'&&isEdit&&activeAccount?.id===row.id){
        const user=await getCurrentUser()
        setActiveAccount(user)
      }
      setModal(null)
      notify(`${entityConfig[type].singular[0].toUpperCase()+entityConfig[type].singular.slice(1)} ${isEdit?'actualizado':'creado'} correctamente.`)
    }catch(error){
      throw new Error(error.message)
    }
  }
  const deleteRow=async(type,id)=>{
    try{
      await deleteRecord(type,id)
      if(type==='usuarios'&&activeAccount?.id===id){
        logout()
      }else{
        await refreshData()
      }
      setModal(null)
      notify('Registro eliminado correctamente.')
    }catch(error){
      notify(error.message)
    }
  }
  const activeItem=navItems.find(nav=>nav.id===page)
  const accountPageLabels={login:'Iniciar sesión',registro:'Crear cuenta',perfil:'Mi perfil'}
  const relatedItem=modal?.kind==='detail'?data.retos.find(r=>r.id===modal.itemId):null
  const headerSearch=searches.retos??''
  const totalCounts={registros:data.registros.length}
  const EntityScreen={retos:Retos,empresas:Empresas,categorias:Categorias,prioridades:Prioridades,usuarios:Usuarios,registros:Registros}[page]
  return <div className="app-shell">
    <Sidebar active={page} onNavigate={navigate} open={sidebarOpen} onClose={()=>setSidebarOpen(false)} counts={totalCounts} account={activeAccount}/>
    <div className="main-area"><header className="topbar"><div className="topbar-left"><button className="mobile-menu icon-only" onClick={()=>setSidebarOpen(true)} aria-label="Abrir menú"><Menu size={22}/></button><span className="topbar-location"><span>Workspace</span><ChevronRight size={14}/><strong>{activeItem?.label||accountPageLabels[page]||'Sobre el proyecto'}</strong></span></div>
      <div className="topbar-right"><label className="topbar-search"><Search size={18}/><input ref={searchRef} aria-label="Buscar retos globalmente" value={headerSearch} disabled={!activeAccount} onFocus={()=>{if(activeAccount&&page!=='retos') navigate('retos')}} onChange={event=>{setSearches(v=>({...v,retos:event.target.value}));if(activeAccount&&page!=='retos')navigate('retos')}} placeholder="Buscar retos..."/><kbd>⌘ K</kbd></label><span className="topbar-divider"/>{activeAccount&&<span className="demo-pill"><span/> API</span>}<AccountMenu account={activeAccount} navigate={navigate} onLogout={logout}/></div>
    </header>
    <main id="contenido">{!authReady?<div className="page"><div className="empty-state">Verificando sesión...</div></div>:page==='login'?<LoginPage navigate={navigate} onLogin={login} account={activeAccount}/>:page==='registro'?<RegisterPage navigate={navigate} onRegister={register}/>:((activeAccount||page==='dashboard')&&!dataLoaded)?<div className="page"><div className="empty-state"><strong>{dataLoadError?'No se pudieron cargar los datos':'Cargando datos...'}</strong>{dataLoadError&&<><p>{dataLoadError}</p><button className="btn btn-primary" onClick={()=>refreshData().catch(error=>{setDataLoadError(error.message);notify(error.message)})}>Reintentar</button></>}</div></div>:page==='perfil'&&activeAccount?<ProfilePage account={activeAccount} data={data} navigate={navigate} onSave={saveProfile} onLogout={logout} onView={openView}/>:page==='dashboard'?<Dashboard data={data} readOnly={!activeAccount} navigate={navigate} onView={openView} onCreate={openCreate} onRegister={values=>openCreate('registros',values)}/>:page==='acerca'?<AboutPage navigate={navigate} data={data} readOnly={!activeAccount}/>:EntityScreen&&activeAccount?<EntityScreen data={data} onCreate={openCreate} onEdit={openEdit} onDelete={openDelete} onView={openView} onRegister={values=>openCreate('registros',values)} search={searches[page]||''} setSearch={value=>setSearches(prev=>({...prev,[page]:value}))} filter={filters[page]||''} setFilter={value=>setFilters(prev=>({...prev,[page]:value}))} viewMode={viewMode} setViewMode={setViewMode} onNotify={notify}/>:null}</main>
    <footer className="app-footer"><span>© {new Date().getFullYear()} Nexo · Plataforma de retos empresariales</span><span>React <span className="footer-dot">•</span> API REST</span></footer>
    </div>
    {modal?.kind==='form'&&<FormModal key={`${modal.type}-${modal.item?.id||'new'}`} type={modal.type} item={modal.item} initialValues={modal.initialValues} data={data} onClose={()=>setModal(null)} onSave={save}/>}
    {modal?.kind==='delete'&&<DeleteModal type={modal.type} item={modal.item} data={data} onClose={()=>setModal(null)} onConfirm={deleteRow}/>}
    {modal?.kind==='detail'&&relatedItem&&<DetailModal item={relatedItem} data={data} onClose={()=>setModal(null)} onEdit={openEdit} onRegister={values=>openCreate('registros',values)}/>}
    {toast&&<div className="toast" role="status"><span className="toast-icon"><Check size={17}/></span>{toast}<button aria-label="Cerrar notificación" onClick={()=>setToast('')}><X size={16}/></button></div>}
  </div>
}
