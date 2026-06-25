import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

DB_PATH = "datamart_inversiones.db"


# ----------------------------------------------------------------------- Conexión y carga
def get_datamart_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"✓ Conexión al Data Mart exitosa ({DB_PATH})")
        return conn
    except sqlite3.Error as e:
        print(f"Error de conexión: {e}")
        return None


def load_data():
    conn = get_datamart_connection()
    if conn is None:
        raise RuntimeError("No se pudo conectar al Data Mart (datamart_inversiones.db).")

    query = """
        SELECT
            f.codigo_inversion,
            f.monto_viable,
            f.costo_actualizado,
            f.beneficiarios,
            f.variacion_costo,
            s.nombre_sector   AS sector,
            en.nombre_entidad AS entidad,
            es.estado,
            ng.nivel_gobierno,
            ti.tipo_intervencion,
            u.departamento,
            t.fecha AS fecha_registro,
            t.anio,
            t.mes,
            t.nombre_mes
        FROM Fact_Inversiones f
        JOIN Dim_Sector s            ON f.id_sector = s.id_sector
        JOIN Dim_Entidad en          ON f.id_entidad = en.id_entidad
        JOIN Dim_Estado es           ON f.id_estado = es.id_estado
        JOIN Dim_NivelGobierno ng    ON f.id_nivel_gobierno = ng.id_nivel_gobierno
        JOIN Dim_TipoIntervencion ti ON f.id_tipo_intervencion = ti.id_tipo_intervencion
        JOIN Dim_Ubicacion u         ON f.id_ubicacion = u.id_ubicacion
        JOIN Dim_Tiempo t            ON f.id_tiempo_registro = t.id_tiempo
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])
    print(f"✓ {len(df):,} inversiones cargadas")
    return df


df_inv = load_data()

# Opciones de filtros (se calculan una vez, en memoria)
opciones_sector = sorted(df_inv['sector'].unique())
opciones_nivel = sorted(df_inv['nivel_gobierno'].unique())
opciones_estado = sorted(df_inv['estado'].unique())
opciones_entidad = sorted(df_inv['entidad'].unique())
fecha_min = df_inv['fecha_registro'].min()
fecha_max = df_inv['fecha_registro'].max()


# ----------------------------------------------------------------------- App
app = dash.Dash(__name__)
app.title = "Dashboard Inversiones Públicas Perú"

app.layout = html.Div([
    html.H1("Dashboard de Inversiones Públicas - Perú",
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '5px'}),
    html.P("Análisis del Banco de Inversiones (Invierte.pe)",
            style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '20px'}),

    # ---------------------------------------------------------------- Filtros
    html.Div([
        html.Div([
            html.Label("Sector", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='sector-filter', options=[{'label': s, 'value': s} for s in opciones_sector],
                         multi=True, placeholder="Buscar sector...")
        ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),

        html.Div([
            html.Label("Nivel de Gobierno", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='nivel-filter', options=[{'label': n, 'value': n} for n in opciones_nivel],
                         multi=True, placeholder="Buscar nivel...")
        ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),

        html.Div([
            html.Label("Estado", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='estado-filter', options=[{'label': e, 'value': e} for e in opciones_estado],
                         multi=True, placeholder="Buscar estado...")
        ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),

        html.Div([
            html.Label("Entidad", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='entidad-filter', options=[{'label': e, 'value': e} for e in opciones_entidad],
                         multi=True, placeholder="Buscar entre 2,012 entidades...")
        ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),

        html.Div([
            html.Label("Rango de fechas (registro)", style={'fontWeight': 'bold'}),
            dcc.DatePickerRange(id='date-range', min_date_allowed=fecha_min, max_date_allowed=fecha_max,
                                 start_date=fecha_min, end_date=fecha_max, display_format='DD/MM/YYYY')
        ], style={'width': '19%', 'display': 'inline-block'})
    ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '20px'}),

    # ---------------------------------------------------------------- KPIs
    html.Div(id='kpi-cards', style={'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)',
                                     'gap': '15px', 'marginBottom': '20px'}),

    # ---------------------------------------------------------------- Fila 1: Nivel Gobierno + Sectores
    html.Div([
        html.Div([dcc.Graph(id='nivel-chart')], style={'width': '38%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='sector-chart')], style={'width': '60%', 'float': 'right', 'display': 'inline-block'})
    ]),

    # ---------------------------------------------------------------- Fila 2: Evolución
    html.Div([dcc.Graph(id='evolucion-chart')], style={'marginTop': '20px'}),

    # ---------------------------------------------------------------- Fila 3: Tipo Intervención + Departamentos
    html.Div([
        html.Div([dcc.Graph(id='tipo-chart')], style={'width': '49%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='departamento-chart')], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={'marginTop': '20px'})
])


# ----------------------------------------------------------------------- Callback
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('nivel-chart', 'figure'),
     Output('sector-chart', 'figure'),
     Output('evolucion-chart', 'figure'),
     Output('tipo-chart', 'figure'),
     Output('departamento-chart', 'figure')],
    [Input('sector-filter', 'value'),
     Input('nivel-filter', 'value'),
     Input('estado-filter', 'value'),
     Input('entidad-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_dashboard(sectores, niveles, estados, entidades, start_date, end_date):
    dff = df_inv.copy()

    if sectores:
        dff = dff[dff['sector'].isin(sectores)]
    if niveles:
        dff = dff[dff['nivel_gobierno'].isin(niveles)]
    if estados:
        dff = dff[dff['estado'].isin(estados)]
    if entidades:
        dff = dff[dff['entidad'].isin(entidades)]
    if start_date and end_date:
        dff = dff[(dff['fecha_registro'] >= pd.to_datetime(start_date)) &
                  (dff['fecha_registro'] <= pd.to_datetime(end_date))]

    # ---------- KPIs
    def kpi(valor, etiqueta, color):
        return html.Div([
            html.H3(valor, style={'color': color, 'margin': '0'}),
            html.P(etiqueta, style={'color': '#7f8c8d', 'margin': '0'})
        ], style={'textAlign': 'center', 'padding': '18px', 'backgroundColor': 'white',
                   'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})

    monto_viable_total = dff['monto_viable'].sum()
    costo_actual_total = dff['costo_actualizado'].sum()
    variacion_pct = ((costo_actual_total - monto_viable_total) / monto_viable_total * 100
                      if monto_viable_total > 0 else 0)

    kpis = [
        kpi(f"{len(dff):,}", "Total Inversiones", '#3498db'),
        kpi(f"S/ {monto_viable_total/1e6:,.1f}M", "Monto Viable Total", '#27ae60'),
        kpi(f"S/ {costo_actual_total/1e6:,.1f}M", "Costo Actualizado Total", '#e74c3c'),
        kpi(f"{dff['beneficiarios'].sum():,.0f}", "Beneficiarios Totales", '#9b59b6'),
        kpi(f"{variacion_pct:+.1f}%", "Variación de Costo Promedio", '#f39c12'),
    ]

    # ---------- 1. Nivel de Gobierno (donut)
    nivel_data = dff.groupby('nivel_gobierno')['monto_viable'].sum().reset_index()
    fig_nivel = px.pie(nivel_data, values='monto_viable', names='nivel_gobierno', hole=0.45,
                        title='Inversión por Nivel de Gobierno',
                        color_discrete_sequence=px.colors.qualitative.Set2)
    fig_nivel.update_traces(textposition='inside', textinfo='percent+label')

    # ---------- 2. Top 10 Sectores (barras horizontales)
    sector_data = dff.groupby('sector')['monto_viable'].sum().reset_index().nlargest(10, 'monto_viable')
    fig_sector = px.bar(sector_data, x='monto_viable', y='sector', orientation='h',
                         title='Top 10 Sectores por Monto Viable',
                         color='monto_viable', color_continuous_scale='Blues',
                         labels={'monto_viable': 'Monto Viable (S/)', 'sector': ''})
    fig_sector.update_layout(yaxis={'categoryorder': 'total ascending'})

    # ---------- 3. Evolución anual: Monto Viable vs Costo Actualizado
    anual = dff.groupby('anio').agg(monto_viable=('monto_viable', 'sum'),
                                     costo_actualizado=('costo_actualizado', 'sum')).reset_index().sort_values('anio')
    fig_evolucion = go.Figure()
    fig_evolucion.add_trace(go.Scatter(x=anual['anio'], y=anual['monto_viable'],
                                        name='Monto Viable', mode='lines+markers',
                                        line=dict(color='#27ae60', width=3)))
    fig_evolucion.add_trace(go.Scatter(x=anual['anio'], y=anual['costo_actualizado'],
                                        name='Costo Actualizado', mode='lines+markers',
                                        line=dict(color='#e74c3c', width=3)))
    fig_evolucion.update_layout(title='Evolución Anual: Monto Viable vs Costo Actualizado (S/)',
                                 xaxis_title='Año', yaxis_title='Monto (S/)')

    # ---------- 4. Top 10 Tipos de Intervención (cantidad de proyectos)
    tipo_data = dff['tipo_intervencion'].value_counts().nlargest(10).reset_index()
    tipo_data.columns = ['tipo_intervencion', 'cantidad']
    fig_tipo = px.bar(tipo_data, x='cantidad', y='tipo_intervencion', orientation='h',
                       title='Top 10 Tipos de Intervención (Nº de proyectos)',
                       color='cantidad', color_continuous_scale='Oranges',
                       labels={'cantidad': 'Proyectos', 'tipo_intervencion': ''})
    fig_tipo.update_layout(yaxis={'categoryorder': 'total ascending'})

    # ---------- 5. Top 10 Departamentos por Beneficiarios
    depto_data = dff.groupby('departamento')['beneficiarios'].sum().reset_index().nlargest(10, 'beneficiarios')
    fig_depto = px.bar(depto_data, x='beneficiarios', y='departamento', orientation='h',
                        title='Top 10 Departamentos por Beneficiarios',
                        color='beneficiarios', color_continuous_scale='Purples',
                        labels={'beneficiarios': 'Beneficiarios', 'departamento': ''})
    fig_depto.update_layout(yaxis={'categoryorder': 'total ascending'})

    return kpis, fig_nivel, fig_sector, fig_evolucion, fig_tipo, fig_depto


if __name__ == '__main__':
    print("Iniciando servidor Dash...")
    print("Accede al dashboard en: http://localhost:8050")
    app.run(debug=True, port=8050)
