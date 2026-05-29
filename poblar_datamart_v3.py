"""
poblar_datamart_v3.py
─────────────────────
Limpia y puebla desde cero el Datamart_Inversiones_Peru.
Funciona aunque las dimensiones ya tengan datos (borra y re-inserta).

REQUISITOS:
    pip install pandas openpyxl pyodbc

CONFIGURACIÓN:
    1. Cambia RUTA_EXCEL a donde tengas el archivo
    2. Cambia SERVER si es necesario (revisa el nombre en SSMS)
    3. Ejecuta: python poblar_datamart_v3.py
"""

import pandas as pd
import pyodbc

# ── CONFIGURACIÓN ──────────────────────────────────────────
RUTA_EXCEL = r"C:\BI\Inversiones_Peru_Consolidado.xlsx"

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"          # Cambia si es necesario
    "DATABASE=Datamart_Inversiones_Peru;"
    "Trusted_Connection=yes;"
)
# ───────────────────────────────────────────────────────────

def conectar():
    try:
        conn = pyodbc.connect(CONN_STR)
        conn.autocommit = False
        print("✓ Conexión exitosa a Datamart_Inversiones_Peru")
        return conn
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        print("  → Prueba cambiando SERVER a: localhost\\SQLEXPRESS  o al nombre que ves en SSMS")
        raise

def cargar_excel(ruta):
    print(f"\nCargando Excel ({ruta})...")
    df = pd.read_excel(ruta)
    df['Ejecutora']     = df['Ejecutora'].fillna('SIN EJECUTORA')
    df['Provincia']     = df['Provincia'].fillna('SIN PROVINCIA')
    df['Distrito']      = df['Distrito'].fillna('SIN DISTRITO')
    df['Beneficiarios'] = pd.to_numeric(df['Beneficiarios'], errors='coerce').fillna(0).astype(int)
    df['Ubigeo']        = df['Ubigeo'].fillna('0').astype(str).str.strip()
    df['Código único de inversión'] = pd.to_numeric(
        df['Código único de inversión'], errors='coerce').fillna(0).astype(int)
    print(f"✓ {len(df):,} filas cargadas")
    return df

def limpiar_tablas(cur):
    """Borra en orden correcto respetando FK"""
    print("\nLimpiando tablas existentes...")
    cur.execute("DELETE FROM Fact_Inversiones")
    cur.execute("DELETE FROM Dim_Entidad")
    cur.execute("DELETE FROM Dim_Ubicacion")
    cur.execute("DELETE FROM Dim_Sector")
    # Dim_Estado y Dim_Tiempo NO se borran (datos fijos)
    cur.connection.commit()
    print("✓ Tablas limpiadas (Dim_Tiempo y Dim_Estado conservados)")

def poblar_sector(cur, df):
    print("\n[1/4] Dim_Sector...")
    sectores = (df[['Sector']].drop_duplicates()
                .sort_values('Sector').reset_index(drop=True))
    sectores.index += 1
    cur.execute("SET IDENTITY_INSERT Dim_Sector ON")
    cur.executemany(
        "INSERT INTO Dim_Sector(id_sector, nombre_sector) VALUES(?,?)",
        [(int(i), str(row['Sector'])) for i, row in sectores.iterrows()]
    )
    cur.execute("SET IDENTITY_INSERT Dim_Sector OFF")
    cur.connection.commit()
    print(f"  ✓ {len(sectores)} sectores insertados")
    return {row['Sector']: int(i) for i, row in sectores.iterrows()}

def poblar_ubicacion(cur, df):
    print("[2/4] Dim_Ubicacion...")
    ubicaciones = (df[['Departamento','Provincia','Distrito','Ubigeo']]
                   .drop_duplicates()
                   .sort_values(['Departamento','Provincia','Distrito'])
                   .reset_index(drop=True))
    ubicaciones.index += 1
    cur.execute("SET IDENTITY_INSERT Dim_Ubicacion ON")
    batch = [(int(i), str(r['Ubigeo']), str(r['Departamento']),
              str(r['Provincia']), str(r['Distrito']))
             for i, r in ubicaciones.iterrows()]
    cur.executemany(
        "INSERT INTO Dim_Ubicacion(id_ubicacion,ubigeo,departamento,provincia,distrito) VALUES(?,?,?,?,?)",
        batch)
    cur.execute("SET IDENTITY_INSERT Dim_Ubicacion OFF")
    cur.connection.commit()
    print(f"  ✓ {len(ubicaciones)} ubicaciones insertadas")
    return {(r['Departamento'],r['Provincia'],r['Distrito'],str(r['Ubigeo']).strip()): int(i)
            for i, r in ubicaciones.iterrows()}

