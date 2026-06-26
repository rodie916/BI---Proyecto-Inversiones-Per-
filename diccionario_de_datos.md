# Diccionario de Datos
## Inversión Pública en el Perú — Business Intelligence

---

## 1. Dataset Fuente: `Inversiones_Peru_Consolidado.xlsx`

Archivo consolidado a partir de 25 archivos Excel regionales descargados del portal de datos abiertos del Estado peruano (datos.gob.pe). Cada fila representa un **proyecto de inversión pública** registrado en el sistema Invierte.pe del Ministerio de Economía y Finanzas (MEF).

**Filas totales:** 468,428 · **Columnas:** 16 · **Período:** 2001–2024 · **Cobertura:** 25 departamentos

| # | Campo | Tipo | Nulos | Valores únicos | Descripción |
|---|-------|------|-------|----------------|-------------|
| 1 | `Código único de inversión` | Entero | 4,328 | 335,946 | Identificador único del proyecto en el sistema Invierte.pe. Puede aparecer en múltiples regiones si el proyecto es multiregional. |
| 2 | `Nombre de la inversión` | Texto | 0 | 339,440 | Nombre oficial del proyecto tal como aparece en el sistema. Suele incluir el tipo de intervención (mejoramiento, construcción, ampliación), el bien o servicio y la ubicación geográfica. |
| 3 | `Monto viable` | Decimal | 0 | 310,030 | Monto en **soles (S/.)** aprobado en la declaratoria de viabilidad del proyecto. Representa el presupuesto oficial aprobado. |
| 4 | `Estado de la inversión` | Texto | 0 | 2 | Estado actual del proyecto. Valores posibles: `ACTIVO` o `CERRADO`. |
| 5 | `Sector` | Texto | 0 | 34 | Sector del gobierno nacional al que pertenece la entidad responsable del proyecto. Ejemplos: `TRANSPORTES Y COMUNICACIONES`, `SALUD`, `EDUCACION`, `AGRICULTURA Y RIEGO`. |
| 6 | `Entidad` | Texto | 0 | 2,012 (2,010 tras limpieza de espacios) | Nombre de la entidad pública responsable (Ministerio, Gobierno Regional o Local). |
| 7 | `Ejecutora` | Texto | 3,655 | 2,692 (2,689 tras limpieza) | Unidad ejecutora específica dentro de la entidad responsable de gestionar el presupuesto del proyecto. Nula cuando la entidad ejecuta directamente. |
| 8 | `Fecha de registro` | Fecha | 0 | 7,845 | Fecha en que el proyecto fue ingresado al sistema Invierte.pe. Rango: 24/05/2001 – 14/09/2024. |
| 9 | `Fecha de viabilidad` | Fecha | 668 | 7,422 | Fecha en que el proyecto obtuvo la declaratoria de viabilidad. Nula cuando el proyecto aún no ha sido declarado viable. |
| 10 | `Costo actualizado` | Decimal | 0 | 315,207 | Última estimación del costo total del proyecto en soles, actualizada durante la ejecución. |
| 11 | `Descripción de la alternativa` | Texto | 83,238 | 254,321 | Descripción técnica libre. **No se incorpora al Data Mart** (no aporta a métricas de BI y no aparece en el modelo estrella). |
| 12 | `Beneficiarios` | Entero | 85,743 | 26,649 | Número de personas beneficiadas directamente. **Regla de negocio aplicada en el ETL: nulo → 0** (queda sin nulos en el Data Mart). |
| 13 | `Departamento` | Texto | 0 | 25 | Departamento del Perú donde se ejecuta el proyecto. |
| 14 | `Provincia` | Texto | 11 | 197 | Provincia dentro del departamento. **Regla de negocio: vacío → `"NO ESPECIFICADO"`** en el Data Mart. |
| 15 | `Distrito` | Texto | 27 | 1,738 | Distrito de ejecución. **Regla de negocio: vacío → `"NO ESPECIFICADO"`** en el Data Mart. |
| 16 | `Ubigeo` | Entero | 0 | 2,145 | Código de ubicación geográfica estándar del INEI. |

