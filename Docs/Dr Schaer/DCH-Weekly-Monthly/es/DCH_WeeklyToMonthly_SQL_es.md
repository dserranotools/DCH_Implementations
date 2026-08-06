# DCH Weekly → Monthly — Function SQL y Scripts

**Cliente:** Dr. Schaer  
**Versión:** 1.0  
**Fecha:** 2026-08-05  
**Ámbito:** DCH 440 — Modo Weekly  

**Documentos relacionados:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_es.md) ← Documento principal
- [DCH_WeeklyToMonthly_SSRS.md](./DCH_WeeklyToMonthly_SSRS_es.md) — Guía SSRS
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_es.md) — Alternativa Power BI
- [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_es.md) — Global Link en DCH
- [DCH_WeeklyToMonthly_HTML.md](./DCH_WeeklyToMonthly_HTML_es.md) — Alternativa HTML estático

---

## Function SQL: `fn_WebCO_ForecastWeeklyToMonthly`

### Descripción

Agrega los datos de `WebCO_ForecastWeekly` a nivel mensual (`Year`, `Month`) aplicando `SUM()` sobre las columnas de cantidad y `CASE WHEN SUM() > 0 THEN 1 ELSE 0 END` para las columnas de tipo flag (edited).

Acepta tres parámetros opcionales para filtrar por usuario y rango de fechas.

### Código

```sql
-- ============================================
-- fn_WebCO_ForecastWeeklyToMonthly
-- Agrega datos semanales a nivel mensual.
-- 
-- Parámetros:
--   @USER_NAME             - Usuario (informativo, se incluye como columna)
--   @DATE_FORECAST_CURRENT - Fecha inicio del filtro (opcional)
--   @DATE_FORECAST_END     - Fecha fin del filtro (opcional)
-- ============================================

CREATE FUNCTION [dbo].[fn_WebCO_ForecastWeeklyToMonthly]
(
    @USER_NAME NVARCHAR(128),
    @DATE_FORECAST_CURRENT DATE = NULL,
    @DATE_FORECAST_END DATE = NULL
)
RETURNS TABLE
AS
RETURN
(
    SELECT
        COProductId,
        COMarketId,
        [Year],
        [Month],
        -- Parámetros como columnas
        @USER_NAME AS UserName,
        @DATE_FORECAST_CURRENT AS DateForecastCurrent,
        @DATE_FORECAST_END AS DateForecastEnd,
        -- Aggregate Budget
        SUM(Budget) AS Budget,
        -- Aggregate Forecast quantities
        SUM(FrcQty) AS FrcQty,
        SUM(FrcLOS) AS FrcLOS,
        -- Aggregate COSO99
        SUM(COSO99) AS COSO99,
        -- Aggregate Outstanding quantities
        SUM(OutstQty) AS OutstQty,
        SUM(OutstLOS) AS OutstLOS,
        -- Aggregate CO quantities (1-5)
        SUM(COQty1) AS COQty1,
        SUM(COQty2) AS COQty2,
        SUM(COQty3) AS COQty3,
        SUM(COQty4) AS COQty4,
        SUM(COQty5) AS COQty5,
        -- COEdited: If any row in the group has flag = 1, then the group is 1 (true)
        CASE WHEN SUM(COEdited1) > 0 THEN 1 ELSE 0 END AS COEdited1,
        CASE WHEN SUM(COEdited2) > 0 THEN 1 ELSE 0 END AS COEdited2,
        CASE WHEN SUM(COEdited3) > 0 THEN 1 ELSE 0 END AS COEdited3,
        CASE WHEN SUM(COEdited4) > 0 THEN 1 ELSE 0 END AS COEdited4,
        CASE WHEN SUM(COEdited5) > 0 THEN 1 ELSE 0 END AS COEdited5,
        -- Aggregate Visibility quantities (1-8)
        SUM(VisQty1) AS VisQty1,
        SUM(VisQty2) AS VisQty2,
        SUM(VisQty3) AS VisQty3,
        SUM(VisQty4) AS VisQty4,
        SUM(VisQty5) AS VisQty5,
        SUM(VisQty6) AS VisQty6,
        SUM(VisQty7) AS VisQty7,
        SUM(VisQty8) AS VisQty8,
        -- Row count (number of weeks with data per product/market/month)
        COUNT(*) AS WeekCount
    FROM [dbo].[WebCO_ForecastWeekly]
    WHERE
        (@DATE_FORECAST_CURRENT IS NULL 
         OR DATEFROMPARTS([Year], [Month], [Day]) >= @DATE_FORECAST_CURRENT)
        AND
        (@DATE_FORECAST_END IS NULL 
         OR DATEFROMPARTS([Year], [Month], [Day]) <= @DATE_FORECAST_END)
    GROUP BY
        COProductId,
        COMarketId,
        [Year],
        [Month]
);
```

