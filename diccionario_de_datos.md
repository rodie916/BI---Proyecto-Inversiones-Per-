# Diccionario de Datos
## Inversión Pública en el Perú — Business Intelligence

---

## 1. Dataset Fuente: `Inversiones_Peru_Consolidado.xlsx`

Archivo consolidado a partir de 25 archivos Excel regionales. Cada fila representa un **proyecto de inversión pública** registrado en el sistema Invierte.pe del MEF.

| # | Campo | Tipo | Nulos | Valores únicos | Descripción |
|---|-------|------|-------|----------------|-------------|
| 1 | `Código único de inversión` | Entero | 4,328 | 335,946 | Identificador único del proyecto en el sistema Invierte.pe. Puede aparecer en múltiples regiones si el proyecto es multiregional. |
| 2 | `Nombre de la inversión` | Texto | 0 | 339,440 | Nombre oficial del proyecto tal como aparece en el sistema. Suele incluir el tipo de intervención (mejoramiento, construcción, ampliación), el bien o servicio y la ubicación geográfica. |
| 3 | `Monto viable` | Decimal | 0 | 310,030 | Monto en **soles (S/.)** aprobado en la declaratoria de viabilidad del proyecto. Representa el presupuesto oficial aprobado. |
| 4 | `Estado de la inversión` | Texto | 0 | 2 | Estado actual del proyecto. Valores posibles: `ACTIVO` (en formulación, evaluación o ejecución) o `CERRADO` (concluido o desactivado). |
| 5 | `Sector` | Texto | 0 | 34 | Sector del gobierno nacional al que pertenece la entidad responsable del proyecto. Ejemplos: `TRANSPORTES Y COMUNICACIONES`, `SALUD`, `EDUCACION`, `AGRICULTURA Y RIEGO`. |
| 6 | `Entidad` | Texto | 0 | 2,012 | Nombre de la entidad pública responsable (Ministerio, Gobierno Regional o Local). Ejemplo: `MINISTERIO DE TRANSPORTES Y COMUNICACIONES - MTC`. |
| 7 | `Ejecutora` | Texto | 3,655 | 2,692 | Unidad ejecutora específica dentro de la entidad responsable de gestionar el presupuesto del proyecto. Puede ser nula cuando la entidad ejecuta directamente. |
| 8 | `Fecha de registro` | Fecha | 0 | 7,845 | Fecha en que el proyecto fue ingresado al sistema Invierte.pe. Formato original: DD/MM/YYYY. Rango: 24/05/2001 – 14/09/2024. |
| 9 | `Fecha de viabilidad` | Fecha | 668 | 7,422 | Fecha en que el proyecto obtuvo la declaratoria de viabilidad (aprobación técnica y económica). Nula cuando el proyecto aún no ha sido declarado viable. |
| 10 | `Costo actualizado` | Decimal | 0 | 315,207 | Última estimación del costo total del proyecto en **soles (S/.)**, actualizada durante la ejecución. Puede diferir del monto viable por modificaciones de alcance o variación de precios. |
| 11 | `Descripción de la alternativa` | Texto | 83,238 | 254,321 | Descripción técnica de la solución propuesta para resolver el problema identificado. Campo de texto libre, frecuentemente extenso. Nulo en proyectos sin alternativa registrada. |
| 12 | `Beneficiarios` | Entero | 85,743 | 26,649 | Número de personas beneficiadas directamente por el proyecto. Nulo en 18.3% de los registros. |
| 13 | `Departamento` | Texto | 0 | 25 | Departamento del Perú donde se ejecuta el proyecto. Los 25 departamentos del territorio nacional están representados. |
| 14 | `Provincia` | Texto | 11 | 197 | Provincia dentro del departamento. Puede contener `- TODOS -` para proyectos de alcance provincial completo. |
| 15 | `Distrito` | Texto | 27 | 1,738 | Distrito de ejecución del proyecto. Puede contener `- TODOS -` para proyectos de alcance distrital completo. |
| 16 | `Ubigeo` | Entero | 0 | 2,145 | Código de ubicación geográfica estándar del INEI. Permite identificar de forma única cada circunscripción territorial y cruzar con otros datasets oficiales del Estado peruano. |

### Notas sobre calidad del dato

- **Código único con nulos (4,328):** Proyectos registrados antes de la implementación del código único o con datos incompletos en la migración al sistema.
- **Ejecutora con nulos (3,655):** En algunos casos la entidad actúa directamente como ejecutora sin una unidad diferenciada.
- **Beneficiarios con nulos (85,743 — 18.3%):** Campo no obligatorio en el sistema Invierte.pe, especialmente en proyectos de infraestructura.
- **Descripción con nulos (83,238 — 17.8%):** Campo opcional, mayoritariamente vacío en proyectos de menor envergadura.

---

## 2. Data Mart: `Datamart_Inversiones_Peru` (SQL Server)

Modelo dimensional tipo **estrella** construido sobre el dataset fuente.

---

### 2.1 Tabla de Hechos: `Fact_Inversiones`

Tabla central del modelo dimensional. Cada fila representa un proyecto de inversión pública con sus métricas y claves foráneas a las dimensiones.