def poblar_entidad(cur, df):
    print("[3/4] Dim_Entidad...")
    entidades = (df[['Entidad','Ejecutora']].drop_duplicates()
                 .sort_values(['Entidad','Ejecutora']).reset_index(drop=True))
    entidades.index += 1
    cur.execute("SET IDENTITY_INSERT Dim_Entidad ON")
    # En lotes de 500 para no saturar memoria
    batch = []
    for i, row in entidades.iterrows():
        batch.append((int(i), str(row['Entidad']), str(row['Ejecutora'])))
        if len(batch) == 500:
            cur.executemany(
                "INSERT INTO Dim_Entidad(id_entidad,nombre_entidad,nombre_ejecutora) VALUES(?,?,?)",
                batch)
            batch = []
    if batch:
        cur.executemany(
            "INSERT INTO Dim_Entidad(id_entidad,nombre_entidad,nombre_ejecutora) VALUES(?,?,?)",
            batch)
    cur.execute("SET IDENTITY_INSERT Dim_Entidad OFF")
    cur.connection.commit()
    print(f"  ✓ {len(entidades)} entidades insertadas")
    return {(str(r['Entidad']), str(r['Ejecutora'])): int(i)
            for i, r in entidades.iterrows()}

def poblar_fact(cur, df, sector_map, ubic_map, ent_map):
    print("[4/4] Fact_Inversiones (468K filas — puede tardar ~5 min)...")
    estado_map = {'ACTIVO': 1, 'CERRADO': 2}

    df['id_tr'] = (pd.to_datetime(df['Fecha de registro'], dayfirst=True, errors='coerce')
                   .dt.strftime('%Y%m%d').fillna('20000101').astype(int))
    df['id_tv'] = (pd.to_datetime(df['Fecha de viabilidad'], dayfirst=True, errors='coerce')
                   .dt.strftime('%Y%m%d'))

    sql = """INSERT INTO Fact_Inversiones
             (codigo_inversion, nombre_inversion,
              id_tiempo_registro, id_tiempo_viabilidad,
              id_ubicacion, id_sector, id_entidad, id_estado,
              monto_viable, costo_actualizado, beneficiarios)
             VALUES (?,?,?,?,?,?,?,?,?,?,?)"""

    batch = []
    total = len(df)
    insertados = 0

    for _, row in df.iterrows():
        id_tv = int(row['id_tv']) if pd.notna(row['id_tv']) and row['id_tv'] != '' else None
        ub_key = (row['Departamento'], row['Provincia'],
                  row['Distrito'], str(row['Ubigeo']).strip())

        batch.append((
            int(row['Código único de inversión']),
            str(row['Nombre de la inversión'])[:490],
            int(row['id_tr']),
            id_tv,
            ubic_map.get(ub_key, 1),
            sector_map.get(row['Sector'], 1),
            ent_map.get((str(row['Entidad']), str(row['Ejecutora'])), 1),
            estado_map.get(row['Estado de la inversión'], 1),
            round(float(row['Monto viable']), 2),
            round(float(row['Costo actualizado']), 2),
            int(row['Beneficiarios'])
        ))

        if len(batch) == 1000:
            cur.executemany(sql, batch)
            cur.connection.commit()
            insertados += 1000
            batch = []
            pct = insertados / total * 100
            print(f"  → {insertados:,} / {total:,} ({pct:.0f}%)...", end='\r')

    if batch:
        cur.executemany(sql, batch)
        cur.connection.commit()
        insertados += len(batch)

    print(f"\n  ✓ {insertados:,} filas insertadas en Fact_Inversiones")

def verificar(cur):
    print("\n══ VERIFICACIÓN FINAL ══════════════════")
    for t in ['Dim_Tiempo','Dim_Ubicacion','Dim_Sector',
              'Dim_Entidad','Dim_Estado','Fact_Inversiones']:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        ok = "✓" if n > 0 else "✗ VACÍA"
        print(f"  {ok}  {t}: {n:,} filas")
    print("════════════════════════════════════════")

# ── MAIN ────────────────────────────────────────────────────
if __name__ == '__main__':
    conn = conectar()
    cur  = conn.cursor()
    df   = cargar_excel(RUTA_EXCEL)

    limpiar_tablas(cur)
    sector_map = poblar_sector(cur, df)
    ubic_map   = poblar_ubicacion(cur, df)
    ent_map    = poblar_entidad(cur, df)
    poblar_fact(cur, df, sector_map, ubic_map, ent_map)
    verificar(cur)

    cur.close()
    conn.close()
    print("\n✓ Data Mart poblado exitosamente.")
