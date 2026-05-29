# Inversión Pública en el Perú — Business Intelligence

> **Curso:** Business Intelligence · Universidad del Pacífico  
> **Dataset:** Public Investments in Peru — Portal de Datos Abiertos del Estado Peruano  
> **Período:** 2001 – 2024 · 25 departamentos · 468,428 proyectos

## Problemática

### Marco Teórico

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
* **Proceso ETL (Extract, Transform, Load)**: Implementado mediante scripts de Python (etl/unir_inversiones.py), el proceso consolida 25 fuentes regionales independientes, estandariza tipos de datos, maneja valores nulos y limpia anomalías estructurales para garantizar la "versión única de la verdad".
* **Modelado Dimensional (Star Schema)**: Se optó por una arquitectura en estrella debido a su alto rendimiento en consultas de agregación y su intuitiva navegación para los usuarios de negocio. El modelo separa claramente las métricas cuantitativas (hechos) de los atributos cualitativos (dimensiones).
* **Métricas Aditivas y Semi-aditivas**: El modelo gestiona medidas sumables a través de todas las dimensiones (como el monto_viable) y ratios calculados que permiten evaluar desviaciones presupuestales de forma porcentual sin distorsionar la agregación.


### Descripción de la Empresa (Entidad) y Problemática

El análisis no se centra en una corporación privada, sino en el **Estado Peruano**, específicamente en el **Sistema Nacional de Programación Multianual y Gestión de Inversiones (Invierte.pe)**, administrado por el *Ministerio de Economía y Finanzas (MEF)*. Esta entidad orienta los recursos públicos destinados a la inversión para el cierre de brechas de infraestructura y acceso a servicios públicos esenciales.

#### La Problemática Encontrada

A pesar de contar con un flujo continuo de miles de millones de soles anuales, la gestión de la inversión pública sufre de ineficiencias estructurales que se evidencian al analizar los **468,428 proyectos registrados entre 2001 y 2024:**

#### 1. Concentración Geográfica Desproporcionada

El **22.2%** del presupuesto viable acumulado se concentra de forma exclusiva en el departamento de Lima (**S/. 967 mil millones**). En contraste, la región Selva (Loreto, Ucayali, Amazonas y Madre de Dios), que abarca más del 55% del territorio y sufre altas tasas de pobreza (INEI, 2023), solo recibe el **8.2%** de los fondos.

| Zona | Monto Viable | % del Total |
|------|-------------|-------------|
| Lima | S/. 967 mil millones | 22.2% |
| Selva (4 dptos.) | S/. 357 mil millones | 8.2% |
| Resto del país | S/. 3,028 mil millones | 69.6% |


#### 2. Desbalance de Prioridades Sectoriales

El sector Transportes y Comunicaciones absorbe el **29.5%** de la inversión total, postergando sectores sociales críticos como Salud (**1.4%**) y Educación (**1.3%**), lo que perpetúa brechas estructurales en zonas rurales.

| Sector | Monto Viable | % del Total |
|--------|-------------|-------------|
| Transportes y Comunicaciones | S/. 1,284 mil millones | **29.5%** |
| Gobiernos Regionales | S/. 821 mil millones | 18.9% |
| Gobiernos Locales | S/. 789 mil millones | 18.1% |
| Agricultura y Riego | S/. 530 mil millones | 12.2% |
| Energía y Minas | S/. 344 mil millones | 7.9% |
| **Salud** | S/. 62 mil millones | **1.4%** |
| **Educación** | S/. 56 mil millones | **1.3%** |


#### 3. Desvío Presupuestal Sistemático (Adendas y Sobrecostos)

Existe una subestimación sistemática en la formulación de proyectos. El costo actualizado real supera al monto viable original en **S/. 664 mil millones** (un desvío del 15.3% global), lo que sugiere deficiencias técnicas en los estudios de pre-inversión y extensiones de alcance injustificadas.


#### 4. Anomalías Históricas de Emergencia (Pico 2020) 

Durante el año de la pandemia por COVID-19, se registró un pico histórico atípico de **S/. 754 mil millones** en registros, cuya eficiencia de distribución y destino geográfico requiere ser evaluada para descartar centralismo de emergencia.


### Preguntas que Responde este Dataset

Con el Data Mart construido, este proyecto responde las siguientes preguntas de negocio:

1. ¿Qué departamentos reciben más inversión pública por habitante en sectores de salud y educación?
2. ¿Ha mejorado la distribución geográfica de la inversión entre 2010 y 2024, o la brecha Lima-regiones se ha profundizado?
3. ¿Qué sectores presentan mayor desvío entre el presupuesto viable y el costo actualizado?
4. ¿Cuánto tiempo transcurre en promedio entre el registro y la declaración de viabilidad de un proyecto, y varía esto por sector o región?
5. ¿Los departamentos con mayor índice de pobreza reciben inversión proporcionalmente mayor en sectores sociales?


## Sobre el Dataset

**Fuente original:** [Portal de Datos Abiertos del Estado Peruano](https://www.datosabiertos.gob.pe/) / [Kaggle — Public Investments in Peru](https://www.kaggle.com/datasets/jenifergrategarro/dataset-public-investments-in-peru)  
**Sistema fuente:** Invierte.pe — Sistema Nacional de Programación Multianual y Gestión de Inversiones (MEF)  
**Cobertura:** 25 departamentos del Perú · Años 2001–2024  
**Registros:** 468,428 proyectos de inversión pública  
**Formato original:** 25 archivos Excel (.xlsx), uno por departamento  

El dataset fue consolidado en un único archivo mediante un script Python (`etl/unir_inversiones.py`) que unifica los 25 archivos manteniendo la integridad de los datos.

### Decisiones de diseño

Se eligió un **Star Schema** por tres razones: el dataset tiene una estructura analítica natural (una transacción central —el proyecto— rodeada de atributos descriptivos), el volumen de datos (468K filas) requiere consultas eficientes, y Power BI trabaja de forma óptima con este modelo.

La tabla de hechos registra una fila por proyecto de inversión. Las métricas principales son el monto viable, el costo actualizado y los beneficiarios. Se incluyó una columna calculada (`variacion_costo`) para medir el desvío presupuestal directamente en la base de datos.

La dimensión tiempo se implementó como **calendario genérico** (2000–2030) con una clave en formato YYYYMMDD, y la tabla de hechos la referencia **dos veces**: una para la fecha de registro y otra para la fecha de viabilidad, permitiendo analizar el tiempo transcurrido entre ambos eventos.

### Diagrama del modelo

![Star Schema — Datamart_Inversiones_Peru](./assets/diagrama_star_schema.png)

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

- **Visión General** — KPIs principales, mapa coroplético, estado de proyectos
- **Evolución temporal** — serie 2001–2024 por región natural (Costa / Sierra / Selva)
- **Brecha regional** — distribución geográfica, inversión per cápita por departamento
- **Desvío presupuestal** — matriz sectorial, top proyectos con mayor desvío
- **Beneficiarios** — impacto social por sector y región


##  Equipo

1. Córdova Delgado, Marietha Kristeen Alexandra
2. Fernandez Yucra, Rodrigo Alejandro
3. Guevara Peralta, Sebatian Antonio Valentino
4. Medina Manrique, Diego Rodrigo
5. Tamariz Pantoja, Fiorella Ariana
