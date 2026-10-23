import React, { useEffect, useState } from 'react'
import { ArrowRight, Mail, ShieldCheck, UserRound } from 'lucide-react'
import { AccountInput, AccountLayout, FormError, PasswordInput, emailPattern, fieldChange } from '../components/AuthComponents.jsx'

export default function RegisterPage({navigate,onRegister}){
  const [form,setForm]=useState({nombre:'',correo:'',password:'',confirmPassword:''})
  const [error,setError]=useState('')
  const [busy,setBusy]=useState(false)
  const [agreed,setAgreed]=useState(false)
  const onChange=event=>{fieldChange(setForm)(event);setError('')}
  const submit=async event=>{
    event.preventDefault();setError('')
    if (form.nombre.trim().length<3){setError('Escribe tu nombre completo (mínimo 3 caracteres).');return}
    if(!emailPattern.test(form.correo.trim())){setError('Ingresa un correo electrónico válido.');return}
    if(form.password.length<8){setError('La contraseña debe contener al menos 8 caracteres.');return}
    if(form.password!==form.confirmPassword){setError('Las contraseñas no coinciden.');return}
    if(!agreed){setError('Confirma que autorizas el envío de tus datos para crear la cuenta.');return}
    setBusy(true)
    try {const result=await onRegister(form);if(!result.ok)setError(result.message)}
    catch {setError('No fue posible crear la cuenta. Inténtalo nuevamente.')}
    finally {setBusy(false)}
  }
  return <AccountLayout mode="registro" navigate={navigate}>
    <div className="account-card-tag"><span/> ÚNETE A LA COMUNIDAD</div><h1>Crea tu cuenta.</h1><p className="account-intro">Empieza a explorar, conectar y participar en los retos que mueven la innovación.</p>
    <form className="account-form" onSubmit={submit}>
      <AccountInput label="Nombre completo" icon={UserRound} name="nombre" value={form.nombre} onChange={onChange} placeholder="Tu nombre y apellido" autoComplete="name"/>
      <AccountInput label="Correo electrónico" icon={Mail} name="correo" value={form.correo} onChange={onChange} type="email" placeholder="nombre@ejemplo.com" autoComplete="email"/>
      <div className="account-password-row"><PasswordInput label="Contraseña" value={form.password} onChange={onChange} autoComplete="new-password"/><PasswordInput label="Confirmar contraseña" name="confirmPassword" value={form.confirmPassword} onChange={onChange} autoComplete="new-password"/></div>
      <p className="account-password-note"><ShieldCheck size={14}/> Mínimo 8 caracteres. Evita reutilizar contraseñas de otros servicios.</p>
      <label className="account-agree"><input type="checkbox" checked={agreed} onChange={event=>setAgreed(event.target.checked)}/><span>Autorizo el envío de mis datos al backend para crear mi cuenta.</span></label>
      <FormError message={error}/>
      <button className="account-submit" disabled={busy} type="submit">{busy?'Creando cuenta...':'Crear mi cuenta'} <ArrowRight size={18}/></button>
    </form>
    <p className="account-switch">¿Ya tienes una cuenta? <button onClick={()=>navigate('login')}>Inicia sesión</button></p>
  </AccountLayout>
}
