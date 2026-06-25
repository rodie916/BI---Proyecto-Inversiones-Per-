# Inversión Pública en el Perú — Business Intelligence

**Curso:** Business Intelligence · Universidad del Pacífico  
**Integrantes:** Sebastian Guevara Peralta, Fiorella Tamariz Pantoja, Marietha Córdova Delgado, Rodrigo Fernandez Yucra y Diego Medina Manrique  
**Ciclo:** 2026-I  
**Dataset:** [Public Investments in Peru — datos.gob.pe / Kaggle](https://www.kaggle.com/datasets/jenifergrategarro/dataset-public-investments-in-peru/data)  
**Período analizado:** 2001 – 2024 · 25 departamentos · 468,428 proyectos

## 1. Marco Teórico

### Business Intelligence

El Business Intelligence (BI) es un conjunto de metodologías, procesos y tecnologías que permiten transformar datos en bruto en información útil para la toma de decisiones. A diferencia de los sistemas transaccionales, cuyo objetivo es registrar operaciones, los sistemas de BI están orientados al análisis: buscan responder preguntas del tipo "¿qué pasó?", "¿por qué pasó?" y "¿qué podría pasar?".

En la práctica, un proyecto de BI implica tres grandes etapas: la **extracción, transformación y carga de datos** (ETL), el **modelado dimensional** de la información, y la **visualización** a través de tableros de control o dashboards.

### Data Mart y Modelado Dimensional

Un **Data Mart** es una base de datos especializada que concentra información de un área o proceso específico de una organización. A diferencia de un Data Warehouse —que abarca toda la empresa— el Data Mart se enfoca en responder preguntas concretas de un dominio acotado.

El modelo más utilizado para estructurar un Data Mart es el **Star Schema** (esquema estrella), propuesto por Ralph Kimball. Este modelo organiza la información en torno a una **tabla de hechos** (que contiene las métricas numéricas a analizar) rodeada de **tablas dimensionales** (que proveen el contexto descriptivo). La principal ventaja de este enfoque es su eficiencia para consultas analíticas: al reducir los JOINs necesarios, permite procesar grandes volúmenes de datos con tiempos de respuesta bajos.

### ETL (Extract, Transform, Load)

El proceso ETL es el puente entre los sistemas fuente y el Data Mart. En este proyecto se implementó mediante:

- **Extracción:** lectura de 25 archivos Excel regionales provenientes del portal datos.gob.pe
- **Transformación:** consolidación, limpieza de nulos, normalización de texto y generación de claves surrogate mediante Python (pandas)
- **Carga:** inserción en SQL Server a través de scripts T-SQL y conexión directa vía pyodbc

### Herramientas utilizadas

| Herramienta | Uso en el proyecto |
|-------------|-------------------|
| Python (pandas, openpyxl, pyodbc) | ETL y consolidación del dataset |
| SQL Server + SSMS | Creación y gestión del Data Mart |
| Power BI Desktop | Visualización y dashboards |
| GitHub | Control de versiones y documentación |

#### Conceptos Clave Aplicados
* **OLAP vs. OLTP**: Los sistemas fuente de Invierte.pe operan bajo un esquema transaccional (OLTP), optimizado para el registro individual de proyectos. Este proyecto migra dicha información a un entorno analítico (OLAP), diseñado para consultas complejas, agregaciones históricas y análisis de tendencias multidimensionales.
* **Proceso ETL (Extract, Transform, Load)**: Implementado mediante scripts de Python `unir_inversiones.py`, el proceso consolida 25 fuentes regionales independientes, estandariza tipos de datos, maneja valores nulos y limpia anomalías estructurales para garantizar la "versión única de la verdad".
* **Modelado Dimensional (Star Schema)**: Se optó por una arquitectura en estrella debido a su alto rendimiento en consultas de agregación y su intuitiva navegación para los usuarios de negocio. El modelo separa claramente las métricas cuantitativas (hechos) de los atributos cualitativos (dimensiones).
* **Métricas Aditivas y Semi-aditivas**: El modelo gestiona medidas sumables a través de todas las dimensiones (como el monto_viable) y ratios calculados que permiten evaluar desviaciones presupuestales de forma porcentual sin distorsionar la agregación.

## 2. Descripción de la institución y problematica
### El sistema de inversión pública en el Perú

El Ministerio de Economía y Finanzas (MEF) del Perú gestiona la inversión pública a través del sistema **Invierte.pe**, implementado en 2017 como sucesor del SNIP. Este sistema establece un ciclo de vida para cada proyecto: formulación, evaluación, aprobación de viabilidad, ejecución y cierre. Cada proyecto recibe un código único y queda registrado con información sobre su sector, entidad responsable, ubicación geográfica, presupuesto aprobado y número de beneficiarios.

Entre 2001 y 2024, el Estado peruano registró **468,428 proyectos de inversión pública** por un monto viable acumulado de **S/. 4.35 billones**, distribuidos en los 25 departamentos del país.

#### Problemática Encontrada

El análisis exploratorio del dataset revela tres patrones que justifican este estudio:

**Concentración Geográfica.** El 22.2% del presupuesto viable acumulado se concentra de forma exclusiva en el departamento de Lima (**S/. 967 mil millones**). En contraste, la región Selva (Loreto, Ucayali, Amazonas y Madre de Dios), que abarca más del 55% del territorio y sufre altas tasas de pobreza (INEI, 2023), solo recibe el **8.2%** de los fondos.

| Zona | Monto Viable | % del Total |
|------|-------------|-------------|
| Lima | S/. 967 mil millones | 22.2% |
| Selva (4 dptos.) | S/. 357 mil millones | 8.2% |
| Resto del país | S/. 3,028 mil millones | 69.6% |


**Sesgo sectorial.** El sector Transportes y Comunicaciones concentra el 29.5% del monto total (S/. 1,284 miles de millones), mientras que Salud y Educación juntos no alcanzan el 3% (S/. 62 y S/. 56 miles de millones respectivamente). Esto ocurre en un contexto donde el 57.6% de la población rural carece de seguro de salud (ENAHO, 2022) y la tasa de conclusión de secundaria en zonas rurales es 19 puntos porcentual menor que en zonas urbanas (MINEDU, 2023).

| Sector | Monto Viable | % del Total |
|--------|-------------|-------------|
| Transportes y Comunicaciones | S/. 1,284 mil millones | **29.5%** |
| Gobiernos Regionales | S/. 821 mil millones | 18.9% |
| Gobiernos Locales | S/. 789 mil millones | 18.1% |
| Agricultura y Riego | S/. 530 mil millones | 12.2% |
| Energía y Minas | S/. 344 mil millones | 7.9% |
| **Salud** | S/. 62 mil millones | **1.4%** |
| **Educación** | S/. 56 mil millones | **1.3%** |


**Desvío presupuestal sistemático.** El costo actualizado de los proyectos supera al monto viable original en S/. 663,790 millones, equivalente a un desvío del 15.3% sobre el total. Este patrón sugiere debilidades en la formulación de proyectos y en los estudios de pre-inversión.


**Anomalías Históricas de Emergencia (Pico 2020)** Durante el año de la pandemia por COVID-19, se registró un pico histórico atípico de S/. 754 mil millones en registros, cuya eficiencia de distribución y destino geográfico requiere ser evaluada para descartar centralismo de emergencia.


### Pregunta central del proyecto

> *¿La distribución de la inversión pública peruana entre 2001 y 2024 reproduce y profundiza las brechas territoriales y sectoriales existentes?*

### Preguntas específicas que responde el Data Mart

1. ¿Qué departamentos reciben más inversión en salud y educación por habitante?
2. ¿La brecha Lima-regiones se ha reducido o ampliado entre 2010 y 2024?
3. ¿Qué sectores presentan mayor desvío entre presupuesto viable y costo actualizado?
4. ¿Los departamentos de la selva reciben inversión proporcionalmente mayor en servicios básicos?
5. ¿Cuánto tiempo tarda en promedio un proyecto en obtener viabilidad, y varía esto por región?


## Sobre el Dataset

**Fuente original:** [Portal de Datos Abiertos del Estado Peruano](https://www.datosabiertos.gob.pe/) / [Kaggle — Public Investments in Peru](https://www.kaggle.com/datasets/jenifergrategarro/dataset-public-investments-in-peru)  
**Sistema fuente:** Invierte.pe — Sistema Nacional de Programación Multianual y Gestión de Inversiones (MEF)  
**Cobertura:** 25 departamentos del Perú · Años 2001–2024  
**Registros:** 468,428 proyectos de inversión pública  
**Formato original:** 25 archivos Excel (.xlsx), uno por departamento  

El dataset fue consolidado en un único archivo mediante un script Python (`unir_inversiones.py`) que unifica los 25 archivos manteniendo la integridad de los datos.

## 3. Modelado Dimensional

### Decisiones de diseño

Se eligió un **Star Schema** por tres razones: el dataset tiene una estructura analítica natural (una transacción central —el proyecto— rodeada de atributos descriptivos), el volumen de datos (468K filas) requiere consultas eficientes, y Power BI trabaja de forma óptima con este modelo.

La tabla de hechos registra una fila por proyecto de inversión. Las métricas principales son el monto viable, el costo actualizado y los beneficiarios. Se incluyó una columna calculada (`variacion_costo`) para medir el desvío presupuestal directamente en la base de datos.

La dimensión tiempo se implementó como **calendario genérico** (2000–2030) con una clave en formato YYYYMMDD, y la tabla de hechos la referencia **dos veces**: una para la fecha de registro y otra para la fecha de viabilidad, permitiendo analizar el tiempo transcurrido entre ambos eventos.

### Diagrama del modelo

![Star Schema — Datamart_Inversiones_Peru](DataMart%20Estrella%20Inverisones%20Perú.jpeg)

### Descripción de tablas

**Fact_Inversiones** — tabla central, 468,428 filas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_hecho | INT PK | Clave surrogate |
| codigo_inversion | BIGINT | Código en Invierte.pe |
| nombre_inversion | NVARCHAR(500) | Nombre oficial del proyecto |
| id_tiempo_registro | INT FK | Fecha de ingreso al sistema |
| id_tiempo_viabilidad | INT FK | Fecha de declaratoria de viabilidad (nullable) |
| id_ubicacion | INT FK | Referencia geográfica |
| id_sector | INT FK | Sector del gobierno |
| id_entidad | INT FK | Entidad y ejecutora |
| id_estado | INT FK | Estado del proyecto |
| monto_viable | DECIMAL(20,2) | Presupuesto aprobado en S/. |
| costo_actualizado | DECIMAL(20,2) | Costo actualizado en S/. |
| beneficiarios | INT | Personas beneficiadas (nullable) |
| variacion_costo | Calculada | costo_actualizado - monto_viable |

**Dim_Tiempo** — 11,323 filas (calendario 2000–2030)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_tiempo | INT PK | Formato YYYYMMDD |
| fecha | DATE | Fecha completa |
| anio | INT | Año |
| trimestre | INT | Trimestre (1–4) |
| mes | INT | Mes (1–12) |
| nombre_mes | VARCHAR(20) | Nombre del mes |
| semana | INT | Semana del año |
| dia | INT | Día del mes |
| nombre_dia | VARCHAR(20) | Nombre del día |
| es_fin_semana | BIT | 1 = sábado o domingo |

**Dim_Ubicacion** — 2,174 filas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_ubicacion | INT PK | Clave surrogate |
| ubigeo | VARCHAR(10) | Código INEI |
| departamento | VARCHAR(100) | Departamento (25 valores) |
| provincia | VARCHAR(100) | Provincia (197 valores) |
| distrito | VARCHAR(100) | Distrito (1,738 valores) |

**Dim_Sector** — 34 filas  
**Dim_Entidad** — 9,923 filas (entidad + ejecutora)  
**Dim_Estado** — 2 filas (ACTIVO / CERRADO)

El diccionario de datos completo se encuentra en [`diccionario_de_datos.md`](./diccionario_de_datos.md).

## 4. Diseño y Análisis de Resultados (Power BI)

*Esta sección se completará en la entrega final con capturas del dashboard y análisis de cada visualización.*

El dashboard está estructurado en 5 pestañas con narrativa progresiva:

*Esta sección se completará en la entrega final con capturas del dashboard y análisis de cada visualización.*

- **Visión General** — KPIs principales, mapa coroplético, estado de proyectos
- **Evolución temporal** — serie 2001–2024 por región natural (Costa / Sierra / Selva)
- **Brecha regional** — distribución geográfica, inversión per cápita por departamento
- **Desvío presupuestal** — matriz sectorial, top proyectos con mayor desvío
- **Beneficiarios** — impacto social por sector y región

## 5. Conclusiones

*Se completarán en la entrega final una vez analizado el dashboard.*

---

## 6. Recomendaciones

*Se completarán en la entrega final.*

---

## Estructura del repositorio

```
📦 BI---Proyecto-Inversiones-Per-/
├── 📄 README.md
├── 📄 diccionario_de_datos.md
├── 📄 Datamart_Inversiones_Peru_v2.sql      ← Creación del Data Mart
├── 📄 poblar_dimensiones_v2.sql             ← INSERT dimensiones
├── 📄 poblar_datamart_v4.py                 ← ETL Python → SQL Server
├── 🖼️ DataMart Estrella Inverisones Perú.jpeg ← Imagen del modelo
└── 📄 .gitignore                            ← Archivos excluidos del control de versiones
```

## Cómo reproducir el proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/rodie916/BI---Proyecto-Inversiones-Per-.git

# 2. Instalar dependencias
pip install pandas openpyxl pyodbc

# 3. Crear estructura del Data Mart en SSMS
# → Ejecutar Datamart_Inversiones_Peru_v2.sql

# 4. Poblar dimensiones en SSMS
# → Ejecutar poblar_dimensiones_v2.sql

# 5. Poblar Fact Table vía Python
# → Editar RUTA_EXCEL y SERVER en poblar_datamart_v4.py
python poblar_datamart_v4.py
```

---

*Fuente de datos: Portal de Datos Abiertos del Estado Peruano — datosabiertos.gob.pe · Sistema Invierte.pe — MEF*

