# 📊 Análisis de Contratación Pública SECOP - Colombia

<div align="center">
  <h2>🇨🇴 Datos Abiertos del Gobierno Colombiano</h2>
  <p><strong>Tutorial completo para analizar contratos públicos con Python</strong></p>
  
  ![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
  ![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green?style=for-the-badge&logo=pandas)
  ![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange?style=for-the-badge&logo=python)
  ![Nivel](https://img.shields.io/badge/Nivel-Principiante-brightgreen?style=for-the-badge&logo=star)
</div>

---

## 🎯 Una aventura real con datos del gobierno colombiano

¿Alguna vez te has preguntado cómo funciona realmente la contratación pública en Colombia? Este proyecto te lleva de la mano a través del fascinante mundo de los **datos abiertos gubernamentales**, utilizando información real del sistema SECOP (Sistema Electrónico de Contratación Pública).

Lo que hace especial a este análisis es que trabajarás con **datos reales y actuales** del gobierno colombiano, no con ejemplos académicos. Aprenderás a enfrentarte a los desafíos que tienen los analistas de datos en el mundo real: información incompleta, valores corruptos, y datasets masivos.

**🎓 Habilidades que desarrollarás:**
- Limpieza de datos complejos con valores mixtos
- Filtrado temporal para trabajar con datos de calidad (2021+)
- Análisis exploratorio de datasets gubernamentales
- Visualización profesional con matplotlib
- Detección de patrones en la contratación pública
- Análisis de proveedores y mercado público

---

## 🚀 Un recorrido paso a paso por el análisis

Este proyecto te guía a través de un proceso completo de análisis de datos, desde la descarga hasta los insights finales. **No es solo un tutorial técnico**, sino una experiencia de aprendizaje que simula el trabajo real de un analista de datos en el sector público.

### **🔍 1. El reto de los datos reales**

Cuando trabajamos con datos del mundo real, especialmente gubernamentales, nos enfrentamos a desafíos únicos. Los valores monetarios vienen mezclados con texto, las fechas tienen formatos inconsistentes, y hay información duplicada.

```python
# Ejemplo de limpieza automática incluida
def limpiar_valor_monetario(valor):
    # Convierte texto corrupto en números utilizables
    # Maneja casos especiales y errores comunes
```

### **📊 2. Análisis temporal profundo** 

Exploraremos los **patrones temporales de la contratación pública**. ¿Sabías que hay meses del año en los que se firman significativamente más contratos?

- **Contratos por año y mes:** Identifica patrones estacionales
- **Duración de contratos:** Calcula promedios y tendencias  
- **Valor total por período:** Analiza el gasto público anual

### **🏢 3. El mapa sectorial del Estado**

Colombia invierte recursos públicos en una amplia variedad de sectores. Construirás visualizaciones que revelan cómo se distribuye el presupuesto público:

- **Sector Transporte:** ~48% de los contratos
- **Tecnologías de Información:** ~22% del mercado  
- **Inclusión Social:** ~13% de participación

### **🏪 4. El ecosistema de proveedores**

Explorarás el fascinante mundo de los proveedores del Estado. ¿Hay una concentración excesiva en pocos proveedores, o existe una competencia saludable?

- PYMES vs Grandes empresas: Participación en el mercado
- Top proveedores por cantidad y valor de contratos  
- Índices de concentración para evaluar competencia

---

## 🛠️ **Configuración súper sencilla**

**La buena noticia es que no necesitas instalar nada en tu computadora.** Este proyecto está diseñado para funcionar completamente en la nube usando Google Colab, la plataforma gratuita de Google para análisis de datos.

### **🌐 Opción recomendada: Google Colab**
1. Ve a [Google Colab](https://colab.research.google.com)
2. Sube el archivo `analisis_secop_completo.ipynb`
3. ¡Ejecuta celda por celda y aprende!

### **💻 Opción avanzada: Local con Jupyter**
Si prefieres trabajar en tu máquina:
```bash
pip install pandas numpy matplotlib requests
jupyter notebook analisis_secop_completo.ipynb
```

**📁 Estructura del proyecto:**
```
📁 analisis-secop/
├── 📄 README.md                           # Este archivo
├── 📁 Codigo/                            # Carpeta con códigos
│   ├── 📓 analisis_secop_completo.ipynb  # Notebook principal 
│   └── 🐍 analisis_secop_completo.py     # Código Python limpio
├── 📁 Graficas/                          # Carpeta con gráficas generadas
│   ├── 📊 contratos_por_año.png          # Gráfico de barras temporal
│   ├── 📈 tendencias_temporales.png      # Líneas de tiempo
│   └── 🥧 distribucion_sectores.png      # Gráfico de torta sectorial
└── 📁 Datos/                            # Carpeta con datasets procesados
    ├── 📋 contratos_limpios.csv          # Datos después de limpieza
    └── 📊 resumen_estadistico.xlsx       # Estadísticas principales
```
---

## 🎓 **Tecnologías que dominarás**

**Este no es un curso teórico**, es una experiencia práctica donde aprenderás haciendo. Cada concepto se introduce justo cuando lo necesitas, siguiendo una metodología de aprendizaje basada en proyectos.

### **🐍 Python para análisis de datos**
Python se ha convertido en el lenguaje preferido para ciencia de datos por una razón: es poderoso pero accesible. El código está completamente comentado y entenderás **por qué** hacemos cada paso, no solo **cómo**.

### **🐼 Pandas: Excel con superpoderes**  
- Carga de datos desde URLs del gobierno
- Filtrado y selección de información compleja
- Agrupación y agregación de estadísticas
- Manejo profesional de fechas y valores monetarios

### **📊 Matplotlib: visualizaciones que cuentan historias**
- Gráficos de líneas para tendencias temporales
- Gráficos de barras para comparaciones sectoriales  
- Gráficos de torta con leyendas profesionales
- Paletas de colores institucionales

---

## 📖 **Tu recorrido de aprendizaje**

### **⚡ Paso 1: Preparación (5 minutos)**
El notebook instala automáticamente todas las librerías necesarias. También te explica qué hace cada herramienta para que entiendas tu arsenal de análisis.

```python
# Configuración automática
import pandas as pd
import matplotlib.pyplot as plt
```

### **🌐 Paso 2: Conexión con datos reales (10 minutos)**
Te conectarás directamente con los servidores del gobierno colombiano para descargar más de 100,000 contratos. Es emocionante trabajar con los mismos datos que usan los funcionarios públicos.

### **🧹 Paso 3: Limpieza de datos (15 minutos)**
Los datos del mundo real son desordenados. Aprenderás técnicas profesionales para convertir información corrupta en datos utilizables. Esta es la parte más valiosa del aprendizaje.

### **📈 Paso 4: Análisis temporal (20 minutos)**  
- Patrones estacionales de contratación
- Tendencias anuales en el gasto público
- Duración promedio de contratos por sector

### **🏢 Paso 5: Análisis sectorial (20 minutos)**
- Distribución del presupuesto público por sectores
- Gráficos de torta con leyendas claras
- Ranking de sectores por valor contratado

### **🏪 Paso 6: Ecosistema de proveedores (20 minutos)**
- Participación de PYMES vs grandes empresas
- Top proveedores por volumen y valor
- Índices de concentración de mercado

---

## 🔍 **Dataset: Contratos Públicos SECOP**

Trabajaremos con información del **Sistema Electrónico de Contratación Pública**, la plataforma oficial donde el gobierno colombiano registra todos sus contratos. Esta base de datos contiene más de 100,000 registros desde 2021.

**📊 Variables principales:**
| Variable | Descripción | Uso en el análisis |
|----------|-------------|-------------------|
| `fecha_de_firma` | Cuándo se firmó el contrato | Análisis temporal |
| `valor_del_contrato` | Monto en pesos colombianos | Estudios financieros |
| `sector` | Sector económico del contrato | Distribución sectorial |
| `proveedor_adjudicado` | Empresa contratada | Análisis de mercado |
| `es_pyme` | Si es pequeña empresa | Políticas de inclusión |

---

## 🚨 **Problemas comunes (y sus soluciones)**

### **Error: 'fecha_firma' no existe**
**Problema:** Usaste el nombre incorrecto de la columna.  
**Solución:** Usa `fecha_de_firma` (con guiones bajos).

### **Error: No se pueden convertir valores monetarios**
**Problema:** Los datos vienen con texto mezclado.  
**Solución:** El notebook incluye una función `limpiar_valor_monetario()` que resuelve esto automáticamente.

### **Gráficos saturados con muchas categorías**
**Problema:** Demasiadas categorías pequeñas en gráficos de torta.  
**Solución:** Usa solo el top 5-7 elementos y agrupa el resto como "Otros".

### **ModuleNotFoundError**
**Problema:** Falta una librería.  
**Solución:** Ejecuta `!pip install nombre_libreria` en una celda.

---

## 🎯 **Lo que lograrás al final**

Al completar este análisis, tendrás habilidades tangibles y resultados concretos que puedes mostrar con orgullo.

### **🏆 Resultados tangibles:**
- Análisis completo de +100,000 contratos públicos
- 6-8 visualizaciones profesionales listas para presentar
- Insights sobre patrones de contratación gubernamental
- Código reutilizable para otros datasets similares

### **💼 Habilidades profesionales:**
- Limpieza y procesamiento de datos complejos
- Visualización de información para audiencias ejecutivas
- Análisis exploratorio de datasets gubernamentales  
- Pensamiento analítico aplicado a políticas públicas

**Nivel alcanzado:** De Principiante a **Analista Junior de Datos Públicos**

---

## 🌟 **Siguientes pasos**

Una vez completado este análisis, estarás listo para expandir tus conocimientos y aplicar lo aprendido a nuevos desafíos.

### **📚 Expandir tu análisis:**
- Incluir departamentos específicos de Colombia
- Comparar con datos de años anteriores
- Desarrollar indicadores de eficiencia gubernamental

### **🔧 Mejorar técnicamente:**
- Automatizar la descarga de datos actualizados
- Crear dashboards interactivos con Streamlit
- Implementar análisis predictivo con machine learning

### **🎓 Continuar aprendiendo:**
- Análisis estadístico avanzado con SciPy
- Machine Learning para predicciones gubernamentales
- Visualización interactiva con Plotly Dash

---

## 🤝 **Contribuciones bienvenidas**

Este proyecto está en constante mejora. **¿Tienes ideas? ¿Encontraste algo interesante?**

- 🍴 Fork del repositorio
- 🌿 Crea tu rama: `git checkout -b mi-mejora`
- 📝 Haz tus cambios y mejoras  
- 📤 Pull Request con descripción clara

**Ideas que necesitamos:**
- Nuevas visualizaciones creativas
- Análisis de otros aspectos (transparencia, eficiencia)
- Mejoras en la limpieza de datos
- Documentación más clara para principiantes

---

<div align="center">
  
## 🎉 **¡Felicitaciones por completar el análisis!**

**Has desarrollado habilidades valiosas en:**
- 🏛️ Análisis de políticas públicas
- 📊 Ciencia de datos aplicada
- 🔍 Investigación con datos gubernamentales
- 🏢 Consultoría basada en evidencia

### 🚀 **¡Comparte tu trabajo!**
*#AnálisisDatos #Python #DatosAbiertos #SECOP #Colombia*

---

<p><em>Hecho con ❤️ para la transparencia y el aprendizaje</em></p>
<p><strong>🇨🇴 Datos del pueblo, para el pueblo</strong></p>

</div>
