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

## 🎯 ¿Qué vas a aprender?

### **Análisis Real de Datos Públicos**
Este proyecto te enseña a analizar **datos reales de contratación pública de Colombia** usando el sistema SECOP (Sistema Electrónico de Contratación Pública).

### **Habilidades que desarrollarás:**
- ✅ **Limpieza de datos** complejos con valores mixtos
- ✅ **Filtrado temporal** para trabajar con datos de calidad (2021+)
- ✅ **Análisis exploratorio** de datasets gubernamentales
- ✅ **Visualización profesional** con matplotlib
- ✅ **Detección de patrones** en la contratación pública
- ✅ **Análisis de proveedores** y mercado público

---

## 🚀 ¿Qué hace este análisis?

### **1. 📥 Carga y Limpieza de Datos**
```python
# Descarga datos reales del gobierno colombiano
# Limpia valores monetarios con caracteres especiales  
# Filtra datos desde 2021 para mayor calidad
```

### **2. 📊 Análisis Temporal**
- **Contratos por año y mes:** Identifica patrones estacionales
- **Duración de contratos:** Calcula promedios y tendencias  
- **Valor total por período:** Analiza el gasto público anual

### **3. 🏢 Análisis por Sectores**
- **Distribución sectorial:** ¿Qué sectores contratan más?
- **Gráficos de torta mejorados:** Visualización clara con leyendas
- **Ranking de sectores:** Por número y valor de contratos

### **4. 🏪 Análisis de Proveedores**
- **PYMES vs Grandes empresas:** Participación en el mercado
- **Top proveedores:** Por cantidad y valor de contratos
- **Concentración de mercado:** Índices de competencia

### **5. 📈 Visualizaciones Profesionales**
- **Gráficos de líneas** para tendencias temporales
- **Gráficos de barras** para comparaciones
- **Gráficos de torta** con paletas de colores profesionales
- **Distribuciones estadísticas** para detectar anomalías

---

## 🛠️ **Configuración Inicial**

