import pyodbc
import pandas as pd
import getpass
import unicodedata
from datetime import datetime

EXCEL_PATH = "Inversiones_Peru_Consolidado.xlsx"
USUARIO_ETL = getpass.getuser()

# Categorías fijas (orden = id_* generado por IDENTITY)
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


# Conexión de manera tradicional
'''def get_connection_destino():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;'
            'DATABASE=InversionesDW;'
            'UID=sa;'
            'PWD=1234567890'
        )
        conn.autocommit = False
        print("✓ Conexión a destino exitosa")
        return conn
    except pyodbc.Error as e:
        print(f"Error de conexión al destino: {e}")
        return None'''

#Para el caso de realización en el trabajo
def get_connection_destino():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=LAPTOP-QDTQNSI1;'
            'DATABASE=InversionesDW;'
            'Trusted_Connection=yes;'
        )
        conn.autocommit = False
        print("✓ Conexión a destino exitosa")
        return conn
    except pyodbc.Error as e:
        print(f"Error de conexión al destino: {e}")
        return None

# ----------------------------------------------------------------------- Esquema
def create_datamart_schema(cursor):
    create_script = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Dim_Tiempo' AND xtype='U')
    CREATE TABLE Dim_Tiempo (
        id_tiempo INT IDENTITY(1,1) PRIMARY KEY,
        fecha DATE NOT NULL UNIQUE,
        anio INT NOT NULL,
        trimestre INT NOT NULL,
        mes INT NOT NULL,
        nombre_mes NVARCHAR(15) NOT NULL,
        semana INT NOT NULL,
        dia INT NOT NULL,
        nombre_dia NVARCHAR(15) NOT NULL,
        es_fin_semana BIT NOT NULL
    );

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Dim_Sector' AND xtype='U')
    CREATE TABLE Dim_Sector (
        id_sector INT IDENTITY(1,1) PRIMARY KEY,
        nombre_sector NVARCHAR(150) NOT NULL UNIQUE
    );

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Dim_Entidad' AND xtype='U')
    CREATE TABLE Dim_Entidad (
        id_entidad INT IDENTITY(1,1) PRIMARY KEY,
        nombre_entidad NVARCHAR(250) NOT NULL UNIQUE
    );

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Dim_Ejecutora' AND xtype='U')
    CREATE TABLE Dim_Ejecutora (
        id_ejecutora INT IDENTITY(1,1) PRIMARY KEY,
        nombre_ejecutora NVARCHAR(250) NOT NULL UNIQUE
    );

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Dim_Estado' AND xtype='U')
    CREATE TABLE Dim_Estado (
        id_estado INT IDENTITY(1,1) PRIMARY KEY,
        estado NVARCHAR(50) NOT NULL UNIQUE
    );

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Dim_Ubicacion' AND xtype='U')
    CREATE TABLE Dim_Ubicacion (
        id_ubicacion INT IDENTITY(1,1) PRIMARY KEY,
        ubigeo INT NOT NULL UNIQUE,
        departamento NVARCHAR(100) NOT NULL,
        provincia NVARCHAR(100) NOT NULL,
        distrito NVARCHAR(100) NOT NULL
    );

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Dim_NivelGobierno' AND xtype='U')
    CREATE TABLE Dim_NivelGobierno (
        id_nivel_gobierno INT IDENTITY(1,1) PRIMARY KEY,
        nivel_gobierno VARCHAR(50) NOT NULL UNIQUE
    );

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Dim_TipoIntervencion' AND xtype='U')
    CREATE TABLE Dim_TipoIntervencion (
        id_tipo_intervencion INT IDENTITY(1,1) PRIMARY KEY,
        tipo_intervencion VARCHAR(50) NOT NULL UNIQUE
    );

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Fact_Inversiones' AND xtype='U')
    CREATE TABLE Fact_Inversiones (
        id_hecho INT IDENTITY(1,1) PRIMARY KEY,
        codigo_inversion BIGINT NOT NULL,
        nombre_inversion NVARCHAR(MAX) NOT NULL,
        id_tiempo_registro INT NOT NULL,
        id_tiempo_viabilidad INT NULL,
        id_ubicacion INT NOT NULL,
        id_sector INT NOT NULL,
        id_entidad INT NOT NULL,
        id_estado INT NOT NULL,
        id_ejecutora INT NULL,
        id_nivel_gobierno INT NOT NULL,
        id_tipo_intervencion INT NOT NULL,
        monto_viable DECIMAL(18,2) NOT NULL,
        costo_actualizado DECIMAL(18,2) NOT NULL,
        beneficiarios INT NOT NULL,
        variacion_costo DECIMAL(18,2) NOT NULL,
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

    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Log_Fact_Inversiones' AND xtype='U')
    CREATE TABLE Log_Fact_Inversiones (
        id_log INT IDENTITY(1,1) PRIMARY KEY,
        accion NVARCHAR(20) NOT NULL,
        id_hecho INT NULL,
        codigo_inversion BIGINT NULL,
        fecha_accion DATETIME NOT NULL DEFAULT GETDATE(),
        usuario NVARCHAR(100) NOT NULL
    );
    """
    cursor.execute(create_script)
    cursor.commit()


def clean_datamart(cursor, conn):
    print("🧹 Limpiando Data Mart...")
    for tabla in ["Log_Fact_Inversiones", "Fact_Inversiones", "Dim_Ubicacion",
                  "Dim_TipoIntervencion", "Dim_NivelGobierno",
                  "Dim_Estado", "Dim_Ejecutora", "Dim_Entidad", "Dim_Sector", "Dim_Tiempo"]:
        cursor.execute(f"DELETE FROM {tabla}")
        print(f"  → {tabla} vaciada.")
    conn.commit()
    print("✓ Data Mart limpiado completamente.\n")


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
# Limpieza de espacios en blanco (SQL Server ignora espacios finales en UNIQUE, Python no)
for col in ["Sector", "Entidad", "Ejecutora", "Estado de la inversión"]:
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].replace("nan", None)
df["Ejecutora"] = df["Ejecutora"].where(df["Ejecutora"].notna(), None)

# Ubicación: Dim_Ubicacion no admite NULL, los vacíos se marcan como "NO ESPECIFICADO"
for col in ["Departamento", "Provincia", "Distrito"]:
    df[col] = df[col].astype(str).str.strip().replace("nan", "NO ESPECIFICADO")
    df[col] = df[col].replace("", "NO ESPECIFICADO")

# Conexión y esquema
dest_conn = get_connection_destino()
if not dest_conn:
    exit(1)
dest_cursor = dest_conn.cursor()
dest_cursor.fast_executemany = True

create_datamart_schema(dest_cursor)
print("✓ Esquema del Data Mart creado.")
clean_datamart(dest_cursor, dest_conn)

def mapa_id(conn, query):
    """Lee un mapeo clave->id desde SQL Server forzando el id a int nativo de Python
    (evita 'Unknown object type numpy.int64' al usarlo luego con fast_executemany)."""
    df_map = pd.read_sql(query, conn)
    col_clave, col_id = df_map.columns
    return {k: int(v) for k, v in zip(df_map[col_clave], df_map[col_id])}


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

# ----------------------------------------------------------------------- Dim_Tiempo
print("Cargando Dim_Tiempo...")
fechas = pd.concat([df["Fecha de registro"], df["Fecha de viabilidad"]]).dropna().drop_duplicates().sort_values()
dim_tiempo_rows = []
for f in fechas:
    dim_tiempo_rows.append((
        f.date(), f.year, ((f.month - 1) // 3) + 1, f.month, f.month_name(),
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
        int(r["Código único de inversión"]),
        str(r["Nombre de la inversión"]),
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
       (codigo_inversion, nombre_inversion, id_tiempo_registro, id_tiempo_viabilidad,
        id_ubicacion, id_sector, id_entidad, id_estado, id_ejecutora,
        id_nivel_gobierno, id_tipo_intervencion,
        monto_viable, costo_actualizado, beneficiarios, variacion_costo)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    fact_rows
)
dest_conn.commit()
print(f"✓ {len(fact_rows)} inversiones cargadas.")

# ----------------------------------------------------------------------- Log_Fact_Inversiones (auditoría)
print("Registrando auditoría en Log_Fact_Inversiones...")
df_fact_db = pd.read_sql("SELECT id_hecho, codigo_inversion FROM Fact_Inversiones", dest_conn)
ahora = datetime.now()
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
print("ETL completado exitosamente. Data Mart de Inversiones Perú poblado correctamente.")