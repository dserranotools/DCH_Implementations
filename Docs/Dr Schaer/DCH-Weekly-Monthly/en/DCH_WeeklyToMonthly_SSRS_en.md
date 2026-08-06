| [Main](DCH_WeeklyToMonthly_1_Main_en.md) | [GlobalLink](DCH_WeeklyToMonthly_GlobalLink_en.md) | [HTML](DCH_WeeklyToMonthly_HTML_en.md) | [PowerBI](DCH_WeeklyToMonthly_PowerBI_en.md) | [SQL](DCH_WeeklyToMonthly_SQL_en.md) | 📄 SSRS |
|:---:|:---:|:---:|:---:|:---:|:---:|

&nbsp;

# DCH Weekly → Monthly — SSRS Guide

**Client:** Dr. Schaer  
**Version:** 1.0  
**Date:** 2026-08-05  
**Scope:** DCH 440 — Weekly Mode  

**Related documents:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_en.md) ← Main document
- [DCH_WeeklyToMonthly_SQL.md](./DCH_WeeklyToMonthly_SQL_en.md) — SQL aggregation function
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_en.md) — Power BI alternative
- [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_en.md) — Global Link in DCH
- [DCH_WeeklyToMonthly_HTML.md](./DCH_WeeklyToMonthly_HTML_en.md) — Static HTML alternative

---

## 1. What is SSRS?

SQL Server Reporting Services is Microsoft's reporting engine, **included in the SQL Server license** (Standard or higher). It allows:

- Designing reports with tables, charts, and parameters
- Publishing them to a web portal (Report Server)
- Accessing via URL (compatible with DCH's Global Link)
- Exporting to Excel, PDF, CSV
- Running on demand or scheduled

**No additional license required** — it is already included in SQL Server Standard.

---

## 2. Verify if SSRS is installed

### On the SQL Server machine

1. Open **SQL Server Configuration Manager**
2. Look for **SQL Server Reporting Services** in the list of services
3. If the service exists and is running, SSRS is installed

Alternatively, open in the browser:
```
http://localhost/Reports
```
If the SSRS web portal loads, it is installed.

### If it is not installed

1. Run the SQL Server installer
2. Select **Add features to an existing instance**
3. Check **Reporting Services - Native**
4. Complete the installation
5. Configure the Report Server (the Configuration Manager opens automatically upon completion)

---

## 3. SSRS Configuration

### 3.1 SQL Server Reporting Services Configuration Manager

1. Open **Reporting Services Configuration Manager**
2. Connect to the SSRS instance
3. Configure the following sections:

| Section | Action |
|---|---|
| **Web Service URL** | Configure port (default: 80) and virtual directory (`ReportServer`) |
| **Database** | Create/confirm the `ReportServer` database (where SSRS stores its metadata) |
| **Web Portal URL** | Configure the web portal (`Reports`) |

When finished, verify by accessing:
- Portal: `http://server/Reports`
- Web Service: `http://server/ReportServer`

### 3.2 Configure authentication for iframe (DCH)

To allow SSRS to be embedded in DCH's iframe, it must be permitted:

1. On the SSRS server, edit the file `ReportServer\Pages\ReportViewer.aspx`
2. Add the header `X-Frame-Options: ALLOW-FROM http://dch-server` (or use `SAMEORIGIN` if DCH and SSRS are on the same domain)

Simpler alternative: use the `&rs:Embed=true` parameter in the URL (works in SSRS 2016+).

---

## 4. Install Report Builder

**Report Builder** is Microsoft's free tool for designing SSRS reports.

1. Download from: https://www.microsoft.com/en-us/download/details.aspx?id=53613
2. Install on the developer's machine
3. When opening, connect to the Report Server: `http://server/ReportServer`

---

## 5. Design the monthly report

### 5.1 Create the Data Source

1. In Report Builder, create a **New Report** (Blank Report)
2. Add a **Data Source**:
   - **Name**: `DCH_DataSource`
   - **Type**: Microsoft SQL Server
   - **Connection string**: `Data Source=SERVER_NAME;Initial Catalog=DCH_DATABASE`
   - **Credentials**: Stored credentials (SQL user with read permissions on `WebCO_ForecastWeekly` and the function)

### 5.2 Create the Dataset

1. Add a **Dataset**:
   - **Name**: `MonthlyForecast`
   - **Data Source**: `DCH_DataSource`
   - **Query**:
     ```sql
     SELECT * 
     FROM [dbo].[fn_WebCO_ForecastWeeklyToMonthly](
         @USER_NAME, 
         @DATE_FORECAST_CURRENT, 
         @DATE_FORECAST_END
     )
     ```

2. The parameters `@USER_NAME`, `@DATE_FORECAST_CURRENT`, `@DATE_FORECAST_END` are created automatically. Configure default values:
   - `@USER_NAME`: Default = `""`
   - `@DATE_FORECAST_CURRENT`: Default = `NULL` (not required)
   - `@DATE_FORECAST_END`: Default = `NULL` (not required)

### 5.3 Design the table

1. Insert a **Table** (matrix or simple table)
2. Recommended columns:
   - `COProductId` / `ProductDescr` (if using the enriched view)
   - `COMarketId` / `MarketDescr`
   - `Year`
   - `Month`
   - `Budget`
   - `FrcQty`
   - `COQty1` … `COQty5` (Forecast Revisions)
   - `OutstQty`
   - `COSO99`

3. Group by `COProductId` and `COMarketId` to allow drill-down
4. Add **totals** by group

### 5.4 Add Excel export

SSRS includes native Excel export (button in the toolbar). If `rs:Embed=true` is used, the toolbar is hidden. To continue allowing export:

- Option A: Do not use `rs:Embed=true` and keep the toolbar visible
- Option B: Add a `&rs:Command=Render&rs:Format=EXCEL` parameter in a link within the report itself

---

## 6. Publish the report

1. In Report Builder: **File > Save As > Save to Report Server**
2. URL: `http://server/ReportServer`
3. Folder: `/` (root) or create a `/DCH` folder
4. Name: `MonthlyForecast`

The report becomes accessible at:
```
http://server/ReportServer?/MonthlyForecast
```

### Verify publication

Open in the browser:
```
http://server/ReportServer?/MonthlyForecast&USER_NAME=test&DATE_FORECAST_CURRENT=2026-01-01&DATE_FORECAST_END=2026-12-31
```

---

## 7. URL for DCH Global Link

The final URL to configure in DCH's Global Link:

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```

The placeholders `{USER_NAME}`, `{DATE_FORECAST_CURRENT}`, `{DATE_FORECAST_END}` are replaced by DCH automatically before loading the URL in the iframe.

> See [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_en.md) for the complete Global Link configuration.

---

## 8. SSRS Troubleshooting

| Problem | Solution |
|---|---|
| "The report server cannot access the data source" | Verify credentials in the Data Source (use stored credentials, not Windows Integrated) |
| The report does not display in DCH's iframe | Add `&rs:Embed=true` to the URL; verify X-Frame-Options |
| Error publishing from Report Builder | Verify user permissions on the Report Server (Content Manager or Publisher) |
| The function does not appear in the object explorer | Verify it was created correctly with `SELECT * FROM sys.objects WHERE name = 'fn_WebCO_ForecastWeeklyToMonthly'` |
| Parameters are not being passed correctly | The names in the URL must match **exactly** (case-sensitive in some cases) those defined in the report |

---

> **Document version**: 1.0  
> **Date**: 2026-08-05  
> **Scope**: DCH 440 — Weekly Mode  
> **Client**: Dr. Schaer