### Notas sobre calidad del dato

- **Código único con nulos (4,328):** estas filas **se descartan por completo** (`dropna`) — no hay forma de identificar el proyecto sin este código, regla de negocio explícita.
- **Ejecutora con nulos (3,655):** la entidad actúa directamente como ejecutora; en el Data Mart, `id_ejecutora` queda `NULL` (FK opcional).
- **Beneficiarios con nulos (85,743 — 18.3%):** se reemplazan por `0` durante el ETL.
- **Descripción de la alternativa:** columna descartada, no forma parte del modelo dimensional.
- **Filas con fecha de registro inválida:** también se excluyen del Fact, ya que no pueden ubicarse en `Dim_Tiempo`.
- **Resultado neto:** de 468,428 filas fuente, **464,100** llegan a `Fact_Inversiones` tras aplicar las reglas anteriores.

---

## 2. Data Mart: `InversionesDW` (SQL Server / SQLite)

Modelo dimensional tipo **Star Schema** con **7 dimensiones** y 1 tabla de hechos. El Data Mart se implementó primero en SQL Server (desarrollo) y se migró a **SQLite** (`datamart_inversiones.db`) para el despliegue portable — el esquema es idéntico, solo cambian los tipos nativos (`NVARCHAR`→`TEXT`, `DECIMAL`→`REAL`, `BIT`→`INTEGER`, `IDENTITY`→`AUTOINCREMENT`).

---

### 2.1 Tabla de Hechos: `Fact_Inversiones`

**464,100 filas** (tras dropna de código único y de fecha de registro). Una fila por proyecto de inversión.

| Columna | Tipo SQL | Nulos | Descripción |
|---------|----------|-------|-------------|
| `id_hecho` | INT IDENTITY/AUTOINCREMENT PK | No | Clave primaria surrogate. |
| `codigo_inversion` | BIGINT | No | Código del proyecto en Invierte.pe. |
| `nombre_inversion` | NVARCHAR(MAX) / TEXT | No | Nombre oficial del proyecto (sin límite de longitud). |
| `id_tiempo_registro` | INT FK | No | → `Dim_Tiempo`: fecha de ingreso al sistema. |
| `id_tiempo_viabilidad` | INT FK | Sí (649 filas) | → `Dim_Tiempo`: fecha de viabilidad. |
| `id_ubicacion` | INT FK | No | → `Dim_Ubicacion`. |
| `id_sector` | INT FK | No | → `Dim_Sector`. |
| `id_entidad` | INT FK | No | → `Dim_Entidad`. |
| `id_estado` | INT FK | No | → `Dim_Estado`. |
| `id_ejecutora` | INT FK | Sí (3,634 filas) | → `Dim_Ejecutora`. NULL cuando la entidad ejecuta directamente. |
| `id_nivel_gobierno` | INT FK | No | → `Dim_NivelGobierno` (derivada de `Entidad`). |
| `id_tipo_intervencion` | INT FK | No | → `Dim_TipoIntervencion` (derivada de `Nombre de la inversión`). |
| `monto_viable` | DECIMAL(18,2) / REAL | No | Presupuesto aprobado en viabilidad, en soles. |
| `costo_actualizado` | DECIMAL(18,2) / REAL | No | Costo actualizado del proyecto, en soles. |
| `beneficiarios` | INT | No (nulo→0 aplicado en ETL) | Número de beneficiarios directos. |
| `variacion_costo` | DECIMAL(18,2) / REAL | No | Calculada en el ETL: `costo_actualizado - monto_viable`. Positivo = sobrecosto. |

> **Nota:** `id_rango_monto` y `Dim_RangoMonto` del diseño original **se eliminaron** y se reemplazaron por `id_ejecutora` / `Dim_Ejecutora`, a pedido explícito del negocio.

---

### 2.2 Dim_Tiempo

