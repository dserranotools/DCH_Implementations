# DCH Weekly → Monthly — Guida SSRS

**Cliente:** Dr. Schaer  
**Versione:** 1.0  
**Data:** 2026-08-05  
**Ambito:** DCH 440 — Modalità Weekly  

**Documenti correlati:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_it.md) ← Documento principale
- [DCH_WeeklyToMonthly_SQL.md](./DCH_WeeklyToMonthly_SQL_it.md) — Function SQL di aggregazione
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_it.md) — Alternativa Power BI
- [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_it.md) — Global Link in DCH
- [DCH_WeeklyToMonthly_HTML.md](./DCH_WeeklyToMonthly_HTML_it.md) — Alternativa HTML statico

---

## 1. Che cos'è SSRS?

SQL Server Reporting Services è il motore di reporting di Microsoft, **incluso nella licenza di SQL Server** (Standard o superiore). Consente di:

- Progettare report con tabelle, grafici e parametri
- Pubblicarli su un portale web (Report Server)
- Accedere via URL (compatibile con il Global Link di DCH)
- Esportare in Excel, PDF, CSV
- Eseguire su richiesta o in modo programmato

**Non richiede licenze aggiuntive** — è già incluso in SQL Server Standard.

---

## 2. Verificare se SSRS è installato

### Sul server SQL Server

1. Aprire **SQL Server Configuration Manager**
2. Cercare **SQL Server Reporting Services** nell'elenco dei servizi
3. Se il servizio esiste ed è in esecuzione, SSRS è installato

In alternativa, aprire nel browser:
```
http://localhost/Reports
```
Se carica il portale web di SSRS, è installato.

### Se non è installato

1. Eseguire il programma di installazione di SQL Server
2. Selezionare **Add features to an existing instance**
3. Selezionare **Reporting Services - Native**
4. Completare l'installazione
5. Configurare il Report Server (si apre automaticamente il Configuration Manager al termine)

---

## 3. Configurazione di SSRS

### 3.1 SQL Server Reporting Services Configuration Manager

1. Aprire **Reporting Services Configuration Manager**
2. Connettersi all'istanza di SSRS
3. Configurare le seguenti sezioni:

| Sezione | Azione |
|---|---|
| **Web Service URL** | Configurare la porta (default: 80) e la directory virtuale (`ReportServer`) |
| **Database** | Creare/confermare il database `ReportServer` (dove SSRS salva i suoi metadati) |
| **Web Portal URL** | Configurare il portale web (`Reports`) |

Al termine, verificare l'accesso a:
- Portale: `http://server/Reports`
- Web Service: `http://server/ReportServer`

### 3.2 Configurare l'autenticazione per iframe (DCH)

Per consentire l'incorporamento di SSRS nell'iframe di DCH, è necessario abilitarlo:

1. Sul server SSRS, modificare il file `ReportServer\Pages\ReportViewer.aspx`
2. Aggiungere l'header `X-Frame-Options: ALLOW-FROM http://dch-server` (o usare `SAMEORIGIN` se DCH e SSRS sono sullo stesso dominio)

Alternativa più semplice: usare il parametro `&rs:Embed=true` nell'URL (funziona in SSRS 2016+).

---

## 4. Installare Report Builder

**Report Builder** è lo strumento gratuito di Microsoft per progettare report SSRS.

1. Scaricare da: https://www.microsoft.com/en-us/download/details.aspx?id=53613
2. Installare sulla macchina dello sviluppatore
3. All'apertura, connettersi al Report Server: `http://server/ReportServer`

---

## 5. Progettare il report mensile

### 5.1 Creare l'Origine Dati (Data Source)

1. In Report Builder, creare un **New Report** (Blank Report)
2. Aggiungere un **Data Source**:
   - **Name**: `DCH_DataSource`
   - **Type**: Microsoft SQL Server
   - **Connection string**: `Data Source=SERVER_NAME;Initial Catalog=DCH_DATABASE`
   - **Credentials**: Credenziali memorizzate (utente SQL con permessi di lettura su `WebCO_ForecastWeekly` e la function)