### **Opción 1: Google Colab (Recomendado para principiantes)**
1. Ve a [Google Colab](https://colab.research.google.com)
2. Sube el archivo `analisis_secop_completo.ipynb`
3. ¡Ejecuta y aprende!

### **Opción 2: Local con Jupyter**
```bash
# Instalar dependencias
pip install pandas numpy matplotlib requests

# Ejecutar Jupyter
jupyter notebook analisis_secop_completo.ipynb
```

---

## 📂 **Estructura del Proyecto**

```
📁 analisis-secop/
├── 📄 README.md                      # Este archivo
├── 📓 analisis_secop_completo.ipynb  # Notebook principal 
├── 🐍 analisis_secop_completo.py     # Código Python limpio
└── 📊 visualizaciones/               # Gráficos generados
```

---

## 🎓 **Conceptos que aprenderás**

### **🐍 Python para Datos**
- Variables y tipos de datos
- Estructuras de control
- Funciones de limpieza de datos

### **🐼 Pandas Avanzado**
- Carga de datos desde URLs
- Filtrado y selección de datos
- Agrupación y agregación
- Manejo de fechas y tiempo

### **📊 Visualización con Matplotlib**
- Gráficos de barras horizontales y verticales
- Gráficos de líneas para series de tiempo
- Gráficos de torta con leyendas
- Personalización de colores y estilos

### **🔍 Análisis Exploratorio**
- Estadísticas descriptivas
- Detección de valores atípicos
- Análisis de distribuciones
- Identificación de patrones temporales

---

## 📖 **Guía Paso a Paso**

### **Paso 1: Preparación del Entorno (5 min)**
```python
# Instalación automática de librerías
!pip install fuzzywuzzy python-Levenshtein networkx plotly kaleido -q

# Importación de librerías esenciales
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt
import requests
```

### **Paso 2: Carga de Datos Reales (10 min)**
```python
# Conectar con datos oficiales del gobierno
url = "https://www.datos.gov.co/api/views/jbjy-vk9h/rows.json?accessType=DOWNLOAD"
print("📥 Descargando datos del gobierno colombiano...")
response = requests.get(url)
data = response.json()
```

### **Paso 3: Limpieza y Filtrado (15 min)**
```python
# Limpiar valores monetarios corruptos
# Filtrar datos desde 2021
# Eliminar duplicados por ID de contrato
```

### **Paso 4: Análisis Temporal (20 min)**
```python
# Contratos por año, mes y día
# Duración promedio de contratos
# Patrones estacionales en la contratación
```

### **Paso 5: Análisis Sectorial (20 min)**
```python
# Distribución por sectores
# Gráficos de torta profesionales
# Ranking de sectores por valor
```

### **Paso 6: Análisis de Proveedores (20 min)**
```python
# PYMES vs grandes empresas
# Top proveedores
# Concentración de mercado
```

---

## 🔍 **Datos que Analizamos**

### **📋 Dataset: Contratos Públicos SECOP**
- **Fuente:** [Datos Abiertos Colombia](https://www.datos.gov.co)
- **Registros:** ~100,000 contratos (filtrados desde 2021)
- **Período:** 2021 - presente
- **Actualización:** Datos gubernamentales oficiales

### **📊 Variables Principales:**
| Variable | Descripción | Tipo |
|----------|-------------|------|
| `fecha_de_firma` | Fecha de firma del contrato | Fecha |
| `valor_del_contrato` | Monto en pesos colombianos | Monetario |
| `sector` | Sector económico del contrato | Categórico |
| `modalidad_de_contratacion` | Tipo de modalidad usada | Categórico |
| `proveedor_adjudicado` | Empresa o persona contratada | Texto |
| `es_pyme` | Si el proveedor es PYME | Booleano |
| `estado_contrato` | Estado actual del contrato | Categórico |

---

## 🎨 **Visualizaciones Incluidas**

### **📈 Gráficos Temporales**
- Líneas de tiempo de contratos firmados
- Barras por año y mes
- Análisis de estacionalidad

### **🥧 Gráficos de Distribución**  
- Tortas sectoriales con leyendas
- Distribución PYMES vs grandes
- Estados de contratos

### **📊 Gráficos Comparativos**
- Top proveedores (horizontal)
- Ranking sectorial por valor
- Modalidades de contratación

### **🎨 Paletas de Colores**
- Azules profesionales para institucional
- Verdes y azules para comparaciones
- Paletas coherentes en todo el análisis

---

## 🧠 **Lo que Descubrirás**

### **🔍 Patrones Temporales**
- ¿En qué meses se contrata más?
- ¿Cómo ha evolucionado el gasto público?
- ¿Hay estacionalidad en la contratación?

### **🏢 Análisis Sectorial**
- **Transporte:** ~48% de los contratos
- **TIC:** ~22% del mercado
- **Inclusión Social:** ~13% de participación

### **🏪 Mercado de Proveedores**
- Participación de PYMES en contratación pública
- Concentración vs competencia en el mercado
- Proveedores más activos por sector

### **💰 Análisis Financiero**
- Distribución de valores de contratos
- Detección de valores atípicos
- Eficiencia por modalidad de contratación

---

## 🚨 **Problemas Comunes y Soluciones**

### **Error: 'fecha_firma' no existe**
```python
# Solución: Usar el nombre correcto
df_contratos['fecha_de_firma']  # ✅ Correcto
```

### **Error: No se pueden convertir valores monetarios**
```python
# Solución: Limpiar datos primero
def limpiar_valor_monetario(valor):
    # Código de limpieza incluido en el notebook
```

### **Error: Gráficos saturados**
```python
# Solución: Usar top N elementos y leyendas
top_sectores = datos.head(5)  # Solo top 5
```

### **Error: Módulo no encontrado**
```python
# Solución: Instalar librerías
!pip install pandas matplotlib
```

---

## 🎯 **Resultados Esperados**

### **Al completar este análisis podrás:**
- ✅ **Cargar y procesar** datasets gubernamentales complejos
- ✅ **Crear visualizaciones** de calidad profesional
- ✅ **Interpretar patrones** en datos de políticas públicas  
- ✅ **Detectar anomalías** y valores atípicos
- ✅ **Generar insights** valiosos para toma de decisiones
- ✅ **Aplicar técnicas** a otros datasets similares

### **📈 Nivel alcanzado:**
De **Principiante** a **Analista Junior de Datos Públicos**

---

## 🌟 **Próximos Pasos**

### **📚 Expandir el Análisis**
- Análisis por departamentos específicos
- Comparaciones con años anteriores a 2021
- Indicadores de eficiencia gubernamental
- Análisis predictivo de tendencias

### **🔧 Mejorar Técnicamente**
- Automatizar la descarga de datos
- Crear dashboards interactivos
- Implementar alertas de anomalías
- Desarrollar APIs de consulta

### **🎓 Continuar Aprendiendo**
- Análisis estadístico avanzado
- Machine Learning para predicciones
- Visualización interactiva con Plotly
- Análisis de series de tiempo

---

## 🤝 **Contribuciones**

¿Encontraste algo interesante? ¿Tienes ideas de mejora?

### **Cómo contribuir:**
1. 🍴 Fork del repositorio
2. 🌿 Crea una rama para tu feature
3. 📝 Haz tus cambios y mejoras
4. 📤 Envía un Pull Request

### **Ideas bienvenidas:**
- Nuevas visualizaciones
- Análisis adicionales
- Mejoras en el código
- Documentación más clara
- Traducciones

---

## 📄 **Licencia**

Este proyecto está bajo licencia MIT. Los datos utilizados son públicos del gobierno colombiano.

---

## 📧 **Contacto**

**¿Dudas? ¿Sugerencias? ¿Quieres colaborar?**

- 📧 Email: [tu-email@ejemplo.com]
- 💼 LinkedIn: [tu-linkedin]
- 🐙 GitHub: [tu-github]

---

<div align="center">
  
## 🎉 **¡Felicitaciones!**

**Has completado un análisis profesional de datos públicos**

*Estas habilidades son altamente valoradas en:*
- 🏛️ **Consultoría gubernamental**
- 📊 **Ciencia de datos**
- 🔍 **Análisis de políticas públicas**
- 🏢 **Investigación institucional**

### 🚀 **¡Comparte tu trabajo!**
*#AnálisisDatos #Python #DatosAbiertos #SECOP #Colombia*

</div>

---

<div align="center">
  <p><em>Hecho con ❤️ para la transparencia y el aprendizaje</em></p>
  <p><strong>🇨🇴 Datos del pueblo, para el pueblo</strong></p>
</div>
