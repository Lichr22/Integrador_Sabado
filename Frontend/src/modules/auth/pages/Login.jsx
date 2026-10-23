import React, { useEffect, useState } from 'react'
import { ArrowRight, CheckCircle2, ChevronRight, CircleAlert, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Sparkles, UserRound } from 'lucide-react'
import { AccountInput, AccountLayout, FormError, PasswordInput, emailPattern, fieldChange } from '../components/AuthComponents.jsx'

export default function LoginPage({navigate,onLogin,account}){
  const [form,setForm]=useState({correo:'',password:''})
  const [error,setError]=useState('')
  const [busy,setBusy]=useState(false)
  const onChange=event=>{fieldChange(setForm)(event);setError('')}
  const submit=async event=>{
    event.preventDefault();setError('')
    if (!emailPattern.test(form.correo.trim())) {setError('Ingresa un correo electrónico válido.');return}
    if (!form.password) {setError('Escribe tu contraseña.');return}
    setBusy(true)
    try {const result=await onLogin(form.correo,form.password);if(!result.ok) setError(result.message)}
    catch {setError('No fue posible validar la cuenta. Inténtalo nuevamente.')}
    finally {setBusy(false)}
  }
  return <AccountLayout mode="login" navigate={navigate}>
    <div className="account-card-tag"><span/> ACCESO A LA PLATAFORMA</div>
    <h1>¡Qué bueno verte de nuevo!</h1><p className="account-intro">Ingresa a tu cuenta y continúa construyendo soluciones para grandes desafíos.</p>
    {account&&<div className="account-session-hint"><UserRound size={16}/> Sesión actual: <strong>{account.nombre}</strong>. Puedes cambiar de cuenta.</div>}
    <form className="account-form" onSubmit={submit}>
      <AccountInput label="Correo electrónico" icon={Mail} name="correo" value={form.correo} onChange={onChange} type="email" placeholder="nombre@ejemplo.com" autoComplete="email"/>
      <PasswordInput value={form.password} onChange={onChange}/>
      <FormError message={error}/>
      <button className="account-submit" disabled={busy} type="submit">{busy?'Validando...':'Iniciar sesión'} <ArrowRight size={18}/></button>
    </form>
    <p className="account-switch">¿Aún no tienes una cuenta? <button onClick={()=>navigate('registro')}>Regístrate gratis</button></p>
    <div className="account-footnote"><ShieldCheck size={15}/> Inicio de sesión validado por el backend.</div>
  </AccountLayout>
}
