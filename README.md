# Inversión Pública en el Perú — Business Intelligence

**Curso:** Business Intelligence · Universidad del Pacífico
**Integrantes:** Sebastian Guevara Peralta, Fiorella Tamariz Pantoja, Marietha Córdova Delgado, Rodrigo Fernandez Yucra y Diego Medina Manrique
**Ciclo:** 2026-I
**Dataset:** [Public Investments in Peru — datos.gob.pe / Kaggle](https://www.kaggle.com/datasets/jenifergrategarro/dataset-public-investments-in-peru/data)
**Período analizado:** 2001 – 2024 · 25 departamentos · 468,428 proyectos fuente (464,100 cargados al Data Mart tras reglas de calidad de datos)

## 1. Marco Teórico

### Business Intelligence

El Business Intelligence (BI) es un conjunto de metodologías, procesos y tecnologías que permiten transformar datos en bruto en información útil para la toma de decisiones. A diferencia de los sistemas transaccionales, cuyo objetivo es registrar operaciones, los sistemas de BI están orientados al análisis: buscan responder preguntas del tipo "¿qué pasó?", "¿por qué pasó?" y "¿qué podría pasar?".

En la práctica, un proyecto de BI implica tres grandes etapas: la **extracción, transformación y carga de datos** (ETL), el **modelado dimensional** de la información, y la **visualización** a través de tableros de control o dashboards.

### Data Mart y Modelado Dimensional

Un **Data Mart** es una base de datos especializada que concentra información de un área o proceso específico de una organización. A diferencia de un Data Warehouse —que abarca toda la empresa— el Data Mart se enfoca en responder preguntas concretas de un dominio acotado.

El modelo más utilizado para estructurar un Data Mart es el **Star Schema** (esquema estrella), propuesto por Ralph Kimball. Este modelo organiza la información en torno a una **tabla de hechos** (que contiene las métricas numéricas a analizar) rodeada de **tablas dimensionales** (que proveen el contexto descriptivo). La principal ventaja de este enfoque es su eficiencia para consultas analíticas: al reducir los JOINs necesarios, permite procesar grandes volúmenes de datos con tiempos de respuesta bajos.

### ETL (Extract, Transform, Load)

El proceso ETL es el puente entre los sistemas fuente y el Data Mart. En este proyecto se implementó mediante:

- **Extracción:** lectura de 25 archivos Excel regionales provenientes del portal datos.gob.pe, consolidados en un único archivo (`Dataset_Inversiones_Peru`).
- **Transformación:** limpieza de nulos, normalización de texto (espacios en blanco, tildes), derivación de dimensiones de negocio (nivel de gobierno y tipo de intervención) y generación de claves surrogate mediante Python (pandas).
- **Carga:** el Data Mart se desarrolló y validó en **SQL Server** (vía `pyodbc`), y se migró a **SQLite** para el despliegue final — mismo esquema, sin necesidad de un servidor de base de datos externo.

### Herramientas utilizadas

| Herramienta | Uso en el proyecto |
|-------------|-------------------|
| Python (pandas, openpyxl, pyodbc, sqlite3) | ETL, consolidación y carga del Data Mart |
| SQL Server + SSMS | Desarrollo y validación inicial del Data Mart |
| SQLite | Base de datos final, portable, usada en el despliegue |
| Dash (Python) + Plotly | Visualización y dashboard interactivo |
| Docker + Azure (VM) | Contenerización y despliegue del Dashboard |
| GitHub | Control de versiones y documentación |

#### Conceptos Clave Aplicados
* **OLAP vs. OLTP**: Los sistemas fuente de Invierte.pe operan bajo un esquema transaccional (OLTP), optimizado para el registro individual de proyectos. Este proyecto migra dicha información a un entorno analítico (OLAP), diseñado para consultas complejas, agregaciones históricas y análisis de tendencias multidimensionales.
* **Proceso ETL (Extract, Transform, Load)**: Implementado mediante scripts de Python, el proceso consolida las fuentes regionales, estandariza tipos de datos, maneja valores nulos y limpia anomalías estructurales para garantizar la "versión única de la verdad".
* **Modelado Dimensional (Star Schema)**: Se optó por una arquitectura en estrella debido a su alto rendimiento en consultas de agregación y su intuitiva navegación para los usuarios de negocio. El modelo separa claramente las métricas cuantitativas (hechos) de los atributos cualitativos (dimensiones).
* **Métricas Aditivas y Semi-aditivas**: El modelo gestiona medidas sumables a través de todas las dimensiones (como el monto_viable) y ratios calculados que permiten evaluar desviaciones presupuestales de forma porcentual sin distorsionar la agregación.

## 2. Descripción de la institución y problemática
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
**Registros fuente:** 468,428 proyectos (4,328 descartados por falta de código único de inversión → 464,100 efectivamente cargados al Data Mart)
**Formato original:** 25 archivos Excel (.xlsx), uno por departamento, consolidados en [`Dataset_Inversiones_Peru`](./Dataset_Inversiones_Peru)

## 3. Modelado Dimensional

### Decisiones de diseño

Se eligió un **Star Schema** por tres razones: el dataset tiene una estructura analítica natural (una transacción central —el proyecto— rodeada de atributos descriptivos), el volumen de datos (~464K filas) requiere consultas eficientes, y este modelo simplifica los JOINs en el Dashboard.

La tabla de hechos registra una fila por proyecto de inversión. Las métricas principales son el monto viable, el costo actualizado y los beneficiarios. Se incluyó una columna calculada (`variacion_costo`) para medir el desvío presupuestal directamente en la base de datos.

La dimensión tiempo (`Dim_Tiempo`) se construyó **solo con las fechas que efectivamente aparecen en el dataset** (fecha de registro y fecha de viabilidad) — no como un calendario genérico completo — para mantener el Data Mart liviano. La tabla de hechos la referencia **dos veces**, permitiendo analizar el tiempo transcurrido entre ambos eventos.

Se incorporaron dos dimensiones derivadas que no existen como columna directa en el Excel fuente: **`Dim_NivelGobierno`** (Nacional/Regional/Local/Otros, clasificada por palabras clave sobre el nombre de la entidad) y **`Dim_TipoIntervencion`** (16 categorías como Mejoramiento, Construcción, Creación, extraídas de la primera palabra del nombre del proyecto). La ejecutora del presupuesto se modeló como dimensión independiente (`Dim_Ejecutora`), separada de la entidad responsable.

### Diagrama del modelo

### Descripción de tablas

**Fact_Inversiones** — tabla central, **464,100 filas**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_hecho | INT PK | Clave surrogate |
| codigo_inversion | BIGINT | Código en Invierte.pe |
| nombre_inversion | NVARCHAR(MAX) | Nombre oficial del proyecto |
| id_tiempo_registro | INT FK | Fecha de ingreso al sistema |
| id_tiempo_viabilidad | INT FK | Fecha de declaratoria de viabilidad (nullable) |
| id_ubicacion | INT FK | Referencia geográfica |
| id_sector | INT FK | Sector del gobierno |
| id_entidad | INT FK | Entidad responsable |
| id_ejecutora | INT FK | Unidad ejecutora del presupuesto (nullable) |
| id_estado | INT FK | Estado del proyecto |
| id_nivel_gobierno | INT FK | Nivel de gobierno (derivado) |
| id_tipo_intervencion | INT FK | Tipo de obra (derivado) |
| monto_viable | DECIMAL(18,2) | Presupuesto aprobado en S/. |
| costo_actualizado | DECIMAL(18,2) | Costo actualizado en S/. |
| beneficiarios | INT | Personas beneficiadas (nulo → 0) |
| variacion_costo | Calculada | costo_actualizado - monto_viable |

**Dim_Tiempo** — 7,950 filas (solo fechas presentes en el dataset, no calendario genérico)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_tiempo | INT PK | Clave surrogate secuencial |
| fecha | DATE | Fecha completa, única |
| anio | INT | Año |
| trimestre | INT | Trimestre (1–4) |
| mes | INT | Mes (1–12) |
| nombre_mes | VARCHAR(20) | Nombre del mes |
| semana | INT | Semana del año |
| dia | INT | Día del mes |
| nombre_dia | VARCHAR(20) | Nombre del día |
| es_fin_semana | BIT | 1 = sábado o domingo |

**Dim_Ubicacion** — 2,145 filas (una por Ubigeo único)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_ubicacion | INT PK | Clave surrogate |
| ubigeo | INT, UNIQUE | Código INEI |
| departamento | VARCHAR(100) | Departamento (25 valores) |
| provincia | VARCHAR(100) | Provincia (197 valores), `"NO ESPECIFICADO"` si falta |
| distrito | VARCHAR(100) | Distrito (1,738 valores), `"NO ESPECIFICADO"` si falta |

**Dim_Sector** — 34 filas
**Dim_Entidad** — 2,010 filas (solo el nombre de la entidad)
**Dim_Ejecutora** — 2,689 filas (unidad ejecutora, FK nullable en el Fact)
**Dim_Estado** — 2 filas (ACTIVO / CERRADO)
**Dim_NivelGobierno** — 4 filas (derivada de Entidad)
**Dim_TipoIntervencion** — 16 filas (derivada del nombre del proyecto)
**Log_Fact_Inversiones** — tabla de auditoría del ETL, se llena automáticamente en cada ejecución del script de población

El diccionario de datos completo se encuentra en [`diccionario_de_datos.md`](./diccionario_de_datos.md).

## 4. Diseño y Análisis de Resultados (Dashboard en Dash)

El Dashboard se construyó en **Dash (Python) + Plotly**, conectado directamente al Data Mart. Incluye 5 filtros con búsqueda (Sector, Nivel de Gobierno, Estado, Entidad, rango de fechas) y 5 visualizaciones, cada una respondiendo a una pregunta de negocio específica:

1. **Donut — Inversión por Nivel de Gobierno**: responde quién ejecuta más inversión pública (nación, región o municipio) — clave para entender la descentralización del gasto.
2. **Barras — Top 10 Sectores por Monto Viable**: muestra dónde se concentra el presupuesto, evidenciando el sesgo sectorial descrito en la problemática (Transportes vs. Salud/Educación).
3. **Líneas — Evolución Anual: Monto Viable vs. Costo Actualizado**: permite visualizar el desvío presupuestal en el tiempo, incluyendo el pico de 2020.
4. **Barras — Top 10 Tipos de Intervención**: distingue si el gasto se concentra en obra nueva (Construcción, Creación) o en mantenimiento de lo existente.
5. **Barras — Top 10 Departamentos por Beneficiarios**: visibiliza las brechas regionales de cobertura, conectando con la concentración geográfica identificada en la sección 2.

## 5. Conclusiones

El análisis del Data Mart de inversión pública peruana (2001–2024) confirma la hipótesis central del proyecto: **la distribución de la inversión pública no solo refleja las brechas territoriales y sectoriales existentes, sino que en varios casos las profundiza.**

- **Concentración geográfica confirmada.** Lima concentra el 22.2% del presupuesto viable nacional, mientras que los cuatro departamentos de la Selva —que cubren más de la mitad del territorio y registran los mayores índices de pobreza del país— reciben en conjunto apenas el 8.2%. Esta asimetría no se explica solo por densidad poblacional, sino que coincide con un patrón histórico de centralización del gasto público.

- **El gasto no sigue las necesidades sociales más urgentes.** El sector Transportes y Comunicaciones recibe casi 10 veces más presupuesto que Salud y Educación juntos, a pesar de que ambos sectores sociales presentan brechas de cobertura significativas en zonas rurales (57.6% sin seguro de salud, 19 puntos porcentuales de diferencia en conclusión de secundaria). Esto sugiere que la asignación presupuestal histórica ha priorizado infraestructura física sobre desarrollo de capital humano.

- **El control de costos es una debilidad estructural del sistema, no un caso aislado.** Un desvío del 15.3% entre el monto viable original y el costo actualizado, sostenido a lo largo de más de dos décadas y miles de proyectos, indica que los estudios de pre-inversión sistemáticamente subestiman el costo real — un problema de diseño del proceso, no de proyectos puntuales mal gestionados.

- **La pandemia no resolvió la inequidad, posiblemente la usó como justificación para mantenerla.** El pico de S/. 754 mil millones registrado en 2020 amerita un análisis específico (pendiente de profundizar con el Dashboard) para determinar si la respuesta de emergencia reforzó o corrigió el patrón de concentración geográfica ya identificado.

- **El modelo dimensional cumple su propósito analítico.** Separar `Dim_NivelGobierno` y `Dim_TipoIntervencion` como dimensiones derivadas —no presentes directamente en la fuente— permitió responder preguntas de negocio (¿quién ejecuta? ¿qué tipo de obra?) que el dataset original no facilitaba directamente, validando la utilidad del proceso de modelado por encima de un simple volcado de datos.

> Las respuestas cuantitativas específicas a las 5 preguntas de investigación planteadas en la sección 2 (evolución de la brecha Lima-regiones 2010–2024, tiempos promedio de viabilidad por región, inversión per cápita en salud/educación por departamento) requieren cruces adicionales que se detallarán con las capturas del Dashboard en la entrega final — los hallazgos arriba corresponden a los patrones agregados ya validados sobre el dataset completo.

---

## 6. Recomendaciones

**Para el diseño de política pública:**
1. **Establecer un piso presupuestal mínimo por habitante** para los departamentos de la Selva y otras zonas de alta pobreza, desligado de su aporte al PBI regional, para revertir la tendencia de subinversión crónica.
2. **Reforzar los estudios de pre-inversión** (fase de formulación en Invierte.pe) con metodologías de estimación de costos más conservadoras, dado que el desvío del 15.3% es sistemático y no producto de proyectos aislados.
3. **Priorizar inversión en Salud y Educación** en las regiones con mayores brechas de cobertura identificadas, sin que esto implique reducir la inversión en infraestructura de transporte, sino corregir la proporción relativa entre sectores.
4. **Auditar específicamente los proyectos registrados en 2020** para evaluar si el pico de inversión de emergencia mantuvo o corrigió el patrón de centralismo geográfico ya identificado en el período pre-pandemia.

**Para la continuidad técnica del proyecto:**
1. **Incorporar al Dashboard un indicador de inversión per cápita** (monto viable / población departamental), cruzando con datos del INEI, para responder con precisión la pregunta de investigación sobre cobertura por habitante.
2. **Agregar una vista de evolución de la brecha Lima-regiones** como serie de tiempo (2010–2024) directamente en el Dashboard, aprovechando que `Dim_Tiempo` ya está modelada para soportar este tipo de análisis.
3. **Mantener actualizado el Data Mart** ante nuevas descargas del portal de datos abiertos, reutilizando el mismo script de población (`poblacion_del_datamart_conexion.py`), que ya contempla las reglas de limpieza necesarias (duplicados por espacios, nulos, normalización de tildes).

---

## Estructura del repositorio

```
📦 BI---Proyecto-Inversiones-Per-/
├── 📄 README.md
├── 📄 diccionario_de_datos.md
├── 📄 poblacion_del_datamart_conexion.py    ← ETL: Excel → Data Mart (SQLite)
├── 📄 dash_proyecto_bi_conexion.py          ← Dashboard Dash, conecta al Data Mart
├── 📄 Dockerfile                            ← Imagen del Dashboard para despliegue
├── 📄 docker_bash.sh                        ← Script de configuración inicial en la VM
├── 📄 requirements.txt                      ← Dependencias Python
├── 🖼️ DataMart Estrella Inverisones Perú.jpeg ← Imagen del modelo dimensional
├── 📄 Dataset_Inversiones_Peru              ← Excel consolidado fuente
├── 📄 LICENSE
└── 📄 .gitignore
```

> Los archivos `poblacion_del_datamart.py` y `dash_proyecto_bi.py` (sin sufijo `_conexion`) corresponden a una versión intermedia de desarrollo; los archivos `_conexion` son la versión final validada.

## Cómo reproducir el proyecto

### Local con Python (rápido, sin Docker)

```bash
# 1. Clonar el repositorio
git clone https://github.com/rodie916/BI---Proyecto-Inversiones-Per-.git
cd BI---Proyecto-Inversiones-Per-

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Poblar el Data Mart (genera datamart_inversiones.db en SQLite)
python poblacion_del_datamart_conexion.py

# 4. Levantar el Dashboard
python dash_proyecto_bi_conexion.py
# → Abrir http://localhost:8050
```

### Con Docker (igual al despliegue en producción)

```bash
git clone https://github.com/rodie916/BI---Proyecto-Inversiones-Per-.git
cd BI---Proyecto-Inversiones-Per-

docker build -t parte1bi:latest .
docker run -d -p 8050:8050 parte1bi:latest
# → Abrir http://localhost:8050
```

### Despliegue

El Dashboard se desplegó en una **VM de Azure** (`vm-trabajo-bi`, Ubuntu, resource group `rg-trabajofinal-bi`) mediante Docker, expuesto vía IP pública en el puerto `8050`. *(La IP puede variar si la VM se reinicia; ver detalle de acceso en la entrega final.)*

**Pasos seguidos en la VM:**

```bash
# 1. Clonar el repositorio
git clone https://github.com/rodie916/BI---Proyecto-Inversiones-Per-
cd BI---Proyecto-Inversiones-Per-/

# 2. Preparar el script de configuración inicial (corrige saltos de línea Windows -> Linux)
sudo apt-get update
sudo apt-get install dos2unix
chmod +x docker_bash.sh
dos2unix docker_bash.sh
./docker_bash.sh

# 3. Construir la imagen Docker
sudo docker build -t contenedorbi.azurecr.io/parte1bi:latest .
sudo docker images

# 4. Subir la imagen a Azure Container Registry (ACR)
sudo docker login contenedorbi.azurecr.io
sudo docker push contenedorbi.azurecr.io/parte1bi:latest

# 5. Correr el contenedor, mapeando el puerto del Dashboard
sudo docker run -d -p 8050:8050 --name dashboard-bi contenedorbi.azurecr.io/parte1bi:latest
sudo docker ps

# 6. Verificar que responde dentro de la VM
curl http://localhost:8050

# 7. Obtener la IP pública para acceder desde fuera
curl ifconfig.me
```

**Configuración adicional necesaria en Azure (fuera de la terminal):**
- **Network Security Group** (`vm-trabajo-bi-nsg`) → Inbound security rules → abrir el puerto `8050` (TCP, Allow, Source: Any).
- Si se reconstruye la imagen tras un cambio de código, repetir los pasos 3 a 5. Si el puerto 8050 ya está en uso por un contenedor anterior, liberarlo primero:
  ```bash
  sudo docker stop <nombre_contenedor_anterior>
  sudo docker rm <nombre_contenedor_anterior>
  ```

**Acceso final:** `http://4.228.57.83:8050/`
**Acceso final:** `https://dashboardbi-bjaagwh4ejhch5gu.brazilsouth-01.azurewebsites.net/`

---

*Fuente de datos: Portal de Datos Abiertos del Estado Peruano — datosabiertos.gob.pe · Sistema Invierte.pe — MEF*
