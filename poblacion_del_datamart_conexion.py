import sqlite3
import pandas as pd
import getpass
import unicodedata
from datetime import datetime

EXCEL_PATH = "Inversiones_Peru_Consolidado.xlsx"
DB_PATH = "datamart_inversiones.db"
USUARIO_ETL = getpass.getuser()

# Categorías fijas (orden = id_* generado por AUTOINCREMENT)
NIVELES_GOBIERNO = ["GOBIERNO NACIONAL", "GOBIERNO REGIONAL", "GOBIERNO LOCAL", "OTROS"]
TIPOS_INTERVENCION = [
    "MEJORAMIENTO", "CREACION", "CONSTRUCCION", "INSTALACION", "ADQUISICION",
    "AMPLIACION", "FORTALECIMIENTO", "REHABILITACION", "RECUPERACION",
    "MANTENIMIENTO", "EQUIPAMIENTO", "IMPLEMENTACION", "ESTUDIOS",
    "PROGRAMA", "PROYECTO", "OTROS"
]


def quitar_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def clasificar_nivel_gobierno(entidad):
    e = quitar_tildes(str(entidad).upper())
    if "GOBIERNO REGIONAL" in e or e.startswith("REGION "):
        return "GOBIERNO REGIONAL"
    if "MUNICIPALIDAD" in e or "MANCOMUNIDAD MUNICIPAL" in e:
        return "GOBIERNO LOCAL"
    if ("MINISTERIO" in e or "NACIONAL" in e or e.startswith("PRESIDENCIA") or "CONGRESO" in e
            or "PODER JUDICIAL" in e or "ESSALUD" in e or "FUERO MILITAR" in e or "FONDO" in e
            or "EMPRESA" in e or "AUTORIDAD" in e or "ORGANISMO" in e or "SUNAT" in e
            or "SUNARP" in e or "JNE" in e or "ONPE" in e or "RENIEC" in e):
        return "GOBIERNO NACIONAL"
    return "OTROS"


def clasificar_tipo_intervencion(nombre_inversion):
    primera = quitar_tildes(str(nombre_inversion).strip().upper()).split()[0]
    primera = primera.strip(",.;:")
    return primera if primera in TIPOS_INTERVENCION else "OTROS"


# ----------------------------------------------------------------------- Conexión
def get_connection_destino():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        print(f"✓ Conexión a destino exitosa ({DB_PATH})")
        return conn
    except sqlite3.Error as e:
        print(f"Error de conexión al destino: {e}")
        return None


# ----------------------------------------------------------------------- Esquema
def create_datamart_schema(conn):
    create_script = """
    CREATE TABLE IF NOT EXISTS Dim_Tiempo (
        id_tiempo INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL UNIQUE,
        anio INTEGER NOT NULL,
        trimestre INTEGER NOT NULL,
        mes INTEGER NOT NULL,
        nombre_mes TEXT NOT NULL,
        semana INTEGER NOT NULL,
        dia INTEGER NOT NULL,
        nombre_dia TEXT NOT NULL,
        es_fin_semana INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Dim_Sector (
        id_sector INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_sector TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Dim_Entidad (
        id_entidad INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_entidad TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Dim_Ejecutora (
        id_ejecutora INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_ejecutora TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Dim_Estado (
        id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
        estado TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Dim_Ubicacion (
        id_ubicacion INTEGER PRIMARY KEY AUTOINCREMENT,
        ubigeo INTEGER NOT NULL UNIQUE,
        departamento TEXT NOT NULL,
        provincia TEXT NOT NULL,
        distrito TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Dim_NivelGobierno (
        id_nivel_gobierno INTEGER PRIMARY KEY AUTOINCREMENT,
        nivel_gobierno TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Dim_TipoIntervencion (
        id_tipo_intervencion INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_intervencion TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Dim_Inversion (
        id_inversion INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_inversion INTEGER NOT NULL UNIQUE,
        nombre_inversion TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Fact_Inversiones (
        id_hecho INTEGER PRIMARY KEY AUTOINCREMENT,
        id_inversion INTEGER NOT NULL,
        id_tiempo_registro INTEGER NOT NULL,
        id_tiempo_viabilidad INTEGER,
        id_ubicacion INTEGER NOT NULL,
        id_sector INTEGER NOT NULL,
        id_entidad INTEGER NOT NULL,
        id_estado INTEGER NOT NULL,
        id_ejecutora INTEGER,
        id_nivel_gobierno INTEGER NOT NULL,
        id_tipo_intervencion INTEGER NOT NULL,
        monto_viable REAL NOT NULL,
        costo_actualizado REAL NOT NULL,
        beneficiarios INTEGER NOT NULL,
        variacion_costo REAL NOT NULL,
        FOREIGN KEY (id_inversion) REFERENCES Dim_Inversion(id_inversion),
        FOREIGN KEY (id_tiempo_registro) REFERENCES Dim_Tiempo(id_tiempo),
        FOREIGN KEY (id_tiempo_viabilidad) REFERENCES Dim_Tiempo(id_tiempo),
        FOREIGN KEY (id_ubicacion) REFERENCES Dim_Ubicacion(id_ubicacion),
        FOREIGN KEY (id_sector) REFERENCES Dim_Sector(id_sector),
        FOREIGN KEY (id_entidad) REFERENCES Dim_Entidad(id_entidad),
        FOREIGN KEY (id_estado) REFERENCES Dim_Estado(id_estado),
        FOREIGN KEY (id_ejecutora) REFERENCES Dim_Ejecutora(id_ejecutora),
        FOREIGN KEY (id_nivel_gobierno) REFERENCES Dim_NivelGobierno(id_nivel_gobierno),
        FOREIGN KEY (id_tipo_intervencion) REFERENCES Dim_TipoIntervencion(id_tipo_intervencion)
    );

    CREATE TABLE IF NOT EXISTS Log_Fact_Inversiones (
        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
        accion TEXT NOT NULL,
        id_hecho INTEGER,
        codigo_inversion INTEGER,
        fecha_accion TEXT NOT NULL,
        usuario TEXT NOT NULL
    );
    """
    conn.executescript(create_script)
    conn.commit()


