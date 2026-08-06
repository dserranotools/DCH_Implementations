| [Main](DCH_WeeklyToMonthly_1_Main_it.md) | 📄 GlobalLink | [HTML](DCH_WeeklyToMonthly_HTML_it.md) | [PowerBI](DCH_WeeklyToMonthly_PowerBI_it.md) | [SQL](DCH_WeeklyToMonthly_SQL_it.md) | [SSRS](DCH_WeeklyToMonthly_SSRS_it.md) |
|:---:|:---:|:---:|:---:|:---:|:---:|

&nbsp;

# DCH Weekly → Monthly — Configurazione del Global Link

**Cliente:** Dr. Schaer  
**Versione:** 1.0  
**Data:** 2026-08-05  
**Ambito:** DCH 440 — Modalità Weekly  

**Documenti correlati:**
- [DCH_WeeklyToMonthly_Main.md](../DCH_WeeklyToMonthly_Main.md) ← Documento principale
- [DCH_WeeklyToMonthly_SQL.md](../DCH_WeeklyToMonthly_SQL_it.md) — Function SQL di aggregazione
- [DCH_WeeklyToMonthly_SSRS.md](../DCH_WeeklyToMonthly_SSRS_it.md) — Guida SSRS
- [DCH_WeeklyToMonthly_PowerBI.md](../DCH_WeeklyToMonthly_PowerBI_it.md) — Alternativa Power BI
- [DCH_WeeklyToMonthly_HTML.md](../DCH_WeeklyToMonthly_HTML_it.md) — Alternativa HTML statico

---

## 1. Che cos'è un Global Link?

DCH consente di configurare **link esterni** che vengono visualizzati nel menu **Cockpit**. Questi link:

- Si aprono in un **iframe incorporato** all'interno dell'interfaccia di DCH
- Supportano **placeholder** che vengono sostituiti dinamicamente con i dati dell'utente e del forecast
- Possono essere **Globali** (visibili a tutti gli utenti) o per **Utente** (ogni utente configura i propri)
- Si gestiscono da `Auxiliary Data > Global Links` (admin) o `Users > Links` (utente)

---

## 2. Placeholder disponibili

| Placeholder | Valore sostituito | Esempio |
|---|---|---|
| `{USER_NAME}` | Nome utente autenticato (lowercase) | `john.doe` |
| `{DATE_FORECAST_CURRENT}` | Data di inizio dell'orizzonte di forecast, nel formato configurato in `PARAM_GLOBAL_LINKS_DATE_FORMAT` | `2026-01-05` |
| `{DATE_FORECAST_END}` | Data di fine dell'orizzonte di forecast | `2026-12-28` |

> Il formato della data si configura in `CONFIG_ParamGen`: `PARAM_GLOBAL_LINKS_DATE_FORMAT`. Predefinito: `yyyy-MM-dd`.

---

## 3. Configurazione passo passo

### 3.1 Accedere ai Global Links

1. Entrare in DCH come **admin**
2. Andare su `Menu > Auxiliary Data > Global Links`
3. Visualizzare l'elenco dei link esistenti (se presenti)

### 3.2 Creare un nuovo Global Link

Fare clic su **New** e compilare:

| Campo | Valore |
|---|---|
| **Description** | `Monthly Forecast Report` o il nome descrittivo preferito dal cliente |
| **Link (URL)** | L'URL del report SSRS con placeholder |

**URL completa:**
```
http://SSRS_SERVER/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```

Dove:
- `SSRS_SERVER` = nome o IP del server su cui è in esecuzione SSRS
- `/MonthlyForecast` = percorso del report nel Report Server
- `&rs:Embed=true` = nasconde la barra degli strumenti di SSRS per una visualizzazione pulita nell'iframe

### 3.3 Salvare

Fare clic su **Save**. Il link appare nell'elenco dei Global Links.

### 3.4 Verificare nel Cockpit

1. Andare su `Cockpit`
2. Cercare la voce **"Monthly Forecast Report"** (o il nome scelto)
3. Fare clic — si deve aprire il report SSRS incorporato in DCH

---

## 4. Configurazione per utente (User Links)

Se si desidera che **ogni utente abbia il proprio link** (invece di uno globale per tutti):

1. Andare su `Users > [nome utente] > Links`
2. Fare clic su **New**
3. Configurare come per il Global Link
4. Salvare

Il link apparirà in `Cockpit` solo per quell'utente.

> **Raccomandazione**: Usare Global Link a meno che non vi sia un'esigenza specifica di personalizzazione per utente. È più facile da mantenere.

---

## 5. Esempio: due link (globale + forecast attuale)

Si possono creare più link per diverse visualizzazioni:

### Link 1: Forecast completo (con date dell'orizzonte)

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```
- **Description**: `Monthly Forecast (Horizon)`
- Mostra il report filtrato sull'orizzonte di forecast attuale

### Link 2: Forecast senza filtro date (tutti i dati)

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&rs:Embed=true
```
- **Description**: `Monthly Forecast (All Data)`
- Mostra il report con tutti i dati storici

---

## 6. Troubleshooting

| Problema | Soluzione |
|---|---|
| Il link non appare nel Cockpit | Verificare che sia stato salvato correttamente in `Auxiliary Data > Global Links` |
| L'iframe mostra errore "X-Frame-Options" | Usare `&rs:Embed=true` nell'URL; configurare SSRS per consentire l'embedding |
| I placeholder non vengono sostituiti | Verificare che le parentesi siano `{PLACEHOLDER}` (non `%PLACEHOLDER%` né `[PLACEHOLDER]`) |
| Il report si carica ma senza dati | Verificare che la function SQL restituisca dati per quell'intervallo di date; testare l'URL direttamente nel browser |
| Errore di credenziali SSRS | Configurare **stored credentials** nell'origine dati del report, non Windows Integrated |

---

> **Documento versione**: 1.0  
> **Data**: 2026-08-05  
> **Ambito**: DCH 440 — Modalità Weekly  
> **Cliente**: Dr. Schaer