**7,950 filas.** A diferencia de un calendario genérico, **solo contiene las fechas que efectivamente aparecen** en `Fecha de registro` o `Fecha de viabilidad` del Excel (más eficiente, sin filas sin uso). Referenciada **dos veces** por la Fact Table.

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_tiempo` | INT IDENTITY/AUTOINCREMENT PK | Clave surrogate secuencial (no codifica la fecha). |
| `fecha` | DATE / TEXT (ISO) | Fecha completa, única. |
| `anio` | INT | Año. |
| `trimestre` | INT | Trimestre del año (1 a 4). |
| `mes` | INT | Mes del año (1 a 12). |
| `nombre_mes` | NVARCHAR(15) / TEXT | Nombre del mes (en inglés, generado por pandas: `January`, `February`…). |
| `semana` | INT | Semana ISO del año. |
| `dia` | INT | Día del mes. |
| `nombre_dia` | NVARCHAR(15) / TEXT | Nombre del día (en inglés: `Monday`, `Tuesday`…). |
| `es_fin_semana` | BIT / INTEGER | 1 = sábado o domingo, 0 = día hábil. |

---

### 2.3 Dim_Ubicacion

**2,145 filas** (una por `Ubigeo` único). Deduplicada por `Ubigeo` como clave natural.

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_ubicacion` | INT IDENTITY/AUTOINCREMENT PK | Clave surrogate. |
| `ubigeo` | INT, UNIQUE | Código INEI de ubicación. |
| `departamento` | NVARCHAR(100) / TEXT | Nombre del departamento. |
| `provincia` | NVARCHAR(100) / TEXT | Nombre de la provincia. `"NO ESPECIFICADO"` cuando no fue registrado. |
| `distrito` | NVARCHAR(100) / TEXT | Nombre del distrito. `"NO ESPECIFICADO"` cuando no fue registrado. |

---

### 2.4 Dim_Sector

**34 filas.**

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_sector` | INT IDENTITY/AUTOINCREMENT PK | Clave surrogate. |
| `nombre_sector` | NVARCHAR(150) / TEXT, UNIQUE | Nombre oficial del sector. Ejemplos: `TRANSPORTES Y COMUNICACIONES`, `SALUD`, `EDUCACION`. |

---

### 2.5 Dim_Entidad

**2,010 filas.** Solo el nombre de la entidad — la ejecutora **ya no vive aquí** (ver 2.6).

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_entidad` | INT IDENTITY/AUTOINCREMENT PK | Clave surrogate. |
| `nombre_entidad` | NVARCHAR(250) / TEXT, UNIQUE | Nombre de la entidad pública responsable. |

---

### 2.6 Dim_Ejecutora

**2,689 filas.** Dimensión independiente (sustituye a `Dim_RangoMonto` del diseño original).

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_ejecutora` | INT IDENTITY/AUTOINCREMENT PK | Clave surrogate. |
| `nombre_ejecutora` | NVARCHAR(250) / TEXT, UNIQUE | Unidad ejecutora del presupuesto. Las filas sin ejecutora quedan con `id_ejecutora = NULL` en el Fact (no se crea una fila "SIN EJECUTORA"). |

---

### 2.7 Dim_Estado

**2 filas** (tabla de dominio).

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_estado` | INT IDENTITY/AUTOINCREMENT PK | Clave surrogate. |
| `estado` | VARCHAR(50) / TEXT, UNIQUE | `ACTIVO` (352,992 proyectos) o `CERRADO` (111,108 proyectos). |

---

### 2.8 Dim_NivelGobierno

**4 filas.** Derivada por clasificación de palabras clave sobre `Entidad` (no viene en el Excel original).

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_nivel_gobierno` | INT IDENTITY/AUTOINCREMENT PK | Clave surrogate. |
| `nivel_gobierno` | VARCHAR(50) / TEXT, UNIQUE | `GOBIERNO NACIONAL`, `GOBIERNO REGIONAL`, `GOBIERNO LOCAL`, `OTROS`. |

**Distribución real en el Data Mart:**

| Nivel | Proyectos | % |
|-------|-----------|---|
| Gobierno Local | 332,469 | 71.7% |
| Gobierno Regional | 69,524 | 15.0% |
| Gobierno Nacional | 60,815 | 13.1% |
| Otros | 1,292 | 0.3% |

---

### 2.9 Dim_TipoIntervencion

**16 filas.** Derivada de la primera palabra de `Nombre de la inversión` (normalizada sin tildes/puntuación).

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_tipo_intervencion` | INT IDENTITY/AUTOINCREMENT PK | Clave surrogate. |
| `tipo_intervencion` | VARCHAR(50) / TEXT, UNIQUE | Tipo de obra. |

