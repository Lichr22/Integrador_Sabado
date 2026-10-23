import React, { useEffect, useState } from 'react'
import {
  ArrowRight, BadgeCheck, CalendarDays, CheckCircle2, ChevronRight,
  ClipboardList, LogIn, Pencil, Save, ShieldCheck, Target, UserRound, Mail
} from 'lucide-react'
import { formatDate, getName, initials } from '../../core/utils/formatters.js'
import { AccountInput, FormError, fieldChange, emailPattern } from '../components/AuthComponents.jsx'

export default function ProfilePage({account,data,navigate,onSave,onLogout,onView}){
  const [editing,setEditing]=useState(false)
  const [form,setForm]=useState({nombre:account?.nombre||'',correo:account?.correo||''})
  const [error,setError]=useState('')
  const [saving,setSaving]=useState(false)

  useEffect(()=>{
    setForm({nombre:account?.nombre||'',correo:account?.correo||''})
    setEditing(false)
    setError('')
  },[account?.id])

  const mine=data.registros.filter(reg=>reg.usuarioId===account.usuarioId)
  const participating=new Set(mine.map(reg=>reg.retoId)).size
  const onChange=fieldChange(setForm)
  const submit=async event=>{
    event.preventDefault()
    setError('')
    if(form.nombre.trim().length<3){setError('El nombre debe tener al menos 3 caracteres.');return}
    if(!emailPattern.test(form.correo.trim())){setError('Ingresa un correo electrónico válido.');return}
    setSaving(true)
    const result=await onSave(form)
    if(result.ok)setEditing(false)
    else setError(result.message)
    setSaving(false)
  }

  return <div className="page profile-page">
    <div className="page-breadcrumb"><span>Mi espacio</span><ChevronRight size={14}/><strong>Mi perfil</strong></div>
    <div className="profile-title"><div><span className="eyebrow">TU ESPACIO PERSONAL</span><h1>Mi perfil</h1><p>Consulta tu actividad y mantén tu información actualizada.</p></div><button className="btn btn-outline" onClick={onLogout}><LogIn size={17}/> Cerrar sesión</button></div>
    <div className="profile-cover"><span className="profile-cover-sparkle">✳</span><div className="profile-cover-doodle">✦</div></div>
    <div className="profile-identity"><div className="profile-big-avatar">{initials(account.nombre)}</div><div className="profile-identity-text"><h2>{account.nombre} <BadgeCheck size={19}/></h2><span>{account.correo}</span><div className="profile-tags"><span><ShieldCheck size={13}/>{account.rol}</span><span><CalendarDays size={13}/> Miembro desde {formatDate(account.creadoEl)}</span></div></div><button className="btn btn-primary" onClick={()=>{setEditing(value=>!value);setError('')}}>{editing?<Pencil size={17}/>:<Pencil size={17}/>} {editing?'Cancelar':'Editar perfil'}</button></div>
    <div className="profile-stats"><div><span><Target size={20}/></span><strong>{participating}</strong><small>Retos en los que participas</small></div><div><span><ClipboardList size={20}/></span><strong>{mine.length}</strong><small>Inscripciones realizadas</small></div><div><span><CheckCircle2 size={20}/></span><strong>{mine.filter(reg=>reg.estado==='Aprobado').length}</strong><small>Inscripciones aprobadas</small></div></div>
    <div className="profile-columns">
      <section className="profile-panel"><div className="profile-panel-heading"><div><h3>Información personal</h3><p>Los datos de tu cuenta de usuario.</p></div>{editing&&<span className="profile-edit-label"><Pencil size={14}/> Editando</span>}</div>
        <form onSubmit={submit} className="profile-form"><div className="profile-form-grid"><AccountInput label="Nombre completo" icon={UserRound} name="nombre" value={form.nombre} onChange={onChange} disabled={!editing} required/><AccountInput label="Correo electrónico" icon={Mail} name="correo" type="email" value={form.correo} onChange={onChange} disabled={!editing}/></div>
        <FormError message={error}/>{editing&&<div className="profile-form-footer"><button type="button" className="btn btn-outline" disabled={saving} onClick={()=>{setEditing(false);setForm({nombre:account.nombre,correo:account.correo});setError('')}}>Cancelar</button><button className="btn btn-primary" type="submit" disabled={saving}><Save size={16}/> {saving?'Guardando...':'Guardar cambios'}</button></div>}
        </form>
      </section>
      <section className="profile-panel"><div className="profile-panel-heading"><div><h3>Mis inscripciones</h3><p>Los retos a los que te has unido.</p></div><span className="count-badge">{mine.length}</span></div>
        {mine.length? <div className="profile-enrollments">{mine.slice(0,5).map(reg=><button key={reg.id} onClick={()=>{const reto=data.retos.find(item=>item.id===reg.retoId);if(reto)onView(reto)}}><span className="profile-enrollment-icon"><Target size={18}/></span><span><strong>{getName(data,'retos',reg.retoId)}</strong><small>{formatDate(reg.fechaRegistro)} · {reg.estado}</small></span><ChevronRight size={17}/></button>)}</div>:<div className="profile-empty"><span><Target size={27}/></span><strong>Aún no tienes inscripciones</strong><p>Explora retos empresariales y participa en nuevas oportunidades.</p><button className="btn btn-outline" onClick={()=>navigate('retos')}>Explorar retos <ArrowRight size={16}/></button></div>}
        <div className="profile-safety-note"><ShieldCheck size={18}/><span>La información de tu cuenta se gestiona en el backend.</span></div>
      </section>
    </div>
  </div>
}
