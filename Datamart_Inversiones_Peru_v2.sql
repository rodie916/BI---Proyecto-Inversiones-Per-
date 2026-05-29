-- ============================================================
-- DATAMART: Inversiones Públicas del Perú — v2
-- 8 dimensiones + 1 fact table
-- ============================================================

-- ── RESET ──────────────────────────────────────────────────
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'Datamart_Inversiones_Peru')
BEGIN
    ALTER DATABASE Datamart_Inversiones_Peru SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE Datamart_Inversiones_Peru;
END
GO
CREATE DATABASE Datamart_Inversiones_Peru;
GO
USE Datamart_Inversiones_Peru;
GO

-- ── 1. DIM_TIEMPO (calendario 2000–2030) ───────────────────
CREATE TABLE Dim_Tiempo (
    id_tiempo     INT PRIMARY KEY,
    fecha         DATE NOT NULL,
    anio          INT  NOT NULL,
    trimestre     INT  NOT NULL,
    mes           INT  NOT NULL,
    nombre_mes    VARCHAR(20) NOT NULL,
    semana        INT  NOT NULL,
    dia           INT  NOT NULL,
    nombre_dia    VARCHAR(20) NOT NULL,
    es_fin_semana BIT  NOT NULL
);
GO
DECLARE @f DATE = '2000-01-01', @fin DATE = '2030-12-31';
WHILE @f <= @fin
BEGIN
    INSERT INTO Dim_Tiempo VALUES (
        CONVERT(INT, FORMAT(@f,'yyyyMMdd')), @f,
        YEAR(@f), DATEPART(QUARTER,@f), MONTH(@f),
        DATENAME(MONTH,@f), DATEPART(WEEK,@f), DAY(@f),
        DATENAME(WEEKDAY,@f),
        CASE WHEN DATEPART(WEEKDAY,@f) IN (1,7) THEN 1 ELSE 0 END
    );
    SET @f = DATEADD(DAY,1,@f);
END
GO

-- ── 2. DIM_UBICACION ───────────────────────────────────────
CREATE TABLE Dim_Ubicacion (
    id_ubicacion  INT IDENTITY(1,1) PRIMARY KEY,
    ubigeo        VARCHAR(10)  NOT NULL,
    departamento  VARCHAR(100) NOT NULL,
    provincia     VARCHAR(100) NOT NULL,
    distrito      VARCHAR(100) NOT NULL
);
GO

-- ── 3. DIM_SECTOR ──────────────────────────────────────────
CREATE TABLE Dim_Sector (
    id_sector    INT IDENTITY(1,1) PRIMARY KEY,
    nombre_sector VARCHAR(100) NOT NULL
);
GO

-- ── 4. DIM_ENTIDAD ─────────────────────────────────────────
CREATE TABLE Dim_Entidad (
    id_entidad        INT IDENTITY(1,1) PRIMARY KEY,
    nombre_entidad    VARCHAR(300) NOT NULL,
    nombre_ejecutora  VARCHAR(300) NOT NULL
);
GO

-- ── 5. DIM_ESTADO ──────────────────────────────────────────
CREATE TABLE Dim_Estado (
    id_estado INT IDENTITY(1,1) PRIMARY KEY,
    estado    VARCHAR(20) NOT NULL
);
GO
INSERT INTO Dim_Estado VALUES ('ACTIVO'), ('CERRADO');
GO

-- ── 6. DIM_NIVEL_GOBIERNO (NUEVA) ──────────────────────────
CREATE TABLE Dim_NivelGobierno (
    id_nivel_gobierno INT IDENTITY(1,1) PRIMARY KEY,
    nivel_gobierno    VARCHAR(50) NOT NULL
);
GO
INSERT INTO Dim_NivelGobierno VALUES
    ('GOBIERNO NACIONAL'),
    ('GOBIERNO REGIONAL'),
    ('GOBIERNO LOCAL'),
    ('OTROS');
GO

-- ── 7. DIM_TIPO_INTERVENCION (NUEVA) ───────────────────────
CREATE TABLE Dim_TipoIntervencion (
    id_tipo_intervencion INT IDENTITY(1,1) PRIMARY KEY,
    tipo_intervencion    VARCHAR(50) NOT NULL
);
GO
INSERT INTO Dim_TipoIntervencion VALUES
    ('MEJORAMIENTO'), ('CREACION'), ('CONSTRUCCION'),
    ('INSTALACION'), ('ADQUISICION'), ('AMPLIACION'),
    ('FORTALECIMIENTO'), ('REHABILITACION'), ('RECUPERACION'),
    ('MANTENIMIENTO'), ('EQUIPAMIENTO'), ('IMPLEMENTACION'),
    ('ESTUDIOS'), ('PROGRAMA'), ('PROYECTO'), ('OTROS');