**Distribución real en el Data Mart:**

| Tipo | Proyectos |
|------|-----------|
| MEJORAMIENTO | 187,267 |
| CREACION | 66,268 |
| OTROS | 62,295 |
| CONSTRUCCION | 47,851 |
| INSTALACION | 27,326 |
| ADQUISICION | 24,661 |
| AMPLIACION | 21,406 |
| REHABILITACION | 9,879 |
| FORTALECIMIENTO | 7,604 |
| RECUPERACION | 6,401 |
| EQUIPAMIENTO | 1,344 |
| IMPLEMENTACION | 1,037 |
| PROGRAMA | 615 |
| PROYECTO | 142 |
| MANTENIMIENTO | 4 |
| ESTUDIOS | 0 |

> **Nota:** `Dim_RangoMonto` (clasificación por tamaño presupuestal) **no se implementó** — fue reemplazada por `Dim_Ejecutora` a pedido explícito del negocio.

---

### 2.10 Tabla de Auditoría: `Log_Fact_Inversiones`

**464,100 filas** (una por cada fila insertada en `Fact_Inversiones`). No forma parte del modelo dimensional.

> **Corrección importante:** esta tabla **no se llena con un trigger de SQL Server** — se llena explícitamente desde el script de población en Python, inmediatamente después de cada carga del Fact. Solo registra la acción `INSERT` (no hay lógica de `DELETE`, ya que el ETL siempre limpia y recarga el Data Mart completo, no hace borrados incrementales).

| Columna | Tipo SQL | Descripción |
|---------|----------|-------------|
| `id_log` | INT IDENTITY/AUTOINCREMENT PK | Clave del registro de auditoría. |
| `accion` | NVARCHAR(20) / TEXT | Siempre `INSERT` en la implementación actual. |
| `id_hecho` | INT | ID del registro afectado en `Fact_Inversiones`. |
| `codigo_inversion` | BIGINT | Código del proyecto afectado. |
| `fecha_accion` | DATETIME / TEXT (ISO) | Fecha y hora de ejecución del ETL (`datetime.now()` en Python, no `GETDATE()`). |
| `usuario` | NVARCHAR(100) / TEXT | Usuario del sistema operativo que ejecutó el script (`getpass.getuser()`, no `SYSTEM_USER` de SQL Server). |

---

## 3. Relaciones del Modelo

```
Fact_Inversiones.id_tiempo_registro    → Dim_Tiempo.id_tiempo
Fact_Inversiones.id_tiempo_viabilidad  → Dim_Tiempo.id_tiempo
Fact_Inversiones.id_ubicacion          → Dim_Ubicacion.id_ubicacion
Fact_Inversiones.id_sector             → Dim_Sector.id_sector
Fact_Inversiones.id_entidad            → Dim_Entidad.id_entidad
Fact_Inversiones.id_ejecutora          → Dim_Ejecutora.id_ejecutora   (NULL permitido)
Fact_Inversiones.id_estado             → Dim_Estado.id_estado
Fact_Inversiones.id_nivel_gobierno     → Dim_NivelGobierno.id_nivel_gobierno
Fact_Inversiones.id_tipo_intervencion  → Dim_TipoIntervencion.id_tipo_intervencion
```

---

*Fuente: Portal de Datos Abiertos del Estado Peruano — datosabiertos.gob.pe · Sistema Invierte.pe — MEF*
*Dataset: Public Investments in Peru — Kaggle (Jenifer Grategarro)*
*Diccionario actualizado conforme a la implementación real validada en SQL Server y SQLite — Junio 2026.*
