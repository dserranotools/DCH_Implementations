# DCH Weekly → Monthly — Funzione SQL e Script

**Cliente:** Dr. Schaer  
**Versione:** 1.0  
**Data:** 2026-08-05  
**Ambito:** DCH 440 — Modalità Weekly  

**Documenti correlati:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_it.md) ← Documento principale
- [DCH_WeeklyToMonthly_SSRS.md](./DCH_WeeklyToMonthly_SSRS_it.md) — Guida SSRS
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_it.md) — Alternativa Power BI
- [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_it.md) — Global Link in DCH
- [DCH_WeeklyToMonthly_HTML.md](./DCH_WeeklyToMonthly_HTML_it.md) — Alternativa HTML statico

---

## Funzione SQL: `fn_WebCO_ForecastWeeklyToMonthly`

### Descrizione

Aggrega i dati di `WebCO_ForecastWeekly` a livello mensile (`Year`, `Month`) applicando `SUM()` sulle colonne di quantità e `CASE WHEN SUM() > 0 THEN 1 ELSE 0 END` per le colonne di tipo flag (edited).

Accetta tre parametri opzionali per filtrare per utente e intervallo di date.

### Codice

```sql
-- ============================================
-- fn_WebCO_ForecastWeeklyToMonthly
-- Aggrega dati settimanali a livello mensile.
-- 
-- Parametri:
--   @USER_NAME             - Utente (informativo, incluso come colonna)
--   @DATE_FORECAST_CURRENT - Data inizio del filtro (opzionale)
--   @DATE_FORECAST_END     - Data fine del filtro (opzionale)
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
        -- Parametri come colonne
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

### Esempi di utilizzo

```sql
-- Senza filtro date (tutti i dati):
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', DEFAULT, DEFAULT);

-- Solo data di inizio:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', '2026-07-01', DEFAULT);

-- Solo data di fine:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', DEFAULT, '2026-12-31');

-- Con entrambe le date (intervallo completo):
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', '2026-07-01', '2026-12-31');

-- Usando NULL esplicitamente:
SELECT * FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('john.doe', NULL, NULL);
```

---

## Vista arricchita con descrizioni (opzionale)

Per report che richiedono nomi di prodotto/mercato invece degli ID:

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

> **Nota**: La vista utilizza valori fissi per `@USER_NAME` e `NULL` per le date (senza filtro). I parametri reali vengono applicati dal report SSRS interrogando direttamente la funzione, non dalla vista.

---

## Verifica

```sql
-- Verificare che la funzione esista
SELECT name, type_desc 
FROM sys.objects 
WHERE name = 'fn_WebCO_ForecastWeeklyToMonthly' 
  AND type IN ('IF', 'TF', 'FN')

-- Testare con dati reali (ultimi 3 mesi)
SELECT TOP 100 * 
FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly]('test_user', '2026-01-01', '2026-03-31')
ORDER BY Year, Month, COProductId

-- Contare record aggregati vs originali
SELECT 'Weekly' AS Level, COUNT(*) AS Rows FROM WebCO_ForecastWeekly
UNION ALL
SELECT 'Monthly' AS Level, COUNT(*) AS Rows FROM fn_WebCO_ForecastWeeklyToMonthly('test', NULL, NULL)
```

---

## Note sul mapping delle settimane ai mesi

`WebCO_ForecastWeekly` ha colonne `[Year]`, `[Month]`, `[Day]` che rappresentano il **primo giorno della settimana**. La funzione raggruppa per `[Year]` e `[Month]`, il che significa che:

- Una settimana che inizia il 29 gennaio e termina il 4 febbraio viene assegnata interamente al mese di **gennaio** (perché il suo `[Day]` è 29 e il suo `[Month]` è 1).
- Questo è corretto secondo la convenzione DCH, dove ogni settimana appartiene al mese della sua **data di inizio**.

Se il cliente richiede una logica diversa (es.: assegnare la settimana al mese in cui cade la maggior parte dei giorni), è necessario modificare la funzione.

---

> **Documento versione**: 1.0  
> **Data**: 2026-08-05  
> **Ambito**: DCH 440 — Modalità Weekly  
> **Cliente**: Dr. Schaer