### 5.2 Creare il Dataset

1. Aggiungere un **Dataset**:
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

2. I parametri `@USER_NAME`, `@DATE_FORECAST_CURRENT`, `@DATE_FORECAST_END` vengono creati automaticamente. Configurare i valori predefiniti:
   - `@USER_NAME`: Default = `""`
   - `@DATE_FORECAST_CURRENT`: Default = `NULL` (non obbligatorio)
   - `@DATE_FORECAST_END`: Default = `NULL` (non obbligatorio)

### 5.3 Progettare la tabella

1. Inserire una **Table** (matrice o tabella semplice)
2. Colonne consigliate:
   - `COProductId` / `ProductDescr` (se si usa la vista arricchita)
   - `COMarketId` / `MarketDescr`
   - `Year`
   - `Month`
   - `Budget`
   - `FrcQty`
   - `COQty1` ... `COQty5` (Revisioni Forecast)
   - `OutstQty`
   - `COSO99`

3. Raggruppare per `COProductId` e `COMarketId` per consentire il drill-down
4. Aggiungere **totali** per gruppo

### 5.4 Aggiungere l'esportazione in Excel

SSRS include l'esportazione in Excel in modo nativo (pulsante nella barra degli strumenti). Se si usa `rs:Embed=true`, la barra degli strumenti viene nascosta. Per consentire comunque l'esportazione:

- Opzione A: Non usare `rs:Embed=true` e mantenere visibile la barra degli strumenti
- Opzione B: Aggiungere un parametro `&rs:Command=Render&rs:Format=EXCEL` in un collegamento all'interno del report stesso

---

## 6. Pubblicare il report

1. In Report Builder: **File > Save As > Save to Report Server**
2. URL: `http://server/ReportServer`
3. Cartella: `/` (radice) o creare una cartella `/DCH`
4. Nome: `MonthlyForecast`

Il report sarà accessibile all'indirizzo:
```
http://server/ReportServer?/MonthlyForecast
```

### Verificare la pubblicazione

Aprire nel browser:
```
http://server/ReportServer?/MonthlyForecast&USER_NAME=test&DATE_FORECAST_CURRENT=2026-01-01&DATE_FORECAST_END=2026-12-31
```

---

## 7. URL per il Global Link di DCH

L'URL finale da configurare nel Global Link di DCH:

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```

I placeholder `{USER_NAME}`, `{DATE_FORECAST_CURRENT}`, `{DATE_FORECAST_END}` vengono sostituiti automaticamente da DCH prima di caricare l'URL nell'iframe.

> Vedi [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_it.md) per la configurazione completa del Global Link.

---

## 8. Risoluzione dei problemi SSRS

| Problema | Soluzione |
|---|---|
| "The report server cannot access the data source" | Verificare le credenziali nell'Origine Dati (usare credenziali memorizzate, non Windows Integrated) |
| Il report non viene visualizzato nell'iframe di DCH | Aggiungere `&rs:Embed=true` all'URL; verificare X-Frame-Options |
| Errore durante la pubblicazione da Report Builder | Verificare i permessi dell'utente sul Report Server (Content Manager o Publisher) |
| La function non appare nell'esploratore oggetti | Verificare che sia stata creata correttamente con `SELECT * FROM sys.objects WHERE name = 'fn_WebCO_ForecastWeeklyToMonthly'` |
| I parametri non vengono passati correttamente | I nomi nell'URL devono corrispondere **esattamente** (in alcuni casi sono case-sensitive) a quelli definiti nel report |

---

> **Versione documento**: 1.0  
> **Data**: 2026-08-05  
> **Ambito**: DCH 440 — Modalità Weekly  
> **Cliente**: Dr. Schaer