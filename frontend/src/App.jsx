import React, { useEffect, useState } from 'react';
import { Activity, HeartPulse, Brain, CalendarDays, ShieldAlert, MessageCircle, LayoutDashboard, UserRound, LogOut, Menu, Stethoscope, FileText, ChevronRight, Plus, Download, Send, Wind, CheckCircle2, Trash2 } from 'lucide-react';
import { api, setSession, clearSession, getToken } from './services/api';

const nav = [
  ['Overview', LayoutDashboard], ['Health check', Stethoscope], ['Wellness', Brain],
  ['Age guidance', Activity], ["Women's health", HeartPulse], ['Emergency', ShieldAlert],
  ['AI assistant', MessageCircle], ['My records', FileText], ['Profile', UserRound]
];

function Notice({children, tone='info'}) { return <div className={'notice '+tone}>{children}</div>; }
function Panel({title, subtitle, children}) { return <section className="panel"><div className="panel-head"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div></div>{children}</section>; }
function Btn({children, ...props}) { return <button className="btn" {...props}>{children}</button>; }
function Empty({children='Nothing saved here yet.'}) { return <div className="empty">{children}</div>; }

function Auth({onAuth}) {
  const [mode,setMode]=useState('login');
  const [form,setForm]=useState({full_name:'',email:'',password:'',age:'',age_group:'30-45',health_goal:'prevent',women_health_opt_in:false,privacy_consent:true});
  const [error,setError]=useState(''); const [busy,setBusy]=useState(false);
  const change=(k,v)=>setForm(f=>({...f,[k]:v}));
  async function submit(e){e.preventDefault();setBusy(true);setError('');try{
    const body={...form,age:form.age?Number(form.age):null};
    const result=await api('/api/auth/'+mode,{method:'POST',body:JSON.stringify(body)});
    setSession(result); onAuth(result.user);
  }catch(err){setError(err.message)}finally{setBusy(false)}}
  return <div className="auth-screen"><div className="auth-intro"><div className="brand-mark"><HeartPulse/></div><span className="eyebrow">YOUR PERSONAL WELLNESS COMPANION</span><h1>Health, made <em>clearer.</em></h1><p>A calm space to organize wellness check-ins, understand general health information, and build thoughtful daily habits.</p><div className="auth-points"><span>✦ Thoughtful insights</span><span>♡ Your privacy matters</span></div></div>
    <form className="auth-card" onSubmit={submit}><span className="eyebrow">{mode==='login'?'WELCOME BACK':'GET STARTED'}</span><h2>{mode==='login'?'Sign in to MediVision':'Create your account'}</h2>
      {mode==='register'&&<><label>Full name<input required value={form.full_name} onChange={e=>change('full_name',e.target.value)} /></label><div className="field-grid"><label>Age<input type="number" min="16" max="120" value={form.age} onChange={e=>change('age',e.target.value)}/></label><label>Age group<select value={form.age_group} onChange={e=>change('age_group',e.target.value)}><option>16-30</option><option>30-45</option><option>45+</option></select></label></div><label>Wellness goal<select value={form.health_goal} onChange={e=>change('health_goal',e.target.value)}><option value="prevent">Preventive wellness</option><option value="fitness">Improve fitness</option><option value="stress">Reduce stress</option><option value="senior">Senior care</option></select></label><label className="check"><input type="checkbox" checked={form.women_health_opt_in} onChange={e=>change('women_health_opt_in',e.target.checked)}/> Enable optional women's health tools</label><label className="check"><input type="checkbox" checked={form.privacy_consent} onChange={e=>change('privacy_consent',e.target.checked)}/> I consent to saving my account and wellness entries</label></>}
      <label>Email address<input type="email" required value={form.email} onChange={e=>change('email',e.target.value)} /></label><label>Password<input type="password" required minLength="8" value={form.password} onChange={e=>change('password',e.target.value)}/></label>
      {error&&<Notice tone="error">{error}</Notice>}<Btn disabled={busy}>{busy?'Please wait…':mode==='login'?'Sign in':'Create account'} <ChevronRight size={16}/></Btn><p className="switch">{mode==='login'?'New to MediVision?':'Already have an account?'} <button type="button" onClick={()=>{setMode(mode==='login'?'register':'login');setError('')}}>{mode==='login'?'Create account':'Sign in'}</button></p><small>Educational prototype only. Not a substitute for professional medical care.</small>
    </form></div>;
}

export default function App(){
  const [user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('mv_user'))}catch{return null}});
  const [page,setPage]=useState('Overview'); const [data,setData]=useState(null); const [toast,setToast]=useState(''); const [mobile,setMobile]=useState(false);
  const notify=(s)=>{setToast(s);setTimeout(()=>setToast(''),3000)};
  async function load(){
    if(!user)return;
    try{
      const path=page==='Overview'||page==='My records'?'/api/dashboard':
        page==='Health check'?'/api/diagnosis':
        page==='Wellness'?'/api/wellness':
        page==='Age guidance'?'/api/guidance/'+encodeURIComponent(user.age_group||'30-45'):
        page==="Women's health"?'/api/womens-health/cycles':
        page==='Emergency'?'/api/emergency/contacts':null;
      if(path)setData(await api(path));
    }catch(e){setData(page==="Women's health"?{locked:true}:[]);notify(e.message)}
  }
  useEffect(()=>{load()},[page,user]);
  function logout(){clearSession();localStorage.removeItem('mv_user');setUser(null);setData(null)}
  if(!getToken()||!user)return <Auth onAuth={u=>{setUser(u);localStorage.setItem('mv_user',JSON.stringify(u))}}/>;
  const PageIcon=nav.find(x=>x[0]===page)?.[1]||Activity;
  return <div className="app-shell">
    <aside className={'sidebar '+(mobile?'open':'')}><div className="brand"><div className="brand-mark"><HeartPulse/></div><div><b>MediVision</b><small>AI WELLNESS SPACE</small></div></div>
      <span className="nav-caption">YOUR SPACE</span>{nav.map(([name,Icon])=><button key={name} className={'nav-item '+(page===name?'active':'')} onClick={()=>{setPage(name);setMobile(false)}}><Icon size={18}/>{name}{page===name&&<span className="nav-dot"/>}</button>)}
      <div className="sidebar-bottom"><div className="user-mini"><div className="avatar">{user.full_name?.[0]||'U'}</div><div><b>{user.full_name}</b><small>{user.age_group} age group</small></div></div><button className="logout" onClick={logout}><LogOut size={16}/> Sign out</button></div>
    </aside>
    <main className="main"><header className="topbar"><button className="mobile-menu" onClick={()=>setMobile(!mobile)}><Menu/></button><div><span className="eyebrow">YOUR WELLNESS JOURNEY</span><h1>{page}</h1></div><div className="top-user"><span className="status-dot"/> Personal space <div className="avatar">{user.full_name?.[0]||'U'}</div></div></header>
      <div className="content">
        {page==='Overview'&&<><div className="hero"><div><span className="eyebrow">A LITTLE CARE, EVERY DAY</span><h2>Make space for your health.</h2><p>Small check-ins today can help you notice patterns over time.</p><Btn onClick={()=>setPage('Wellness')}>Do a daily check-in <ChevronRight size={16}/></Btn></div><div className="hero-art"><div className="hero-sun"/><HeartPulse size={66}/></div></div>
          <div className="stat-grid"><div className="stat"><Brain/><span>Wellness check-ins</span><b>{data?.wellness_count??'—'}</b></div><div className="stat"><Stethoscope/><span>Health check notes</span><b>{data?.diagnosis_count??'—'}</b></div><div className="stat"><HeartPulse/><span>Latest stress index</span><b>{data?.latest_wellness?data.latest_wellness.stress_score+'/100':'—'}</b></div></div>
          <Panel title="Explore your wellness space" subtitle="Tools to support your everyday health"><div className="feature-grid">{nav.slice(1,7).map(([n,I])=><button className="feature" key={n} onClick={()=>setPage(n)}><I/><b>{n}</b><small>Open your {n.toLowerCase()} space</small><ChevronRight size={15}/></button>)}</div></Panel>
          <Notice>For emergencies or severe symptoms, contact local emergency services. MediVision does not dispatch emergency help.</Notice>
        </>}
        {page==='Health check'&&<HealthCheck notify={notify} data={data} refresh={load}/>}
        {page==='Wellness'&&<Wellness notify={notify} data={data} refresh={load}/>}
        {page==='Age guidance'&&<Panel title={data?.title||'Everyday movement'} subtitle={'General ideas for age group '+user.age_group}><ul className="guide-list">{(data?.items||[]).map((x,i)=><li key={i}><CheckCircle2/>{x}</li>)}</ul><Notice>{data?.notice||'General wellness education only; not personal exercise clearance.'}</Notice></Panel>}
        {page==="Women's health"&&<WomenHealth notify={notify} data={data} refresh={load}/>}
        {page==='Emergency'&&<Emergency notify={notify} data={data} refresh={load}/>}
        {page==='AI assistant'&&<Assistant/>}
        {page==='My records'&&<Records data={data}/>}
        {page==='Profile'&&<Profile user={user} notify={notify} onUpdate={u=>{setUser(u);localStorage.setItem('mv_user',JSON.stringify(u))}}/>}
      </div>
      <footer className="footer">© 2026 MediVision AI <span>Designed for informed wellness · Not a diagnostic device</span></footer>
    </main>{toast&&<div className="toast">{toast}</div>}
  </div>;
}