| Columna | Tipo SQL | Nulos | Descripción |
|---------|----------|-------|-------------|
| `id_hecho` | INT IDENTITY PK | No | Clave primaria surrogate, generada automáticamente. |
| `codigo_inversion` | BIGINT | No | Código único del proyecto en Invierte.pe (puede repetirse en proyectos multiregionales). |
| `nombre_inversion` | NVARCHAR(500) | No | Nombre oficial del proyecto (máximo 490 caracteres). |
| `id_tiempo_registro` | INT FK | No | Referencia a `Dim_Tiempo` — fecha de ingreso al sistema. Formato YYYYMMDD. |
| `id_tiempo_viabilidad` | INT FK | Sí | Referencia a `Dim_Tiempo` — fecha de declaratoria de viabilidad. NULL si no tiene. |
| `id_ubicacion` | INT FK | No | Referencia a `Dim_Ubicacion` — departamento, provincia y distrito. |
| `id_sector` | INT FK | No | Referencia a `Dim_Sector` — sector del gobierno responsable. |
| `id_entidad` | INT FK | No | Referencia a `Dim_Entidad` — entidad y unidad ejecutora. |
| `id_estado` | INT FK | No | Referencia a `Dim_Estado` — estado activo o cerrado. |
| `monto_viable` | DECIMAL(20,2) | No | Presupuesto aprobado en viabilidad, en soles. |
| `costo_actualizado` | DECIMAL(20,2) | No | Costo actualizado del proyecto, en soles. |
| `beneficiarios` | INT | Sí | Número de beneficiarios directos. NULL cuando no fue registrado. |
| `variacion_costo` | Calculada | — | Columna computada: `costo_actualizado - monto_viable`. Positivo = sobrecosto. |

---

### 2.2 Dimensión: `Dim_Tiempo`

Calendario genérico que cubre del 01/01/2000 al 31/12/2030 (11,323 filas). Referenciada **dos veces** por la Fact Table.

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_tiempo` | INT PK | Clave en formato YYYYMMDD (ej: 20150301). Permite joins directos con fechas. |
| `fecha` | DATE | Fecha completa. |
| `anio` | INT | Año (2000–2030). |
| `trimestre` | INT | Trimestre del año (1 a 4). |
| `mes` | INT | Mes del año (1 a 12). |
| `nombre_mes` | VARCHAR(20) | Nombre del mes en español (Enero, Febrero…). |
| `semana` | INT | Semana del año (1 a 53). |
| `dia` | INT | Día del mes (1 a 31). |
| `nombre_dia` | VARCHAR(20) | Nombre del día en español (Lunes, Martes…). |
| `es_fin_semana` | BIT | 1 = sábado o domingo, 0 = día hábil. |

---

### 2.3 Dimensión: `Dim_Ubicacion`

Jerarquía geográfica completa del Perú. **2,174 filas** (combinaciones únicas departamento-provincia-distrito).

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_ubicacion` | INT IDENTITY PK | Clave surrogate. |
| `ubigeo` | VARCHAR(10) | Código INEI de ubicación geográfica. Permite cruzar con otros datasets oficiales. |
| `departamento` | VARCHAR(100) | Nombre del departamento (25 valores únicos). |
| `provincia` | VARCHAR(100) | Nombre de la provincia (197 valores únicos). `SIN PROVINCIA` cuando no fue registrado. |
| `distrito` | VARCHAR(100) | Nombre del distrito (1,738 valores únicos). `SIN DISTRITO` cuando no fue registrado. |

---

### 2.4 Dimensión: `Dim_Sector`

Sectores del gobierno nacional. **34 filas.**

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_sector` | INT IDENTITY PK | Clave surrogate. |
| `nombre_sector` | VARCHAR(100) | Nombre oficial del sector (ej: `TRANSPORTES Y COMUNICACIONES`, `SALUD`, `EDUCACION`). |

---

### 2.5 Dimensión: `Dim_Entidad`

Entidades públicas y sus unidades ejecutoras. **9,923 filas.**

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_entidad` | INT IDENTITY PK | Clave surrogate. |
| `nombre_entidad` | VARCHAR(300) | Nombre de la entidad pública responsable (ministerio, gobierno regional o local). |
| `nombre_ejecutora` | VARCHAR(300) | Unidad ejecutora del presupuesto. `SIN EJECUTORA` cuando la entidad ejecuta directamente. |

---

### 2.6 Dimensión: `Dim_Estado`

Estado del proyecto. **2 filas** (tabla de dominio).

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_estado` | INT IDENTITY PK | 1 = ACTIVO, 2 = CERRADO |
| `estado` | VARCHAR(20) | `ACTIVO`: proyecto en formulación, evaluación o ejecución. `CERRADO`: proyecto concluido o desactivado. |

---

### 2.7 Tabla de Auditoría: `Log_Fact_Inversiones`

Registrada automáticamente por el **trigger `trg_Auditoria_Fact`** ante cada INSERT o DELETE en `Fact_Inversiones`. No forma parte del modelo dimensional.

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_log` | INT IDENTITY PK | Clave del registro de auditoría. |
| `accion` | VARCHAR(10) | Tipo de operación: `INSERT` o `DELETE`. |
| `id_hecho` | INT | ID del registro afectado en `Fact_Inversiones`. |
| `codigo_inversion` | BIGINT | Código del proyecto afectado. |
| `fecha_accion` | DATETIME | Fecha y hora exacta de la operación (automática, `GETDATE()`). |
| `usuario` | VARCHAR(100) | Usuario de SQL Server que ejecutó la operación (automático, `SYSTEM_USER`). |

---

## 3. Relaciones del Modelo

```
Fact_Inversiones.id_tiempo_registro   → Dim_Tiempo.id_tiempo
Fact_Inversiones.id_tiempo_viabilidad → Dim_Tiempo.id_tiempo
Fact_Inversiones.id_ubicacion         → Dim_Ubicacion.id_ubicacion
Fact_Inversiones.id_sector            → Dim_Sector.id_sector
Fact_Inversiones.id_entidad           → Dim_Entidad.id_entidad
Fact_Inversiones.id_estado            → Dim_Estado.id_estado
```

---

*Diccionario generado a partir del análisis de 468,428 registros del dataset fuente.*  
*Última actualización: Mayo 2025*
