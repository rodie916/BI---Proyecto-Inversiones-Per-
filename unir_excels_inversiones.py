import pandas as pd
import os


ARCHIVOS = [
    r"C:\Users\TuUsuario\Desktop\Inversiones\Amazonas_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Ancash_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Apurimac_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Arequipa_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Ayacucho_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Cajamarca_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Cusco_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\HuancavelicaFiltrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Huanucp_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Ica_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Junin_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\LaLibertad_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Lambayeque_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Lima_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Loreto_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Madre_de_Dios_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Moquegua_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Pasco_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Puno_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\SanMartin_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Tacna_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Tumbes_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Ucayali_Filtrado.xlsx",
    r"C:\Users\TuUsuario\Desktop\Inversiones\Callao_Filtrado.xlsx",
]


ARCHIVO_SALIDA = r"C:\Users\TuUsuario\Desktop\Inversiones\Inversiones_Peru_Consolidado.xlsx"

dataframes = []
total_filas = 0

for ruta in ARCHIVOS:
    nombre = os.path.basename(ruta)
    try:
        df = pd.read_excel(ruta)
        dataframes.append(df)
        total_filas += len(df)
        print(f"OK  {nombre}  ({len(df):,} filas)")
    except FileNotFoundError:
        print(f"ADVERTENCIA: No se encontró el archivo: {ruta}")
    except Exception as e:
        print(f"ERROR en {nombre}: {e}")

if not dataframes:
    print("\nNo se cargó ningún archivo. Verifica las rutas.")
else:
    consolidado = pd.concat(dataframes, ignore_index=True)
    consolidado.to_excel(ARCHIVO_SALIDA, index=False)
    print(f"\nArchivo guardado en: {ARCHIVO_SALIDA}")
    print(f"Total de filas consolidadas: {total_filas:,}")
    print(f"Columnas: {list(consolidado.columns)}")
