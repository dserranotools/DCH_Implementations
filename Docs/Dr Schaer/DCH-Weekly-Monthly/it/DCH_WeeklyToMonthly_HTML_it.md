# DCH Weekly → Monthly — Alternativa: Report HTML statico

**Cliente:** Dr. Schaer  
**Versione:** 1.0  
**Data:** 2026-08-05  
**Ambito:** DCH 440 — Modalità Weekly  

**Documenti correlati:**
- [DCH_WeeklyToMonthly_Main.md](../DCH_WeeklyToMonthly_Main.md) ← Documento principale
- [DCH_WeeklyToMonthly_SQL.md](../DCH_WeeklyToMonthly_SQL_it.md) — Function SQL di aggregazione
- [DCH_WeeklyToMonthly_SSRS.md](../DCH_WeeklyToMonthly_SSRS_it.md) — Guida SSRS (opzione consigliata)
- [DCH_WeeklyToMonthly_PowerBI.md](../DCH_WeeklyToMonthly_PowerBI_it.md) — Alternativa Power BI
- [DCH_WeeklyToMonthly_GlobalLink.md](../DCH_WeeklyToMonthly_GlobalLink_it.md) — Global Link in DCH

---

## 1. Descrizione

Alternativa a SSRS per ambienti in cui **non è possibile o non si vuole installare SSRS**. Consiste in:

1. Una **Custom Procedure** che esegue la query contro la function `fn_WebCO_ForecastWeeklyToMonthly` e genera un file `.html` con una tabella formattata
2. Il file viene salvato in una cartella accessibile via IIS (es: `D:\DCH\Reports\`)
3. Un **Global Link** in DCH punta a `http://dch-server/DCH/Reports/MonthlyReport.html`
4. La procedure viene eseguita via `DCHRemote /EXECUTESQL` in modo programmato (es: ogni notte)

---

## 2. Confronto SSRS vs HTML statico

| Caratteristica | SSRS | HTML statico |
|---|---|---|
| **Licenza aggiuntiva** | No (inclusa in SQL Server) | No |
| **Installazione aggiuntiva** | Sì (feature di SQL Server) | No |
| **Interattività** | Filtri, parametri, drill-down | Nessuna (tabella piatta) |
| **Esportazione in Excel** | Nativa | Manuale (copia/incolla) |
| **Aggiornamento dei dati** | In tempo reale (interroga il DB a ogni caricamento) | Programmato (l'HTML viene rigenerato) |
| **Manutenzione** | Media (report .rdl + Report Server) | Bassa (un SQL + un .html) |
| **Complessità di implementazione** | Media | Bassa |
| **Aspetto visivo** | Professionale (formattazione condizionale, grafici) | Base (HTML con CSS) |

---

## 3. Implementazione

### 3.1 Creare la cartella per i report

Sul server DCH:
```
D:\DCH\Reports\
```

Assicurare permessi di scrittura per il servizio SQL Server e permessi di lettura per IIS.

### 3.2 Creare una virtual directory in IIS (se necessario)

Se la cartella non si trova all'interno del sito web di DCH, aggiungere una Virtual Directory in IIS che punti a `D:\DCH\Reports\`.

### 3.3 Creare la Custom Procedure

Registrare in `SYSTEM_CustomProcedure`:

```sql
INSERT INTO SYSTEM_CustomProcedure (CustomProcedureId, Descr, Source, tsql, scriptPath, processPath)
VALUES ('6_GENERATE_MONTHLY_REPORT', 'Generate Monthly Forecast HTML Report', 1, '', 'D:\DCH\Scripts\6_GENERATE_MONTHLY_REPORT.sql', '')
```

### 3.4 Script SQL per generare l'HTML

File `D:\DCH\Scripts\6_GENERATE_MONTHLY_REPORT.sql`:

```sql
SET NOCOUNT ON

DECLARE @html NVARCHAR(MAX) = ''
DECLARE @filePath NVARCHAR(500) = 'D:\DCH\Reports\MonthlyReport.html'
DECLARE @dateFrom DATE = NULL  -- o data fissa
DECLARE @dateTo DATE = NULL
DECLARE @userName NVARCHAR(128) = 'SYSTEM'

-- Costruire l'intestazione HTML
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

-- Costruire le righe dei dati
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

-- Chiudere l'HTML
SET @html = @html + '
        </tbody>
    </table>
</body>
</html>'

-- Scrivere su file (richiede xp_cmdshell abilitato o usare BCP)
DECLARE @cmd NVARCHAR(1000)
SET @cmd = 'echo ' + REPLACE(@html, '''', '''''') + ' > "' + @filePath + '"'
-- Nota: per HTML di grandi dimensioni, è meglio usare BCP o uno script PowerShell

PRINT 'Monthly Report HTML generated.'
```

> **Nota**: La generazione di HTML da TSQL con `FOR XML PATH` è adatta per insiemi di dati piccoli. Per volumi grandi (migliaia di prodotti/mercati), è meglio usare uno script PowerShell esterno o SSIS.

### 3.5 Configurare il Global Link

URL del Global Link:
```
http://dch-server/DCH/Reports/MonthlyReport.html
```

Oppure, se si trova in una cartella virtuale separata:
```
http://dch-server/Reports/MonthlyReport.html
```

---

## 4. Limitazioni

- **Nessuna interattività**: Non è possibile filtrare, ordinare né fare drill-down
- **Nessuna esportazione nativa**: L'utente deve copiare/incollare la tabella
- **Nessun parametro dinamico**: I placeholder `{USER_NAME}` non si applicano (l'HTML è lo stesso per tutti)
- **Rigenerazione necessaria**: Se i dati cambiano, è necessario ri-eseguire lo script
- **Dimensione limitata**: Per insiemi di dati grandi, l'HTML può essere pesante e lento da caricare

---

> **Versione documento**: 1.0  
> **Data**: 2026-08-05  
> **Ambito**: DCH 440 — Modalità Weekly  
> **Cliente**: Dr. Schaer