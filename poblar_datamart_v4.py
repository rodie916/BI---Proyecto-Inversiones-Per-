
import pandas as pd
import pyodbc

# ── CONFIGURACIÓN ──────────────────────────────────────────
RUTA_EXCEL = r"C:\BI\Inversiones_Peru_Consolidado.xlsx"

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=Datamart_Inversiones_Peru;"
    "Trusted_Connection=yes;"
)
# ───────────────────────────────────────────────────────────

def conectar():
    try:
        conn = pyodbc.connect(CONN_STR)
        conn.autocommit = False
        print("Conexión exitosa")
        return conn
    except Exception as e:
        print(f"Error de conexión: {e}")
        print("  → Prueba cambiando SERVER a: localhost\\SQLEXPRESS")
        raise

def cargar_excel():
    print(f"\nCargando Excel...")
    df = pd.read_excel(RUTA_EXCEL)
    df['Ejecutora']     = df['Ejecutora'].fillna('SIN EJECUTORA')
    df['Provincia']     = df['Provincia'].fillna('SIN PROVINCIA')
    df['Distrito']      = df['Distrito'].fillna('SIN DISTRITO')
    df['Beneficiarios'] = pd.to_numeric(df['Beneficiarios'], errors='coerce').fillna(0).astype(int)
    df['Ubigeo']        = df['Ubigeo'].fillna('0').astype(str).str.strip()
    df['Código único de inversión'] = pd.to_numeric(
        df['Código único de inversión'], errors='coerce').fillna(0).astype(int)

    def tipo_intervencion(nombre):
        n = str(nombre).upper().strip()
        for v in ['MEJORAMIENTO','CREACION','CONSTRUCCION','INSTALACION','ADQUISICION',
                  'AMPLIACION','FORTALECIMIENTO','REHABILITACION','RECUPERACION',
                  'MANTENIMIENTO','EQUIPAMIENTO','IMPLEMENTACION','ESTUDIOS','PROGRAMA','PROYECTO']:
            if n.startswith(v):
                return v
        return 'OTROS'

    def nivel_gobierno(entidad):
        e = str(entidad).upper()
        if any(x in e for x in ['GOBIERNO REGIONAL','REGION ','GERENCIA REGIONAL']):
            return 'GOBIERNO REGIONAL'
        elif any(x in e for x in ['MUNICIPALIDAD','GOBIERNO LOCAL']):
            return 'GOBIERNO LOCAL'
        elif any(x in e for x in ['MINISTERIO','ORGANISMO','INSTITUTO','PROGRAMA']):
            return 'GOBIERNO NACIONAL'
        return 'OTROS'

    def rango_monto(m):
        m = float(m)
        if m < 1_000_000:       return 'PEQUEÑO (< 1M)'
        elif m < 10_000_000:    return 'MEDIANO (1M - 10M)'
        elif m < 100_000_000:   return 'GRANDE (10M - 100M)'
        else:                   return 'MUY GRANDE (> 100M)'

    df['tipo_intervencion'] = df['Nombre de la inversión'].apply(tipo_intervencion)
    df['nivel_gobierno']    = df['Entidad'].apply(nivel_gobierno)
    df['rango_monto']       = df['Monto viable'].apply(rango_monto)

    print(f" {len(df):,} filas cargadas")
    return df

def limpiar(cur):
    print("\nLimpiando tablas para re-insertar...")
    cur.execute("DELETE FROM Fact_Inversiones")
    cur.execute("DELETE FROM Dim_Entidad")
    cur.execute("DELETE FROM Dim_Ubicacion")
    cur.execute("DELETE FROM Dim_Sector")
    cur.connection.commit()
    print(" Listo (Dim_Tiempo, Dim_Estado, Dim_NivelGobierno, Dim_TipoIntervencion, Dim_RangoMonto conservados)")

def poblar_sector(cur, df):
    print("\n[1/6] Dim_Sector...")
    sec = df[['Sector']].drop_duplicates().sort_values('Sector').reset_index(drop=True)
    sec.index += 1
    cur.execute("SET IDENTITY_INSERT Dim_Sector ON")
    cur.executemany("INSERT INTO Dim_Sector(id_sector,nombre_sector) VALUES(?,?)",
                    [(int(i), str(r['Sector'])) for i, r in sec.iterrows()])
    cur.execute("SET IDENTITY_INSERT Dim_Sector OFF")
    cur.connection.commit()
    print(f"   {len(sec)} sectores")
    return {r['Sector']: int(i) for i, r in sec.iterrows()}

def poblar_ubicacion(cur, df):
    print("[2/6] Dim_Ubicacion...")
    ub = (df[['Departamento','Provincia','Distrito','Ubigeo']]
          .drop_duplicates().sort_values(['Departamento','Provincia','Distrito'])
          .reset_index(drop=True))
    ub.index += 1
    cur.execute("SET IDENTITY_INSERT Dim_Ubicacion ON")
    cur.executemany("INSERT INTO Dim_Ubicacion(id_ubicacion,ubigeo,departamento,provincia,distrito) VALUES(?,?,?,?,?)",
                    [(int(i), str(r['Ubigeo']), str(r['Departamento']), str(r['Provincia']), str(r['Distrito']))
                     for i, r in ub.iterrows()])
    cur.execute("SET IDENTITY_INSERT Dim_Ubicacion OFF")
    cur.connection.commit()
    print(f"   {len(ub)} ubicaciones")
    return {(r['Departamento'],r['Provincia'],r['Distrito'],str(r['Ubigeo']).strip()): int(i)
            for i, r in ub.iterrows()}

