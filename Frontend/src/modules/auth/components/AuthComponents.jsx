import React, { useState } from 'react'
import { ArrowLeft, CheckCircle2, ChevronRight, CircleAlert, Eye, EyeOff, LockKeyhole, Sparkles } from 'lucide-react'
export const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
export const fieldChange = setter => event => setter(prev=>({...prev,[event.target.name]:event.target.value}))

export function AuthLogo(){return <div className="auth-mark"><span>✳</span></div>}
export function FormError({message}){return message?<div className="account-alert" role="alert"><CircleAlert size={17}/><span>{message}</span></div>:null}
export function AccountInput({label,icon:Icon, name, value, onChange, type='text', placeholder, autoComplete, required=true, extra, disabled=false}){
  return <label className="account-field"><span className="account-field-name">{label}</span><span className="account-input-wrap"><Icon size={17}/><input id={`account-${name}`} type={type} name={name} value={value} onChange={onChange} placeholder={placeholder} autoComplete={autoComplete} required={required} disabled={disabled}/>{extra}</span></label>
}
export function PasswordInput({label='Contraseña',name='password',value,onChange,autoComplete='current-password'}){
  const [visible,setVisible]=useState(false)
  return <AccountInput label={label} name={name} value={value} onChange={onChange} icon={LockKeyhole} type={visible?'text':'password'} placeholder="••••••••" autoComplete={autoComplete} extra={<button className="account-visibility" type="button" onClick={()=>setVisible(v=>!v)} aria-label={visible?'Ocultar contraseña':'Mostrar contraseña'} title={visible?'Ocultar contraseña':'Mostrar contraseña'}>{visible?<EyeOff size={17}/>:<Eye size={17}/>}</button>}/>
}
export function AccountLayout({mode,navigate,children}){
  const isRegister=mode==='registro'
  return <div className="page account-page">
    <div className="page-breadcrumb"><button className="account-back" onClick={()=>navigate('dashboard')}><ArrowLeft size={15}/> Volver al inicio</button><ChevronRight size={14}/><strong>{isRegister?'Crear cuenta':'Iniciar sesión'}</strong></div>
    <div className="account-layout">
      <section className="account-showcase">
        <span className="account-showcase-label"><Sparkles size={16}/> TU ESPACIO DE INNOVACIÓN</span>
        <div className="account-showcase-content"><AuthLogo/><h2>Las ideas crecen<br/>cuando nos <em>conectamos.</em></h2><p>Empresas, talento y desafíos reales en un solo lugar. Descubre oportunidades y transforma cada reto en una posibilidad.</p>
          <div className="account-showcase-features"><span><CheckCircle2 size={17}/> Explora retos empresariales</span><span><CheckCircle2 size={17}/> Participa en proyectos de impacto</span><span><CheckCircle2 size={17}/> Gestiona tu actividad</span></div>
        </div>
        <div className="account-showcase-foot"><div className="account-showcase-avatars"><b>VP</b><b>MH</b><b>IR</b></div><span>Una comunidad para crear soluciones juntos.</span></div>
        <span className="account-orbit account-orbit-a"/><span className="account-orbit account-orbit-b"/>
      </section>
      <section className="account-card">{children}</section>
    </div>
  </div>
}

