import streamlit as st
import csv, io, math
st.set_page_config(page_title='Indicadores CONEVAL', layout='wide')
st.title('Construcción y cálculo de indicadores')
st.caption('Taller SUAyED · CONEVAL (2013), pasos 8 y 9')
a,b,c=st.tabs(['Construcción','Cálculo y visualización','Validación y exportación'])
f={}
with a:
 for k in ['Objetivo','Factor relevante','En quién se está midiendo','Universo','Indicador']:
  f[k]=st.text_area(k)
 f['Dimensión']=st.selectbox('Dimensión',['','Eficacia','Eficiencia','Calidad','Economía'])
 f['Cuál es la medición']=st.selectbox('Tipo de medición',['Porcentaje','Tasa de variación','Promedio','Índice'])
 f['Fórmula de cálculo']=st.text_input('Fórmula de cálculo (definición de variables)')
 f['Unidad de medida']=st.text_input('Unidad de medida')
 f['Frecuencia de medición']=st.text_input('Frecuencia de medición')
 f['Medios de verificación']=st.text_area('Medios de verificación')
with b:
 t=f['Cuál es la medición']; r=None
 if t=='Índice': st.info('El índice requiere una metodología específica; no se calcula automáticamente.')
 else:
  labels={'Porcentaje':('Parte','Total'),'Tasa de variación':('Valor actual','Valor anterior'),'Promedio':('Suma de valores','Número de observaciones')}[t]
  x=st.number_input(labels[0],value=None); y=st.number_input(labels[1],value=None)
  if x is not None and y is not None:
   if y==0 or (t=='Porcentaje' and not 0<=x<=y) or (t=='Promedio' and (y<=0 or not float(y).is_integer())): st.error('Revisa los valores de las variables.')
   else: r=(x/y*100 if t=='Porcentaje' else (x/y-1)*100 if t=='Tasa de variación' else x/y)
 base=st.number_input('Línea base',value=None); meta=st.number_input('Meta',value=None)
 f['Línea base']=base; f['Meta']=meta
 if r is not None:
  st.metric('Resultado',f'{r:.2f}'+('%' if t!='Promedio' else ''))
  import pandas as pd
  st.bar_chart(pd.DataFrame({'Referencia':['Línea base','Resultado','Meta'],'Valor':[base,r,meta]}).dropna().set_index('Referencia'))
 f['Resultado calculado']=r
with c:
 for k in ['Claridad','Relevancia','Economía','Monitoreable','Adecuado']:
  f[k]=st.radio(k,['Sin revisar','Sí','No'],horizontal=True)
 st.write('Vista previa',f)
 out=io.StringIO(); w=csv.DictWriter(out,fieldnames=list(f)); w.writeheader(); w.writerow(f)
 st.download_button('Descargar ficha CSV',out.getvalue().encode('utf-8-sig'),'indicador.csv','text/csv')
