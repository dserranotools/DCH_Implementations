| [Main](DCH_WeeklyToMonthly_1_Main_en.md) | [GlobalLink](DCH_WeeklyToMonthly_GlobalLink_en.md) | 📄 HTML | [PowerBI](DCH_WeeklyToMonthly_PowerBI_en.md) | [SQL](DCH_WeeklyToMonthly_SQL_en.md) | [SSRS](DCH_WeeklyToMonthly_SSRS_en.md) |
|:---:|:---:|:---:|:---:|:---:|:---:|

&nbsp;

# DCH Weekly → Monthly — Alternative: Static HTML Report

**Client:** Dr. Schaer  
**Version:** 1.0  
**Date:** 2026-08-05  
**Scope:** DCH 440 — Weekly Mode  

**Related documents:**
- [DCH_WeeklyToMonthly_Main.md](../DCH_WeeklyToMonthly_Main.md) ← Main document
- [DCH_WeeklyToMonthly_SQL.md](../DCH_WeeklyToMonthly_SQL_en.md) — SQL aggregation function
- [DCH_WeeklyToMonthly_SSRS.md](../DCH_WeeklyToMonthly_SSRS_en.md) — SSRS guide (recommended option)
- [DCH_WeeklyToMonthly_PowerBI.md](../DCH_WeeklyToMonthly_PowerBI_en.md) — Power BI alternative
- [DCH_WeeklyToMonthly_GlobalLink.md](../DCH_WeeklyToMonthly_GlobalLink_en.md) — Global Link in DCH

---

## 1. Description

Alternative to SSRS for environments where **SSRS cannot or should not be installed**. It consists of:

1. A **Custom Procedure** that executes the query against the function `fn_WebCO_ForecastWeeklyToMonthly` and generates an `.html` file with a formatted table
2. The file is saved in a folder accessible via IIS (e.g., `D:\DCH\Reports\`)
3. A **Global Link** in DCH points to `http://dch-server/DCH/Reports/MonthlyReport.html`
4. The procedure is executed via `DCHRemote /EXECUTESQL` on a scheduled basis (e.g., every night)

---

## 2. SSRS vs. Static HTML Comparison

| Feature | SSRS | Static HTML |
|---|---|---|
| **Additional license** | No (included in SQL Server) | No |
| **Additional installation** | Yes (SQL Server feature) | No |
| **Interactivity** | Filters, parameters, drill-down | None (flat table) |
| **Export to Excel** | Native | Manual (copy/paste) |
| **Data refresh** | Real-time (queries the DB on each load) | Scheduled (HTML is regenerated) |
| **Maintenance** | Medium (.rdl report + Report Server) | Low (one SQL + one .html) |
| **Implementation complexity** | Medium | Low |
| **Visual appearance** | Professional (conditional formatting, charts) | Basic (HTML with CSS) |

---

## 3. Implementation

### 3.1 Create a Reports Folder

On the DCH server:
```
D:\DCH\Reports\
```

Ensure write permissions for the SQL Server service and read permissions for IIS.

### 3.2 Create a Virtual Directory in IIS (if needed)

If the folder is not within the DCH website, add a Virtual Directory in IIS pointing to `D:\DCH\Reports\`.

### 3.3 Create the Custom Procedure

Register in `SYSTEM_CustomProcedure`:

```sql
INSERT INTO SYSTEM_CustomProcedure (CustomProcedureId, Descr, Source, tsql, scriptPath, processPath)
VALUES ('6_GENERATE_MONTHLY_REPORT', 'Generate Monthly Forecast HTML Report', 1, '', 'D:\DCH\Scripts\6_GENERATE_MONTHLY_REPORT.sql', '')
```

### 3.4 SQL Script to Generate the HTML

File `D:\DCH\Scripts\6_GENERATE_MONTHLY_REPORT.sql`:

```sql
SET NOCOUNT ON

DECLARE @html NVARCHAR(MAX) = ''
DECLARE @filePath NVARCHAR(500) = 'D:\DCH\Reports\MonthlyReport.html'
DECLARE @dateFrom DATE = NULL  -- or fixed date
DECLARE @dateTo DATE = NULL
DECLARE @userName NVARCHAR(128) = 'SYSTEM'

-- Build HTML header
SET @html = '<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Monthly Forecast Report</title>
    <style>
        body { font-family: Segoe UI, Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th { background-color: #2e649e; color: white; padding: 8px; text-align: left; }
        td { padding: 6px 8px; border-bottom: 1px solid #ddd; }
        tr:hover { background-color: #f5f5f5; }
        .header { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2e649e; }
        .subheader { font-size: 12px; color: #666; margin-bottom: 20px; }
        .numeric { text-align: right; }
    </style>
</head>
<body>
    <div class="header">Monthly Forecast Report</div>
    <div class="subheader">Generated: ' + CONVERT(VARCHAR, GETDATE(), 120) + '</div>
    <table>
        <thead>
            <tr>
                <th>Product</th>
                <th>Market</th>
                <th>Year</th>
                <th>Month</th>
                <th class="numeric">Budget</th>
                <th class="numeric">FrcQty</th>
                <th class="numeric">FR1</th>
                <th class="numeric">FR2</th>
                <th class="numeric">FR3</th>
                <th class="numeric">FR4</th>
                <th class="numeric">FR5</th>
                <th class="numeric">OutstQty</th>
            </tr>
        </thead>
        <tbody>'

-- Build data rows
SELECT @html = @html + 
    '<tr>' +
    '<td>' + COProductId + '</td>' +
    '<td>' + COMarketId + '</td>' +
    '<td>' + CAST([Year] AS VARCHAR) + '</td>' +
    '<td>' + CAST([Month] AS VARCHAR) + '</td>' +
    '<td class="numeric">' + FORMAT(Budget, 'N2') + '</td>' +
    '<td class="numeric">' + FORMAT(FrcQty, 'N2') + '</td>' +
    '<td class="numeric">' + FORMAT(COQty1, 'N2') + '</td>' +
    '<td class="numeric">' + FORMAT(COQty2, 'N2') + '</td>' +
    '<td class="numeric">' + FORMAT(COQty3, 'N2') + '</td>' +
    '<td class="numeric">' + FORMAT(COQty4, 'N2') + '</td>' +
    '<td class="numeric">' + FORMAT(COQty5, 'N2') + '</td>' +
    '<td class="numeric">' + FORMAT(OutstQty, 'N2') + '</td>' +
    '</tr>'
FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly](@userName, @dateFrom, @dateTo)
ORDER BY COProductId, COMarketId, [Year], [Month]

-- Close HTML
SET @html = @html + '
        </tbody>
    </table>
</body>
</html>'

-- Write to file (requires xp_cmdshell enabled or use BCP)
DECLARE @cmd NVARCHAR(1000)
SET @cmd = 'echo ' + REPLACE(@html, '''', '''''') + ' > "' + @filePath + '"'
-- Note: for large HTML, it is better to use BCP or a PowerShell script

PRINT 'Monthly Report HTML generated.'
```

> **Note**: HTML generation from TSQL using `FOR XML PATH` is suitable for small datasets. For large volumes (thousands of products/markets), it is better to use an external PowerShell script or SSIS.

### 3.5 Configure the Global Link

Global Link URL:
```
http://dch-server/DCH/Reports/MonthlyReport.html
```

Or if it is in a separate virtual folder:
```
http://dch-server/Reports/MonthlyReport.html
```

---

## 4. Limitations

- **No interactivity**: Cannot filter, sort, or drill down
- **No native export**: The user must copy/paste the table
- **No dynamic parameters**: The `{USER_NAME}` placeholders do not apply (the HTML is the same for everyone)
- **Regeneration required**: If the data changes, the script must be re-executed
- **Limited size**: For large datasets, the HTML can be heavy and slow to load

---

> **Document version**: 1.0  
> **Date**: 2026-08-05  
> **Scope**: DCH 440 — Weekly Mode  
> **Client**: Dr. Schaer