GO

-- ── 8. DIM_RANGO_MONTO (NUEVA) ─────────────────────────────
CREATE TABLE Dim_RangoMonto (
    id_rango_monto INT IDENTITY(1,1) PRIMARY KEY,
    rango_monto    VARCHAR(30) NOT NULL,
    monto_min      DECIMAL(20,2) NOT NULL,
    monto_max      DECIMAL(20,2) NOT NULL
);
GO
INSERT INTO Dim_RangoMonto VALUES
    ('PEQUEÑO (< 1M)',       0,          999999.99),
    ('MEDIANO (1M - 10M)',   1000000,    9999999.99),
    ('GRANDE (10M - 100M)',  10000000,   99999999.99),
    ('MUY GRANDE (> 100M)',  100000000,  99999999999.99);
GO

-- ── FACT_INVERSIONES ───────────────────────────────────────
CREATE TABLE Fact_Inversiones (
    id_hecho                  INT IDENTITY(1,1) PRIMARY KEY,
    codigo_inversion          BIGINT         NOT NULL,
    nombre_inversion          NVARCHAR(500)  NOT NULL,
    id_tiempo_registro        INT            NOT NULL,
    id_tiempo_viabilidad      INT            NULL,
    id_ubicacion              INT            NOT NULL,
    id_sector                 INT            NOT NULL,
    id_entidad                INT            NOT NULL,
    id_estado                 INT            NOT NULL,
    id_nivel_gobierno         INT            NOT NULL,
    id_tipo_intervencion      INT            NOT NULL,
    id_rango_monto            INT            NOT NULL,
    monto_viable              DECIMAL(20,2)  NOT NULL DEFAULT 0,
    costo_actualizado         DECIMAL(20,2)  NOT NULL DEFAULT 0,
    beneficiarios             INT            NULL,
    variacion_costo AS (costo_actualizado - monto_viable),

    CONSTRAINT FK_Fact_TR   FOREIGN KEY (id_tiempo_registro)   REFERENCES Dim_Tiempo(id_tiempo),
    CONSTRAINT FK_Fact_TV   FOREIGN KEY (id_tiempo_viabilidad) REFERENCES Dim_Tiempo(id_tiempo),
    CONSTRAINT FK_Fact_Ub   FOREIGN KEY (id_ubicacion)         REFERENCES Dim_Ubicacion(id_ubicacion),
    CONSTRAINT FK_Fact_Sec  FOREIGN KEY (id_sector)            REFERENCES Dim_Sector(id_sector),
    CONSTRAINT FK_Fact_Ent  FOREIGN KEY (id_entidad)           REFERENCES Dim_Entidad(id_entidad),
    CONSTRAINT FK_Fact_Est  FOREIGN KEY (id_estado)            REFERENCES Dim_Estado(id_estado),
    CONSTRAINT FK_Fact_Niv  FOREIGN KEY (id_nivel_gobierno)    REFERENCES Dim_NivelGobierno(id_nivel_gobierno),
    CONSTRAINT FK_Fact_Tip  FOREIGN KEY (id_tipo_intervencion) REFERENCES Dim_TipoIntervencion(id_tipo_intervencion),
    CONSTRAINT FK_Fact_Ran  FOREIGN KEY (id_rango_monto)       REFERENCES Dim_RangoMonto(id_rango_monto)
);
GO

-- ── ÍNDICES ────────────────────────────────────────────────
CREATE INDEX IX_TR  ON Fact_Inversiones(id_tiempo_registro);
CREATE INDEX IX_TV  ON Fact_Inversiones(id_tiempo_viabilidad);
CREATE INDEX IX_Ub  ON Fact_Inversiones(id_ubicacion);
CREATE INDEX IX_Sec ON Fact_Inversiones(id_sector);
CREATE INDEX IX_Ent ON Fact_Inversiones(id_entidad);
CREATE INDEX IX_Niv ON Fact_Inversiones(id_nivel_gobierno);
CREATE INDEX IX_Tip ON Fact_Inversiones(id_tipo_intervencion);
GO