def clean_datamart(conn):
    print("🧹 Limpiando Data Mart...")
    cursor = conn.cursor()
    for tabla in ["Log_Fact_Inversiones", "Fact_Inversiones", "Dim_Inversion", "Dim_Ubicacion",
                  "Dim_TipoIntervencion", "Dim_NivelGobierno",
                  "Dim_Estado", "Dim_Ejecutora", "Dim_Entidad", "Dim_Sector", "Dim_Tiempo"]:
        cursor.execute(f"DELETE FROM {tabla}")
        print(f"  → {tabla} vaciada.")
    conn.commit()
    print("✓ Data Mart limpiado completamente.\n")


def mapa_id(conn, query):
    """Lee un mapeo clave->id desde la base, forzando el id a int nativo de Python."""
    df_map = pd.read_sql(query, conn)
    col_clave, col_id = df_map.columns
    return {k: int(v) for k, v in zip(df_map[col_clave], df_map[col_id])}


# ----------------------------------------------------------------------- Extracción y transformación
print("Leyendo Excel...")
df = pd.read_excel(EXCEL_PATH)

# Regla de negocio: descartar filas sin código único de inversión
filas_antes = len(df)
df = df.dropna(subset=["Código único de inversión"])
print(f"✓ {filas_antes - len(df)} filas descartadas por código de inversión vacío.")

# Regla de negocio: beneficiarios nulo -> 0
df["Beneficiarios"] = df["Beneficiarios"].fillna(0).astype(int)

df["Código único de inversión"] = df["Código único de inversión"].astype("int64")
df["Fecha de registro"] = pd.to_datetime(df["Fecha de registro"], dayfirst=True, errors="coerce")
df["Fecha de viabilidad"] = pd.to_datetime(df["Fecha de viabilidad"], dayfirst=True, errors="coerce")

# Limpieza de espacios en blanco (evita duplicados por espacios finales)
# Nota: pandas 3.x usa dtype 'string' nullable -> los vacíos son pd.NA real, no el texto "nan",
# por eso se usa fillna() en vez de replace('nan', ...).
for col in ["Sector", "Entidad", "Estado de la inversión"]:
    df[col] = df[col].astype(str).str.strip()

df["Ejecutora"] = df["Ejecutora"].astype(str).str.strip()
df["Ejecutora"] = df["Ejecutora"].replace("nan", None).where(df["Ejecutora"].notna(), None)
df["Ejecutora"] = df["Ejecutora"].where(df["Ejecutora"] != "", None)

# Ubicación: Dim_Ubicacion no admite NULL, los vacíos se marcan como "NO ESPECIFICADO"
for col in ["Departamento", "Provincia", "Distrito"]:
    df[col] = df[col].fillna("NO ESPECIFICADO").astype(str).str.strip()
    df[col] = df[col].replace("", "NO ESPECIFICADO")

# Conexión y esquema
dest_conn = get_connection_destino()
if not dest_conn:
    exit(1)
dest_cursor = dest_conn.cursor()

create_datamart_schema(dest_conn)
print("✓ Esquema del Data Mart creado.")
clean_datamart(dest_conn)

