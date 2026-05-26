# Inversión Pública en el Perú — Business Intelligence

> **Curso:** Business Intelligence · Universidad del Pacífico  
> **Dataset:** Public Investments in Peru — Portal de Datos Abiertos del Estado Peruano  
> **Período:** 2001 – 2024 · 25 departamentos · 468,428 proyectos

## Problemática

### Marco Teórico

El desarrollo de este proyecto se fundamenta en los principios de **Business Intelligence (BI)** y el modelado de datos propuesto por la metodología de **Ralph Kimball (Lifecycle Toolkit)**. El objetivo primordial es transformar datos transaccionales gubernamentales de naturaleza heterogénea en activos de información estratégica para la toma de decisiones y el control ciudadano.

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

## Arquitectura del Data Mart

El proyecto implementa un **modelo dimensional tipo Star Schema** en SQL Server:

```
         Dim_Tiempo
              |
Dim_Sector ──┤
              ├── Fact_Inversiones ──── Dim_Ubicacion
Dim_Entidad ──┤
              |
         Dim_Estado
```

**Fact Table:** `Fact_Inversiones` — 468,428 filas  
**Métricas:** monto_viable, costo_actualizado, beneficiarios, variacion_costo (calculada)  
**Dimensiones:** 5 tablas dimensionales + calendario Dim_Tiempo (2000–2030)

Ver el **[Diccionario de Datos](./diccionario_de_datos.md)** para la descripción completa de cada tabla y columna.


##  Equipo

1. Córdova Delgado, Marietha Kristeen Alexandra
2. Fernandez Yucra, Rodrigo Alejandro
3. Guevara Peralta, Sebatian Antonio Valentino
4. Medina Manrique, Diego Rodrigo
5. Tamariz Pantoja, Fiorella Ariana
