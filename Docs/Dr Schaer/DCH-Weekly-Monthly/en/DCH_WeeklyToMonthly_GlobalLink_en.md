# DCH Weekly → Monthly — Global Link Configuration

**Client:** Dr. Schaer  
**Version:** 1.0  
**Date:** 2026-08-05  
**Scope:** DCH 440 — Weekly Mode  

**Related documents:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_en.md) ← Main document
- [DCH_WeeklyToMonthly_SQL.md](./DCH_WeeklyToMonthly_SQL_en.md) — SQL aggregation function
- [DCH_WeeklyToMonthly_SSRS.md](./DCH_WeeklyToMonthly_SSRS_en.md) — SSRS guide
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_en.md) — Power BI alternative
- [DCH_WeeklyToMonthly_HTML.md](./DCH_WeeklyToMonthly_HTML_en.md) — Static HTML alternative

---

## 1. What is a Global Link?

DCH allows configuring **external links** displayed in the **Cockpit** menu. These links:

- Open in an **embedded iframe** within the DCH interface
- Support **placeholders** that are dynamically replaced with user and forecast data
- Can be **Global** (visible to all users) or per **User** (each user configures their own)
- Are managed from `Auxiliary Data > Global Links` (admin) or `Users > Links` (user)

---

## 2. Available placeholders

| Placeholder | Replaced value | Example |
|---|---|---|
| `{USER_NAME}` | Authenticated username (lowercase) | `john.doe` |
| `{DATE_FORECAST_CURRENT}` | Forecast horizon start date, in the format configured in `PARAM_GLOBAL_LINKS_DATE_FORMAT` | `2026-01-05` |
| `{DATE_FORECAST_END}` | Forecast horizon end date | `2026-12-28` |

> The date format is configured in `CONFIG_ParamGen`: `PARAM_GLOBAL_LINKS_DATE_FORMAT`. Default: `yyyy-MM-dd`.

---

## 3. Step-by-step configuration

### 3.1 Access Global Links

1. Log into DCH as **admin**
2. Go to `Menu > Auxiliary Data > Global Links`
3. View the list of existing links (if any)

### 3.2 Create a new Global Link

Click **New** and fill in:

| Field | Value |
|---|---|
| **Description** | `Monthly Forecast Report` or any descriptive name the client prefers |
| **Link (URL)** | The SSRS report URL with placeholders |

**Full URL:**
```
http://SSRS_SERVER/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```

Where:
- `SSRS_SERVER` = name or IP of the server running SSRS
- `/MonthlyForecast` = report path on the Report Server
- `&rs:Embed=true` = hides the SSRS toolbar for a clean display in the iframe

### 3.3 Save

Click **Save**. The link appears in the Global Links list.

### 3.4 Verify in Cockpit

1. Go to `Cockpit`
2. Look for the **"Monthly Forecast Report"** entry (or the chosen name)
3. Click — the SSRS report should open embedded in DCH

---

## 4. Per-user configuration (User Links)

If you want **each user to have their own link** (instead of one global link for everyone):

1. Go to `Users > [username] > Links`
2. Click **New**
3. Configure the same as a Global Link
4. Save

The link will appear in `Cockpit` only for that user.

> **Recommendation**: Use a Global Link unless there is a specific need for per-user customization. It is easier to maintain.

---

## 5. Example: two links (global + current forecast)

Multiple links can be created for different views:

### Link 1: Full forecast (with horizon dates)

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```
- **Description**: `Monthly Forecast (Horizon)`
- Displays the report filtered to the current forecast horizon

### Link 2: Forecast without date filter (all data)

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&rs:Embed=true
```
- **Description**: `Monthly Forecast (All Data)`
- Displays the report with all historical data

---

## 6. Troubleshooting

| Problem | Solution |
|---|---|
| The link does not appear in Cockpit | Verify it was saved correctly in `Auxiliary Data > Global Links` |
| The iframe shows "X-Frame-Options" error | Use `&rs:Embed=true` in the URL; configure SSRS to allow embedding |
| Placeholders are not being replaced | Verify that braces are `{PLACEHOLDER}` (not `%PLACEHOLDER%` or `[PLACEHOLDER]`) |
| The report loads but has no data | Verify the SQL function returns data for that date range; test the URL directly in the browser |
| SSRS credential error | Configure **stored credentials** in the report's Data Source, not Windows Integrated |

---

> **Document version**: 1.0  
> **Date**: 2026-08-05  
> **Scope**: DCH 440 — Weekly Mode  
> **Client**: Dr. Schaer