# ----------------------------------------------------------------------- Dim_Sector
print("Cargando Dim_Sector...")
sectores = sorted(df["Sector"].dropna().unique())
dest_cursor.executemany("INSERT INTO Dim_Sector (nombre_sector) VALUES (?)", [(s,) for s in sectores])
dest_conn.commit()
sector_to_id = mapa_id(dest_conn, "SELECT nombre_sector, id_sector FROM Dim_Sector")
print(f"✓ {len(sectores)} sectores cargados.")

# ----------------------------------------------------------------------- Dim_Entidad
print("Cargando Dim_Entidad...")
entidades = sorted(df["Entidad"].dropna().unique())
dest_cursor.executemany("INSERT INTO Dim_Entidad (nombre_entidad) VALUES (?)", [(e,) for e in entidades])
dest_conn.commit()
entidad_to_id = mapa_id(dest_conn, "SELECT nombre_entidad, id_entidad FROM Dim_Entidad")
print(f"✓ {len(entidades)} entidades cargadas.")

# ----------------------------------------------------------------------- Dim_Ejecutora
print("Cargando Dim_Ejecutora...")
ejecutoras = sorted(df["Ejecutora"].dropna().unique())
dest_cursor.executemany("INSERT INTO Dim_Ejecutora (nombre_ejecutora) VALUES (?)", [(e,) for e in ejecutoras])
dest_conn.commit()
ejecutora_to_id = mapa_id(dest_conn, "SELECT nombre_ejecutora, id_ejecutora FROM Dim_Ejecutora")
print(f"✓ {len(ejecutoras)} ejecutoras cargadas.")

# ----------------------------------------------------------------------- Dim_Estado
print("Cargando Dim_Estado...")
estados = sorted(df["Estado de la inversión"].dropna().unique())
dest_cursor.executemany("INSERT INTO Dim_Estado (estado) VALUES (?)", [(e,) for e in estados])
dest_conn.commit()
estado_to_id = mapa_id(dest_conn, "SELECT estado, id_estado FROM Dim_Estado")
print(f"✓ {len(estados)} estados cargados.")

# ----------------------------------------------------------------------- Dim_Ubicacion
print("Cargando Dim_Ubicacion...")
df_ubic = df[["Ubigeo", "Departamento", "Provincia", "Distrito"]].dropna(subset=["Ubigeo"]).drop_duplicates(subset=["Ubigeo"])
dest_cursor.executemany(
    "INSERT INTO Dim_Ubicacion (ubigeo, departamento, provincia, distrito) VALUES (?, ?, ?, ?)",
    list(df_ubic.itertuples(index=False, name=None))
)
dest_conn.commit()
ubigeo_to_id = mapa_id(dest_conn, "SELECT ubigeo, id_ubicacion FROM Dim_Ubicacion")
print(f"✓ {len(df_ubic)} ubicaciones cargadas.")

# ----------------------------------------------------------------------- Dim_NivelGobierno (derivada de Entidad)
print("Cargando Dim_NivelGobierno...")
dest_cursor.executemany("INSERT INTO Dim_NivelGobierno (nivel_gobierno) VALUES (?)", [(n,) for n in NIVELES_GOBIERNO])
dest_conn.commit()
nivel_to_id = mapa_id(dest_conn, "SELECT nivel_gobierno, id_nivel_gobierno FROM Dim_NivelGobierno")
df["nivel_gobierno"] = df["Entidad"].apply(clasificar_nivel_gobierno)
print(f"✓ {len(NIVELES_GOBIERNO)} niveles de gobierno cargados.")

# ----------------------------------------------------------------------- Dim_TipoIntervencion (derivada del nombre)
print("Cargando Dim_TipoIntervencion...")
dest_cursor.executemany("INSERT INTO Dim_TipoIntervencion (tipo_intervencion) VALUES (?)", [(t,) for t in TIPOS_INTERVENCION])
dest_conn.commit()
tipo_to_id = mapa_id(dest_conn, "SELECT tipo_intervencion, id_tipo_intervencion FROM Dim_TipoIntervencion")
df["tipo_intervencion"] = df["Nombre de la inversión"].apply(clasificar_tipo_intervencion)
print(f"✓ {len(TIPOS_INTERVENCION)} tipos de intervención cargados.")

