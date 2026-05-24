# Inversión Pública en el Perú — Business Intelligence

> **Curso:** Business Intelligence · Universidad del Pacífico  
> **Dataset:** Public Investments in Peru — Portal de Datos Abiertos del Estado Peruano  
> **Período:** 2001 – 2024 · 25 departamentos · 468,428 proyectos

## Problemática

### Contexto

El Perú destina anualmente miles de millones de soles a proyectos de inversión pública a través del **Sistema Nacional de Programación Multianual y Gestión de Inversiones (Invierte.pe)**. Estos proyectos abarcan infraestructura vial, salud, educación, saneamiento, energía y otros sectores críticos para el desarrollo del país.

Sin embargo, el análisis de los **468,428 proyectos registrados entre 2001 y 2024** revela patrones preocupantes que plantean interrogantes sobre la eficiencia, equidad y sostenibilidad del gasto público peruano.

### Hallazgos Principales

#### 1. Concentración geográfica: Lima vs. el resto del país

> *"El 22.2% del monto total de inversión viable se concentra en un solo departamento: Lima."*

Con un monto viable acumulado de **S/. 967 mil millones**, Lima lidera la inversión pública a nivel nacional, mientras que los cuatro departamentos de la selva peruana (Loreto, Ucayali, Amazonas y Madre de Dios) — que juntos representan más del **55% del territorio nacional** — apenas concentran el **8.2% del monto total (S/. 357 mil millones)**.

Esta disparidad es especialmente preocupante cuando se considera que los departamentos amazónicos presentan los mayores índices de pobreza y menor acceso a servicios básicos del país (INEI, 2023).

| Zona | Monto Viable | % del Total |
|------|-------------|-------------|
| Lima | S/. 967 mil millones | 22.2% |
| Selva (4 dptos.) | S/. 357 mil millones | 8.2% |
| Resto del país | S/. 3,028 mil millones | 69.6% |


#### 2. Sesgo sectorial: infraestructura vial sobre sectores sociales

> *"El sector Transportes y Comunicaciones concentra casi 3 de cada 10 soles de inversión pública, mientras Salud y Educación juntos no llegan al 3%."*

El análisis sectorial revela una marcada preferencia por la infraestructura física sobre los servicios sociales:

| Sector | Monto Viable | % del Total |
|--------|-------------|-------------|
| Transportes y Comunicaciones | S/. 1,284 mil millones | **29.5%** |
| Gobiernos Regionales | S/. 821 mil millones | 18.9% |
| Gobiernos Locales | S/. 789 mil millones | 18.1% |
| Agricultura y Riego | S/. 530 mil millones | 12.2% |
| Energía y Minas | S/. 344 mil millones | 7.9% |
| **Salud** | S/. 62 mil millones | **1.4%** |
| **Educación** | S/. 56 mil millones | **1.3%** |

Este patrón resulta crítico en un país donde el **57.6% de la población rural** no tiene acceso a seguro de salud (ENAHO 2022) y donde la tasa de conclusión de secundaria en zonas rurales es del 72%, frente al 91% en zonas urbanas (MINEDU 2023).


#### 3. Desvío presupuestal sistemático: el costo real siempre supera lo planeado

> *"El costo actualizado de los proyectos supera el monto viable original en S/. 664 mil millones, lo que representa un desvío del 15.3% sobre el total."*

El dataset permite comparar el **monto viable** (presupuesto aprobado al declarar viable el proyecto) con el **costo actualizado** (última estimación del costo real). La diferencia acumulada asciende a **S/. 663,790 millones**, lo que sugiere:

- Subestimación sistemática de costos en la formulación de proyectos
- Modificaciones de alcance durante la ejecución
- Impacto de la inflación y variación de precios de materiales
- Posibles deficiencias en los estudios de pre-inversión

Los sectores con mayor desvío absoluto son **Transportes y Agricultura**, precisamente los de mayor volumen de inversión.


#### 4. Pico atípico de 2020: ¿reactivación o concentración de emergencia?

> *"En 2020, el monto de inversión registrado alcanzó S/. 754 mil millones, el cual fue el mayor pico histórico del período analizado."*

El año 2020, marcado por la pandemia COVID-19, registró el mayor volumen de inversión pública de toda la serie histórica. INVESSTIGAR FUENTES O TEORIZAR SI FUE POR EMERGENCIA EQUITATIVAMENTE EN TODAS PARTES O SE CONCENTRÓ EN UN DEPARTAMENTO.


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