function HealthCheck({notify,data,refresh}){
 const [symptoms,S]=useState(''),[category,C]=useState('symptom-check'),[file,F]=useState(null),[result,R]=useState(null),[busy,B]=useState(false);
 async function submit(e){e.preventDefault();B(true);try{const f=new FormData();f.append('symptoms',symptoms);f.append('category',category);if(file)f.append('file',file);R(await api('/api/diagnosis',{method:'POST',body:f}));S('');F(null);notify('Health note saved');refresh()}catch(e){notify(e.message)}finally{B(false)}}
 return <div className="two-col"><Panel title="Start a health check" subtitle="Describe what you're experiencing"><form onSubmit={submit}><label>What would you like to record?<select value={category} onChange={e=>C(e.target.value)}><option value="symptom-check">Symptoms</option><option value="skin-image">Skin image (record only)</option><option value="xray">X-ray / scan (record only)</option><option value="report">Medical report</option></select></label><label>Symptoms or question<textarea required minLength={3} maxLength={3000} value={symptoms} onChange={e=>S(e.target.value)} placeholder="When did it start? What are you feeling?"/></label><label className="upload">Attach image or PDF (optional)<input type="file" accept=".png,.jpg,.jpeg,.webp,.pdf" onChange={e=>F(e.target.files?.[0]||null)}/><small>{file?.name||'PNG, JPG, WEBP or PDF · up to 8 MB'}</small></label><Btn disabled={busy}>{busy?'Saving…':'Save health note'} <ChevronRight size={16}/></Btn></form>{result&&<Notice tone="success"><b>{result.severity}</b><p>{result.guidance}</p>{result.medical_notice}</Notice>}</Panel><Panel title="Important safety note"><Notice tone="warning">This feature records symptoms and provides general safety guidance only. It does not analyze images, diagnose disease, or replace a clinician.</Notice><p className="muted">Seek urgent medical help for severe breathing difficulty, chest pain, stroke-like symptoms, severe bleeding or loss of consciousness.</p></Panel></div>;
}
function Wellness({notify,data,refresh}){
 const [mood,M]=useState('Normal'),[sleep,S]=useState('7'),[note,N]=useState(''),[saved,V]=useState(null);
 async function submit(e){e.preventDefault();try{V(await api('/api/wellness',{method:'POST',body:JSON.stringify({mood,sleep_hours:Number(sleep),note})}));N('');notify('Daily check-in saved');refresh()}catch(e){notify(e.message)}}
 return <div className="two-col"><Panel title="How are you feeling today?" subtitle="A small moment to check in with yourself"><form onSubmit={submit}><label>Mood<select value={mood} onChange={e=>M(e.target.value)}>{['Happy','Normal','Stressed','Low','Anxious'].map(x=><option key={x}>{x}</option>)}</select></label><label>Hours of sleep<input type="number" min="0" max="24" step=".5" value={sleep} onChange={e=>S(e.target.value)}/></label><label>Anything you'd like to note?<textarea value={note} onChange={e=>N(e.target.value)} /></label><Btn>Save daily check-in <ChevronRight size={16}/></Btn></form>{saved&&<Notice tone="success">Estimated stress index: {saved.stress_score}/100. {saved.suggestion}<small>Not a validated mental-health assessment.</small></Notice>}</Panel><Panel title="A moment to breathe"><Wind size={28}/><p>Try a gentle paced-breathing exercise. Stop if you feel uncomfortable.</p><Notice>Take a slow breath in, pause comfortably, and breathe out gently. Repeat only as comfortable.</Notice></Panel></div>;
}
function WomenHealth({notify,data,refresh}){
 const [date,D]=useState(''),[length,L]=useState('28'),[notes,N]=useState('');
 if(data?.locked)return <Notice tone="warning">This module is optional and currently disabled. Enable women's health tools in Profile settings to use cycle tracking.</Notice>;
 async function add(e){e.preventDefault();try{await api('/api/womens-health/cycles',{method:'POST',body:JSON.stringify({start_date:date,cycle_length:Number(length),notes})});D('');N('');notify('Cycle entry saved');refresh()}catch(e){notify(e.message)}}
 return <div className="two-col"><Panel title="Cycle tracking" subtitle="Record dates and notice patterns over time"><form onSubmit={add}><label>Period start date<input type="date" required value={date} onChange={e=>D(e.target.value)}/></label><label>Typical cycle length (days)<input type="number" min="15" max="60" value={length} onChange={e=>L(e.target.value)}/></label><label>Notes<textarea value={notes} onChange={e=>N(e.target.value)} /></label><Btn>Save cycle entry</Btn></form><Notice>Cycle estimates are approximate and are not diagnosis or medical advice.</Notice></Panel><Panel title="Awareness library"><p>PCOS symptoms have several possible causes. An app cannot diagnose PCOS; discuss concerns with a qualified clinician.</p><p>For pregnancy-specific advice, consult an obstetric professional.</p>{data?.map?.(x=><p key={x.id}>{x.start_date} · {x.cycle_length} day cycle</p>)}</Panel></div>;
}
function Emergency({notify,data,refresh}){
 const [name,N]=useState(''),[relationship,R]=useState(''),[phone,P]=useState('');
 async function add(e){e.preventDefault();try{await api('/api/emergency/contacts',{method:'POST',body:JSON.stringify({name,relationship,phone})});N('');R('');P('');notify('Emergency contact saved');refresh()}catch(e){notify(e.message)}}
 async function del(id){try{await api('/api/emergency/contacts/'+id,{method:'DELETE'});refresh()}catch(e){notify(e.message)}}
 return <div className="two-col"><Panel title="Emergency preparedness"><Notice tone="warning">This button does not call, message or dispatch emergency services. In an emergency, call your local emergency number directly.</Notice><p>In India, call 112 for pan-India emergency response.</p><a href="https://112.gov.in/" target="_blank" rel="noreferrer">India emergency response · 112</a></Panel><Panel title="Emergency contacts"><form onSubmit={add}><label>Name<input required value={name} onChange={e=>N(e.target.value)}/></label><label>Relationship<input required value={relationship} onChange={e=>R(e.target.value)}/></label><label>Phone<input required value={phone} onChange={e=>P(e.target.value)}/></label><Btn><Plus size={16}/> Add contact</Btn></form>{(data||[]).map(c=><div className="record" key={c.id}><b>{c.name}</b><span>{c.relationship} · {c.phone}</span><button onClick={()=>del(c.id)}><Trash2 size={16}/></button></div>)}</Panel></div>;
}
function Assistant(){
 const [message,M]=useState(''),[history,H]=useState([]),[busy,B]=useState(false);
 async function send(e){e.preventDefault();if(!message.trim())return;const q=message;H(h=>[...h,{role:'you',text:q}]);M('');B(true);try{const r=await api('/api/assistant/chat',{method:'POST',body:JSON.stringify({message:q})});H(h=>[...h,{role:'assistant',text:r.answer,sources:r.sources||[]}])}catch(err){H(h=>[...h,{role:'assistant',text:err.message}])}finally{B(false)}}
 return <div className="two-col"><Panel title="MediVision health assistant" subtitle="General health education · References shown where available"><div className="chat-log">{history.length===0&&<p className="muted">Ask a general wellness question. The assistant uses a small curated reference library.</p>}{history.map((m,i)=><div className={'bubble '+m.role} key={i}><b>{m.role==='you'?'You':'Assistant'}</b><p>{m.text}</p>{m.sources?.map((s,j)=><a key={j} href={s.url} target="_blank" rel="noreferrer">{s.title} ↗</a>)}</div>)}</div><form className="chat-form" onSubmit={send}><input value={message} onChange={e=>M(e.target.value)} placeholder="Ask a wellness question…"/><Btn disabled={busy}><Send size={16}/></Btn></form></Panel><Panel title="Helpful, with boundaries"><p>The assistant is designed for general health education. It does not diagnose, prescribe, or replace a qualified professional.</p><Notice tone="warning">For a possible emergency, do not wait for a chatbot reply. Contact local emergency services.</Notice></Panel></div>;
}
function Records({data}){
 return <Panel title="Your wellness history" subtitle="A personal summary of information stored in your account"><Notice>This is a user-entered wellness summary, not a formal medical record.</Notice><h3>Recent health notes</h3>{data?.recent_records?.length?data.recent_records.map(r=><div className="record" key={r.id}><b>{r.symptoms}</b><span>{r.severity}</span></div>):<Empty/>}<Btn onClick={async()=>{try{const t=await api('/api/reports/summary.txt');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/plain'}));a.download='medivision-summary.txt';a.click();URL.revokeObjectURL(a.href)}catch(e){alert(e.message)}}}><Download size={16}/> Download summary</Btn></Panel>;
}
function Profile({user,notify,onUpdate}){
 const [form,F]=useState({...user});const change=(k,v)=>F(f=>({...f,[k]:v}));
 async function save(e){e.preventDefault();try{const r=await api('/api/profile',{method:'PUT',body:JSON.stringify(form)});onUpdate(r);notify('Profile updated')}catch(e){notify(e.message)}}
 return <div className="two-col"><Panel title="Your profile" subtitle="Update your preferences"><form onSubmit={save}><label>Full name<input value={form.full_name||''} onChange={e=>change('full_name',e.target.value)}/></label><label>Age group<select value={form.age_group||'30-45'} onChange={e=>change('age_group',e.target.value)}><option>16-30</option><option>30-45</option><option>45+</option></select></label><label>Health goal<select value={form.health_goal||'prevent'} onChange={e=>change('health_goal',e.target.value)}><option value="prevent">Preventive wellness</option><option value="fitness">Fitness</option><option value="stress">Stress reduction</option><option value="senior">Senior care</option></select></label><label className="check"><input type="checkbox" checked={!!form.women_health_opt_in} onChange={e=>change('women_health_opt_in',e.target.checked)}/> Enable optional women's health tools</label><Btn>Save profile</Btn></form></Panel><Panel title="Privacy and safety"><p>Use synthetic demo data only. This prototype needs a formal privacy and security review before any real patient information is used.</p></Panel></div>;
}