# ----------------------------------------------------------------------- Dim_Inversion (codigo + nombre del proyecto)
print("Cargando Dim_Inversion...")
df["Nombre de la inversión"] = df["Nombre de la inversión"].astype(str).str.strip()
df_inversion = df[["Código único de inversión", "Nombre de la inversión"]].drop_duplicates(
    subset=["Código único de inversión"]
)
dest_cursor.executemany(
    "INSERT INTO Dim_Inversion (codigo_inversion, nombre_inversion) VALUES (?, ?)",
    list(df_inversion.itertuples(index=False, name=None))
)
dest_conn.commit()
inversion_to_id = mapa_id(dest_conn, "SELECT codigo_inversion, id_inversion FROM Dim_Inversion")
print(f"✓ {len(df_inversion)} inversiones (proyectos únicos) cargadas en Dim_Inversion.")

# ----------------------------------------------------------------------- Dim_Tiempo
print("Cargando Dim_Tiempo...")
fechas = pd.concat([df["Fecha de registro"], df["Fecha de viabilidad"]]).dropna().drop_duplicates().sort_values()
dim_tiempo_rows = []
for f in fechas:
    dim_tiempo_rows.append((
        str(f.date()), f.year, ((f.month - 1) // 3) + 1, f.month, f.month_name(),
        int(f.isocalendar()[1]), f.day, f.day_name(), int(f.dayofweek >= 5)
    ))
dest_cursor.executemany(
    "INSERT INTO Dim_Tiempo (fecha, anio, trimestre, mes, nombre_mes, semana, dia, nombre_dia, es_fin_semana) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    dim_tiempo_rows
)
dest_conn.commit()
df_tiempo_db = pd.read_sql("SELECT id_tiempo, fecha FROM Dim_Tiempo", dest_conn)
fecha_to_id = dict(zip(pd.to_datetime(df_tiempo_db["fecha"]).dt.date, df_tiempo_db["id_tiempo"].astype(int)))
print(f"✓ {len(dim_tiempo_rows)} fechas cargadas.")

# ----------------------------------------------------------------------- Fact_Inversiones
print("Cargando Fact_Inversiones...")
fact_rows = []
for _, r in df.iterrows():
    f_reg = r["Fecha de registro"].date() if pd.notna(r["Fecha de registro"]) else None
    f_via = r["Fecha de viabilidad"].date() if pd.notna(r["Fecha de viabilidad"]) else None

    id_tiempo_registro = fecha_to_id.get(f_reg)
    if id_tiempo_registro is None:
        continue  # sin fecha de registro no se puede cargar el hecho

    fact_rows.append((
        inversion_to_id.get(int(r["Código único de inversión"])),
        id_tiempo_registro,
        fecha_to_id.get(f_via),
        ubigeo_to_id.get(r["Ubigeo"]),
        sector_to_id.get(r["Sector"]),
        entidad_to_id.get(r["Entidad"]),
        estado_to_id.get(r["Estado de la inversión"]),
        ejecutora_to_id.get(r["Ejecutora"]),
        nivel_to_id.get(r["nivel_gobierno"]),
        tipo_to_id.get(r["tipo_intervencion"]),
        float(r["Monto viable"]),
        float(r["Costo actualizado"]),
        int(r["Beneficiarios"]),
        float(r["Costo actualizado"]) - float(r["Monto viable"])
    ))

dest_cursor.executemany(
    """INSERT INTO Fact_Inversiones
       (id_inversion, id_tiempo_registro, id_tiempo_viabilidad,
        id_ubicacion, id_sector, id_entidad, id_estado, id_ejecutora,
        id_nivel_gobierno, id_tipo_intervencion,
        monto_viable, costo_actualizado, beneficiarios, variacion_costo)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    fact_rows
)
dest_conn.commit()
print(f"✓ {len(fact_rows)} inversiones cargadas.")

# ----------------------------------------------------------------------- Log_Fact_Inversiones (auditoría)
print("Registrando auditoría en Log_Fact_Inversiones...")
df_fact_db = pd.read_sql(
    "SELECT f.id_hecho, di.codigo_inversion FROM Fact_Inversiones f "
    "JOIN Dim_Inversion di ON f.id_inversion = di.id_inversion",
    dest_conn
)
ahora = datetime.now().isoformat(sep=" ", timespec="seconds")
log_rows = [
    ("INSERT", int(r["id_hecho"]), int(r["codigo_inversion"]), ahora, USUARIO_ETL)
    for _, r in df_fact_db.iterrows()
]
dest_cursor.executemany(
    "INSERT INTO Log_Fact_Inversiones (accion, id_hecho, codigo_inversion, fecha_accion, usuario) "
    "VALUES (?, ?, ?, ?, ?)",
    log_rows
)
dest_conn.commit()
print(f"✓ {len(log_rows)} registros de auditoría insertados.")

dest_conn.close()
print(f"ETL completado exitosamente. Data Mart de Inversiones Perú poblado correctamente en '{DB_PATH}'.")