-- ── LOG DE AUDITORÍA ───────────────────────────────────────
CREATE TABLE Log_Fact_Inversiones (
    id_log           INT IDENTITY(1,1) PRIMARY KEY,
    accion           VARCHAR(10)  NOT NULL,
    id_hecho         INT          NOT NULL,
    codigo_inversion BIGINT       NOT NULL,
    fecha_accion     DATETIME     NOT NULL DEFAULT GETDATE(),
    usuario          VARCHAR(100) NOT NULL DEFAULT SYSTEM_USER
);
GO
CREATE TRIGGER trg_Auditoria_Fact
ON Fact_Inversiones AFTER INSERT, DELETE AS
BEGIN
    INSERT INTO Log_Fact_Inversiones(accion,id_hecho,codigo_inversion)
    SELECT 'INSERT', id_hecho, codigo_inversion FROM inserted;
    INSERT INTO Log_Fact_Inversiones(accion,id_hecho,codigo_inversion)
    SELECT 'DELETE', id_hecho, codigo_inversion FROM deleted;
END
GO

-- ── STORED PROCEDURES ──────────────────────────────────────
CREATE PROCEDURE sp_InversionPorDepartamentoAnio
    @anio_inicio INT = 2000, @anio_fin INT = 2030
AS
BEGIN
    SELECT u.departamento, t.anio,
        COUNT(*) AS total_proyectos,
        SUM(f.monto_viable) AS total_monto_viable,
        SUM(f.variacion_costo) AS total_desvio,
        SUM(ISNULL(f.beneficiarios,0)) AS total_beneficiarios
    FROM Fact_Inversiones f
    JOIN Dim_Ubicacion u ON f.id_ubicacion = u.id_ubicacion
    JOIN Dim_Tiempo    t ON f.id_tiempo_registro = t.id_tiempo
    WHERE t.anio BETWEEN @anio_inicio AND @anio_fin
    GROUP BY u.departamento, t.anio
    ORDER BY u.departamento, t.anio;
END
GO

CREATE PROCEDURE sp_CentralizacionLimaVsRegiones
    @sector VARCHAR(100) = NULL, @anio INT = NULL
AS
BEGIN
    SELECT
        CASE WHEN u.departamento='LIMA' THEN 'LIMA' ELSE 'RESTO DEL PAÍS' END AS zona,
        s.nombre_sector, t.anio,
        COUNT(*) AS total_proyectos,
        SUM(f.monto_viable) AS total_monto_viable,
        ROUND(COUNT(*)*100.0 / SUM(COUNT(*)) OVER (PARTITION BY t.anio,s.nombre_sector),2) AS pct_proyectos
    FROM Fact_Inversiones f
    JOIN Dim_Ubicacion u ON f.id_ubicacion = u.id_ubicacion
    JOIN Dim_Sector    s ON f.id_sector    = s.id_sector
    JOIN Dim_Tiempo    t ON f.id_tiempo_registro = t.id_tiempo
    WHERE (@sector IS NULL OR s.nombre_sector=@sector)
      AND (@anio   IS NULL OR t.anio=@anio)
    GROUP BY CASE WHEN u.departamento='LIMA' THEN 'LIMA' ELSE 'RESTO DEL PAÍS' END,
             s.nombre_sector, t.anio
    ORDER BY t.anio, s.nombre_sector, zona;
END
GO

-- ── VERIFICACIÓN ───────────────────────────────────────────
SELECT tabla, filas FROM (
    SELECT 'Dim_Tiempo'           AS tabla, COUNT(*) AS filas FROM Dim_Tiempo           UNION ALL
    SELECT 'Dim_Ubicacion',               COUNT(*) FROM Dim_Ubicacion                  UNION ALL
    SELECT 'Dim_Sector',                  COUNT(*) FROM Dim_Sector                     UNION ALL
    SELECT 'Dim_Entidad',                 COUNT(*) FROM Dim_Entidad                    UNION ALL
    SELECT 'Dim_Estado',                  COUNT(*) FROM Dim_Estado                     UNION ALL
    SELECT 'Dim_NivelGobierno',           COUNT(*) FROM Dim_NivelGobierno              UNION ALL
    SELECT 'Dim_TipoIntervencion',        COUNT(*) FROM Dim_TipoIntervencion           UNION ALL
    SELECT 'Dim_RangoMonto',              COUNT(*) FROM Dim_RangoMonto                 UNION ALL
    SELECT 'Fact_Inversiones',            COUNT(*) FROM Fact_Inversiones
) x ORDER BY tabla;
GO