### Ejemplos de uso

```sql
-- Sin filtro de fechas (todos los datos):
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', DEFAULT, DEFAULT);

-- Solo fecha de inicio:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', '2026-07-01', DEFAULT);

-- Solo fecha de fin:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', DEFAULT, '2026-12-31');

-- Con ambas fechas (rango completo):
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', '2026-07-01', '2026-12-31');

-- Usando NULL explícitamente:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', NULL, NULL);
```

---

## Vista enriquecida con descripciones (opcional)

Para informes que requieran nombres de producto/mercado en lugar de IDs:

```sql
CREATE VIEW [dbo].[vw_ForecastMonthlyEnriched]
AS
SELECT
    f.COMarketId,
    m.MarketDescr,
    f.COProductId,
    p.ProductDescr,
    f.Year,
    f.Month,
    f.UserName,
    f.DateForecastCurrent,
    f.DateForecastEnd,
    f.Budget,
    f.FrcQty,
    f.FrcLOS,
    f.COSO99,
    f.OutstQty,
    f.OutstLOS,
    f.COQty1, f.COQty2, f.COQty3, f.COQty4, f.COQty5,
    f.COEdited1, f.COEdited2, f.COEdited3, f.COEdited4, f.COEdited5,
    f.VisQty1, f.VisQty2, f.VisQty3, f.VisQty4,
    f.VisQty5, f.VisQty6, f.VisQty7, f.VisQty8,
    f.WeekCount
FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('SSRS_REPORT', NULL, NULL) f
LEFT JOIN [dbo].[MasterData_COMarket] m ON f.COMarketId = m.COMarketId
LEFT JOIN [dbo].[MasterData_COProduct] p ON f.COProductId = p.COProductId;
```

> **Nota**: La vista usa valores fijos para `@USER_NAME` y `NULL` para fechas (sin filtro). Los parámetros reales se aplican desde el informe SSRS al consultar la function directamente, no desde la vista.

---

## Verificación

```sql
-- Verificar que la function existe
SELECT name, type_desc 
FROM sys.objects 
WHERE name = 'fn_WebCO_ForecastWeeklyToMonthly' 
  AND type IN ('IF', 'TF', 'FN')

-- Probar con datos reales (últimos 3 meses)
SELECT TOP 100 * 
FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('test_user', '2026-01-01', '2026-03-31')
ORDER BY Year, Month, COProductId

-- Contar registros agregados vs originales
SELECT 'Weekly' AS Level, COUNT(*) AS Rows FROM WebCO_ForecastWeekly
UNION ALL
SELECT 'Monthly' AS Level, COUNT(*) AS Rows FROM fn_WebCO_ForecastWeeklyToMonthly('test', NULL, NULL)
```

---

## Notas sobre el mapeo de semanas a meses

`WebCO_ForecastWeekly` tiene columnas `[Year]`, `[Month]`, `[Day]` que representan el **primer día de la semana**. La function agrupa por `[Year]` y `[Month]`, lo que significa que:

- Una semana que empieza el 29 de enero y termina el 4 de febrero se asigna completamente al mes **enero** (porque su `[Day]` es 29 y su `[Month]` es 1).
- Esto es correcto según la convención de DCH, donde cada semana pertenece al mes de su **fecha de inicio**.

Si el cliente requiere una lógica diferente (ej: asignar la semana al mes donde caen la mayoría de los días), debe ajustarse la function.

---

> **Documento versión**: 1.0  
> **Fecha**: 2026-08-05  
> **Ámbito**: DCH 440 — Modo Weekly  
> **Cliente**: Dr. Schaer