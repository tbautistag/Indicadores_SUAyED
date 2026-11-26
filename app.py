import streamlit as st
import pandas as pd
import csv, io, math, html
st.set_page_config(page_title='Indicadores SUAyED',layout='wide')
st.markdown('''<style>.stApp{--primary-color:#00356b} h1,h2,h3{color:#00356b!important} div[data-testid="stMetric"]{border:1px solid #d7c69c;border-radius:10px;padding:16px} </style><div style="background:#002b5c;color:white;padding:24px;border-radius:12px;border-bottom:5px solid #c49a42"><div style="color:#e7c980;font-size:14px">SUAyED · MODELO EDUCATIVO</div><div style="font-size:30px;font-weight:bold">Construcción y cálculo de indicadores</div><div>Metodología CONEVAL (2013) · pasos 8 y 9</div></div>''',unsafe_allow_html=True)
a,b,c=st.tabs(['1. Construcción','2. Cálculo y visualización','3. Validación y exportación'])
f={}
with a:
 st.subheader('Elementos del indicador')
 for k,h in [('Objetivo','¿Qué objetivo se desea medir?'),('Factor relevante','¿Qué aspecto esencial del objetivo se mide?'),('En quién se está midiendo','Identifica la población o unidad de análisis.'),('Universo','Delimita el conjunto de referencia y periodo.'),('Indicador','Escribe un nombre preciso y comprensible.')]:
  f[k]=st.text_area(k,help=h)
 f['Dimensión']=st.selectbox('Dimensión',['','Eficacia','Eficiencia','Calidad','Economía'])
 f['Cuál es la medición']=st.selectbox('Tipo de medición',['Porcentaje','Tasa de variación','Promedio','Índice'])
 f['Fórmula de cálculo']=st.text_input('Fórmula de cálculo (definición de variables)')
 f['Unidad de medida']=st.text_input('Unidad de medida')
 f['Frecuencia de medición']=st.text_input('Frecuencia de medición',placeholder='Ej. Semestral')
 f['Medios de verificación']=st.text_area('Medios de verificación',help='Identifica la fuente de cada variable con precisión.')