def poblar_entidad(cur, df):
    print("[3/6] Dim_Entidad...")
    ent = df[['Entidad','Ejecutora']].drop_duplicates().sort_values(['Entidad','Ejecutora']).reset_index(drop=True)
    ent.index += 1
    cur.execute("SET IDENTITY_INSERT Dim_Entidad ON")
    batch = []
    for i, r in ent.iterrows():
        batch.append((int(i), str(r['Entidad']), str(r['Ejecutora'])))
        if len(batch) == 500:
            cur.executemany("INSERT INTO Dim_Entidad(id_entidad,nombre_entidad,nombre_ejecutora) VALUES(?,?,?)", batch)
            batch = []
    if batch:
        cur.executemany("INSERT INTO Dim_Entidad(id_entidad,nombre_entidad,nombre_ejecutora) VALUES(?,?,?)", batch)
    cur.execute("SET IDENTITY_INSERT Dim_Entidad OFF")
    cur.connection.commit()
    print(f"   {len(ent)} entidades")
    return {(str(r['Entidad']),str(r['Ejecutora'])): int(i) for i, r in ent.iterrows()}

def cargar_lookups_fijos(cur):
    """Carga los IDs de las dims fijas desde SQL"""
    print("[4/6] Cargando dims fijas (Estado, NivelGobierno, TipoIntervencion, RangoMonto)...")
    cur.execute("SELECT estado, id_estado FROM Dim_Estado")
    estado_map = {r[0]: r[1] for r in cur.fetchall()}

    cur.execute("SELECT nivel_gobierno, id_nivel_gobierno FROM Dim_NivelGobierno")
    nivel_map = {r[0]: r[1] for r in cur.fetchall()}

    cur.execute("SELECT tipo_intervencion, id_tipo_intervencion FROM Dim_TipoIntervencion")
    tipo_map = {r[0]: r[1] for r in cur.fetchall()}

    cur.execute("SELECT rango_monto, id_rango_monto FROM Dim_RangoMonto")
    rango_map = {r[0]: r[1] for r in cur.fetchall()}

    print("   Listo")
    return estado_map, nivel_map, tipo_map, rango_map

def poblar_fact(cur, df, sec_map, ub_map, ent_map, estado_map, nivel_map, tipo_map, rango_map):
    print("[5/6] Fact_Inversiones (468K filas — ~5 min)...")

    df['id_tr'] = pd.to_datetime(df['Fecha de registro'], dayfirst=True, errors='coerce')\
                    .dt.strftime('%Y%m%d').fillna('20000101').astype(int)
    df['id_tv'] = pd.to_datetime(df['Fecha de viabilidad'], dayfirst=True, errors='coerce')\
                    .dt.strftime('%Y%m%d')

    sql = """INSERT INTO Fact_Inversiones
             (codigo_inversion,nombre_inversion,
              id_tiempo_registro,id_tiempo_viabilidad,
              id_ubicacion,id_sector,id_entidad,id_estado,
              id_nivel_gobierno,id_tipo_intervencion,id_rango_monto,
              monto_viable,costo_actualizado,beneficiarios)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

    batch, insertados, total = [], 0, len(df)

    for _, row in df.iterrows():
        id_tv = int(row['id_tv']) if pd.notna(row['id_tv']) and row['id_tv'] != '' else None
        ub_key = (row['Departamento'], row['Provincia'], row['Distrito'], str(row['Ubigeo']).strip())

        batch.append((
            int(row['Código único de inversión']),
            str(row['Nombre de la inversión'])[:490],
            int(row['id_tr']),
            id_tv,
            ub_map.get(ub_key, 1),
            sec_map.get(row['Sector'], 1),
            ent_map.get((str(row['Entidad']), str(row['Ejecutora'])), 1),
            estado_map.get(row['Estado de la inversión'], 1),
            nivel_map.get(row['nivel_gobierno'], 1),
            tipo_map.get(row['tipo_intervencion'], 16),   # 16 = OTROS
            rango_map.get(row['rango_monto'], 1),
            round(float(row['Monto viable']), 2),
            round(float(row['Costo actualizado']), 2),
            int(row['Beneficiarios'])
        ))

        if len(batch) == 1000:
            cur.executemany(sql, batch)
            cur.connection.commit()
            insertados += 1000
            batch = []
            print(f"  → {insertados:,}/{total:,} ({insertados/total*100:.0f}%)...", end='\r')

    if batch:
        cur.executemany(sql, batch)
        cur.connection.commit()
        insertados += len(batch)

    print(f"\n   {insertados:,} filas insertadas")

def verificar(cur):
    print("\n[6/6] VERIFICACIÓN FINAL ══════════════════════")
    tablas = ['Dim_Tiempo','Dim_Ubicacion','Dim_Sector','Dim_Entidad',
              'Dim_Estado','Dim_NivelGobierno','Dim_TipoIntervencion',
              'Dim_RangoMonto','Fact_Inversiones']
    for t in tablas:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        print(f"  {'' if n>0 else '✗'}  {t}: {n:,} filas")
    print("════════════════════════════════════════════════")

if __name__ == '__main__':
    conn = conectar()
    cur  = conn.cursor()
    df   = cargar_excel()

    limpiar(cur)
    sec_map  = poblar_sector(cur, df)
    ub_map   = poblar_ubicacion(cur, df)
    ent_map  = poblar_entidad(cur, df)
    estado_map, nivel_map, tipo_map, rango_map = cargar_lookups_fijos(cur)
    poblar_fact(cur, df, sec_map, ub_map, ent_map, estado_map, nivel_map, tipo_map, rango_map)
    verificar(cur)

    cur.close()
    conn.close()
    print("\n Data Mart poblado exitosamente.")
