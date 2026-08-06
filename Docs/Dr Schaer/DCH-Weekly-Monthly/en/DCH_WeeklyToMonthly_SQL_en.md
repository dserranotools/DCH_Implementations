| [Main](DCH_WeeklyToMonthly_1_Main_en.md) | [GlobalLink](DCH_WeeklyToMonthly_GlobalLink_en.md) | [HTML](DCH_WeeklyToMonthly_HTML_en.md) | [PowerBI](DCH_WeeklyToMonthly_PowerBI_en.md) | 📄 SQL | [SSRS](DCH_WeeklyToMonthly_SSRS_en.md) |
|:---:|:---:|:---:|:---:|:---:|:---:|

&nbsp;

# DCH Weekly → Monthly — SQL Function and Scripts

**Client:** Dr. Schaer  
**Version:** 1.0  
**Date:** 2026-08-05  
**Scope:** DCH 440 — Weekly Mode  

**Related documents:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_en.md) ← Main document
- [DCH_WeeklyToMonthly_SSRS.md](./DCH_WeeklyToMonthly_SSRS_en.md) — SSRS Guide
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_en.md) — Power BI Alternative
- [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_en.md) — Global Link in DCH
- [DCH_WeeklyToMonthly_HTML.md](./DCH_WeeklyToMonthly_HTML_en.md) — Static HTML Alternative

---

## SQL Function: `fn_WebCO_ForecastWeeklyToMonthly`

### Description

Aggregates data from `WebCO_ForecastWeekly` at the monthly level (`Year`, `Month`) by applying `SUM()` over quantity columns and `CASE WHEN SUM() > 0 THEN 1 ELSE 0 END` for flag-type (edited) columns.

Accepts three optional parameters to filter by user and date range.

### Code

```sql
-- ============================================
-- fn_WebCO_ForecastWeeklyToMonthly
-- Aggregates weekly data at the monthly level.
-- 
-- Parameters:
--   @USER_NAME             - User (informational, included as a column)
--   @DATE_FORECAST_CURRENT - Start date of the filter (optional)
--   @DATE_FORECAST_END     - End date of the filter (optional)
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
        -- Parameters as columns
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

### Usage examples

```sql
-- Without date filter (all data):
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', DEFAULT, DEFAULT);

-- Start date only:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', '2026-07-01', DEFAULT);

-- End date only:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', DEFAULT, '2026-12-31');

-- With both dates (full range):
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', '2026-07-01', '2026-12-31');

-- Using NULL explicitly:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', NULL, NULL);
```

---

## Enriched view with descriptions (optional)

For reports that require product/market names instead of IDs:

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

> **Note**: The view uses fixed values for `@USER_NAME` and `NULL` for dates (no filter). Actual parameters are applied from the SSRS report when querying the function directly, not from the view.

---

## Verification

```sql
-- Verify that the function exists
SELECT name, type_desc 
FROM sys.objects 
WHERE name = 'fn_WebCO_ForecastWeeklyToMonthly' 
  AND type IN ('IF', 'TF', 'FN')

-- Test with real data (last 3 months)
SELECT TOP 100 * 
FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('test_user', '2026-01-01', '2026-03-31')
ORDER BY Year, Month, COProductId

-- Compare aggregated vs original row counts
SELECT 'Weekly' AS Level, COUNT(*) AS Rows FROM WebCO_ForecastWeekly
UNION ALL
SELECT 'Monthly' AS Level, COUNT(*) AS Rows FROM fn_WebCO_ForecastWeeklyToMonthly('test', NULL, NULL)
```

---

## Notes on week-to-month mapping

`WebCO_ForecastWeekly` has columns `[Year]`, `[Month]`, `[Day]` that represent the **first day of the week**. The function groups by `[Year]` and `[Month]`, which means:

- A week starting on January 29 and ending on February 4 is assigned entirely to the month of **January** (because its `[Day]` is 29 and its `[Month]` is 1).
- This is correct according to the DCH convention, where each week belongs to the month of its **start date**.

If the client requires a different logic (e.g., assign the week to the month where most days fall), the function should be adjusted.

---

> **Document version**: 1.0  
> **Date**: 2026-08-05  
> **Scope**: DCH 440 — Weekly Mode  
> **Client**: Dr. Schaer