with b:
 st.subheader('Cálculo del indicador')
 t=f['Cuál es la medición']; r=None; x=y=None
 if t=='Índice': st.info('El índice requiere una metodología específica. Introduce el resultado obtenido mediante esa metodología.') ; r=st.number_input('Resultado del índice',value=None)
 else:
  labels={'Porcentaje':('Parte (numerador)','Total (denominador)'),'Tasa de variación':('Valor actual','Valor anterior'),'Promedio':('Suma de valores','Número de observaciones')}[t]
  p,q=st.columns(2)
  x=p.number_input(labels[0],value=None,key=t+'x'); y=q.number_input(labels[1],value=None,key=t+'y')
  if x is not None and y is not None:
   if y==0 or (t=='Porcentaje' and not 0<=x<=y) or (t=='Promedio' and (y<=0 or not float(y).is_integer())): st.error('Revisa los valores de las variables.')
   else: r=x/y*100 if t=='Porcentaje' else (x/y-1)*100 if t=='Tasa de variación' else x/y
 p,q=st.columns(2)
 base=p.number_input('Línea base',value=None,key=t+'base'); meta=q.number_input('Meta',value=None,key=t+'meta')
 f['Línea base']=base; f['Meta']=meta; f['Resultado calculado']=r
 unit='%' if t in ('Porcentaje','Tasa de variación') else ''
 def fmt(v): return 'Sin definir' if v is None else f'{v:,.2f}{unit}'
 if t=='Porcentaje' and any(v is not None and not 0<=v<=100 for v in (base,meta)): st.warning('Para este porcentaje, revisa que la línea base y la meta estén entre 0 y 100.')
 if r is not None:
  st.subheader(f['Indicador'] or 'Resultado del indicador')
  for col,(label,v) in zip(st.columns(3),[('Línea base',base),('Resultado',r),('Meta',meta)]): col.metric(label,fmt(v))
  data=[{'Referencia':k,'Valor':v} for k,v in [('Línea base',base),('Resultado',r),('Meta',meta)] if v is not None]
  spec={'mark':{'type':'bar','cornerRadiusTopLeft':5,'cornerRadiusTopRight':5},'encoding':{'x':{'field':'Referencia','type':'nominal','sort':['Línea base','Resultado','Meta'],'axis':{'labelAngle':0,'title':None}},'y':{'field':'Valor','type':'quantitative','scale':{'zero':True},'title':unit or f['Unidad de medida'] or 'Valor'},'color':{'field':'Referencia','type':'nominal','scale':{'domain':['Línea base','Resultado','Meta'],'range':['#94a3b8','#003b70','#c49a42']},'legend':None},'tooltip':[{'field':'Referencia'},{'field':'Valor','type':'quantitative','format':'.2f'}]}}
  st.vega_lite_chart(pd.DataFrame(data),spec,use_container_width=True)
  if t=='Porcentaje':
   angle=math.pi*(1-r/100); px=170+100*math.cos(angle); py=125-100*math.sin(angle)
   marker=''
   if meta is not None and 0<=meta<=100:
    m=math.pi*(1-meta/100); marker=f'<line x1="{170+87*math.cos(m)}" y1="{125-87*math.sin(m)}" x2="{170+113*math.cos(m)}" y2="{125-113*math.sin(m)}" stroke="#c49a42" stroke-width="5"/>'
   arc=f'<path d="M70 125 A100 100 0 0 1 {px} {py}" fill="none" stroke="#003b70" stroke-width="18"/>' if r>0 else ''
   st.markdown(f'<svg viewBox="0 0 340 155" style="width:100%;max-width:460px;display:block;margin:auto"><path d="M70 125 A100 100 0 0 1 270 125" fill="none" stroke="#dce3eb" stroke-width="18"/>{arc}{marker}<text x="170" y="110" text-anchor="middle" font-size="30" fill="#003b70">{r:.1f}%</text><text x="60" y="148" font-size="12">0%</text><text x="260" y="148" font-size="12">100%</text></svg>',unsafe_allow_html=True)
   st.caption('Azul: resultado · Dorado: meta (si está definida dentro de la escala).')
  suffix=' puntos porcentuales' if unit else ' unidades'
  if base is not None: st.write(f'Diferencia respecto a la línea base: {r-base:+.2f}{suffix}.')
  if meta is not None: st.write(f'Diferencia del resultado respecto a la meta: {r-meta:+.2f}{suffix}.')
 else: st.info('Completa las variables para obtener el resultado.')
with c:
 st.subheader('Criterios de validación CREMA')
 for k,h in [('Claridad','¿Es preciso y comprensible?'),('Relevancia','¿Mide un aspecto esencial del objetivo?'),('Economía','¿La información se obtiene a un costo razonable?'),('Monitoreable','¿Puede verificarse de manera independiente?'),('Adecuado','¿Ofrece una base suficiente para evaluar el desempeño?')]:
  st.write('**'+k+'** — '+h); f[k]=st.radio(k,['Sin revisar','Sí','No'],horizontal=True,label_visibility='collapsed',key=k)
 st.divider(); st.subheader('Ficha del indicador'); st.write(f['Indicador'] or 'Indicador sin definir')
 for col,(label,v) in zip(st.columns(3),[('Línea base',base),('Resultado',r),('Meta',meta)]): col.metric(label,fmt(v))
 st.table(pd.DataFrame([{'Elemento':k,'Descripción':str(v) if v is not None and v!='' else 'Sin definir'} for k,v in f.items() if k not in ('Línea base','Meta','Resultado calculado','Claridad','Relevancia','Economía','Monitoreable','Adecuado')]))
 st.table(pd.DataFrame([{'Criterio':k,'Valoración':f[k]} for k in ['Claridad','Relevancia','Economía','Monitoreable','Adecuado']]))
 st.caption('La valoración CREMA corresponde a la revisión de los participantes; no es una certificación automática.')
 out=io.StringIO(); w=csv.DictWriter(out,fieldnames=list(f)); w.writeheader(); w.writerow(f)
 st.download_button('Descargar ficha CSV',out.getvalue().encode('utf-8-sig'),'indicador.csv','text/csv')
 st.caption('Descarga la ficha antes de cerrar o actualizar la página. La aplicación no incluye almacenamiento permanente.')
