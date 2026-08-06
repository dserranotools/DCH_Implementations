| [Workflow](DCH_MultiFR_Parallel_Workflow_1_Main_it.md) | [Scripts](DCH_MultiFR_Scripts_it.md) | 📄 DCH Remote |
|:---:|:---:|:---:|

&nbsp;

# DCH Remote — Riferimento dei Comandi

**Cliente:** Dr. Schaer  
**Versione:** 1.0  
**Data:** 2026-08-05  
**Ambito:** DCH 440

---

## Uso generale

```cmd
DCHRemote.exe [COMANDO] [PARAMETRI...]
```

DCHRemote comunica con DCH tramite Web API. Ogni esecuzione esegue **una sola operazione** e termina. È adatto alla pianificazione tramite batch o Windows Task Scheduler.

---

## Indice dei comandi

| Categoria | Comandi |
|---|---|
| [Import / Export](#import--export) | `/IMPORT`, `/IMPORT_SINGLE_FILE`, `/IMPORT_MULTIPLE_FILES`, `/EXPORT` |
| [Inizializzazione Forecast Revision](#inizializzazione-forecast-revision) | `/INIT_CO`, `/INIT_BUDGET`, `/REFRESH_SO99_FORECAST` |
| [Custom Procedures (SQL)](#custom-procedures-sql) | `/EXECUTESQL` |
| [Approval Workflow](#approval-workflow) | `/SIGN_OFF_USER`, `/SIGN_OFF_USER_LEVEL`, `/END_APPROVAL_WORKFLOW`, `/CHECK_AUTOMATIC_SIGN_OFF` |
| [Gestione utenti](#gestione-utenti) | `/USER_FRC_WRITE_ENABLE`, `/USER_FRC_WRITE_DISABLE`, `/USER_INTERNAL_IMPORT`, `/USER_EXTERNAL_IMPORT` |
| [Alert](#alert) | `/RUN_ALERT` |
| [Manutenzione](#manutenzione) | `/CLEAR_CACHE`, `/SET_FROZEN_PERIOD`, `/SEND_EMAIL`, `/ENCRYPT`, `/DECRYPT`, `/TEST` |

---

## Import / Export

### `/IMPORT`

Esegue **tutti** gli import configurati in DCH.

```cmd
DCHRemote.exe /IMPORT
```

### `/IMPORT_SINGLE_FILE [FILE_ID]`

Importa un **singolo file** tramite il suo `FILE_ID` (secondo `CONFIG_ImportFile`).

```cmd
DCHRemote.exe /IMPORT_SINGLE_FILE 1
```

### `/IMPORT_MULTIPLE_FILES [ID1-ID2-ID3...]`

Importa più file contemporaneamente. Gli ID sono separati da trattini.

```cmd
DCHRemote.exe /IMPORT_MULTIPLE_FILES 1-2-5-12
```

### `/EXPORT`

Esegue **tutte** le esportazioni configurate in DCH (secondo `CONFIG_ExportQuery`).

```cmd
DCHRemote.exe /EXPORT
```

---

## Inizializzazione Forecast Revision

Tutti questi comandi copiano i dati da una serie sorgente a una Forecast Revision di destinazione. `CO_IDX_TO` = l'indice della FR (1 = FR1, 2 = FR2, ecc.).

### Inizializzare FR da sorgente

| Comando | Sorgente → Destinazione |
|---|---|
| `/INIT_CO N /INIT_FROM_SO99_FRC` | SO99 Statistical Forecast → FR N |
| `/INIT_CO N /INIT_FROM_SO99_CO` | SO99 Customer Orders → FR N |
| `/INIT_CO N /INIT_FROM_WEB_CO M` | FR M → FR N |
| `/INIT_CO N /INIT_FROM_BUDGET` | Budget → FR N |
| `/INIT_CO N /INIT_FROM_DS M` | Display Serie M → FR N |

### Inizializzare Budget da sorgente

| Comando | Sorgente → Budget |
|---|---|
| `/INIT_BUDGET /INIT_FROM_SO99_FRC` | SO99 Statistical Forecast → Budget |
| `/INIT_BUDGET /INIT_FROM_SO99_CO` | SO99 Customer Orders → Budget |
| `/INIT_BUDGET /INIT_FROM_WEB_CO M` | FR M → Budget |
| `/INIT_BUDGET /INIT_FROM_DS M` | Display Serie M → Budget |

### Aggiornare tabella forecast

```cmd
DCHRemote.exe /REFRESH_SO99_FORECAST
```

Aggiorna la tabella interna `Temp_SO99ForecastWeekly`/`Monthly` con gli ultimi dati SO99+.

### Esempi

```cmd
REM Inizializzare FR1 da SO99 Statistical Forecast
DCHRemote.exe /INIT_CO 1 /INIT_FROM_SO99_FRC

REM Inizializzare FR2 da FR1 (concatenato)
DCHRemote.exe /INIT_CO 2 /INIT_FROM_WEB_CO 1

REM Inizializzare Budget da FR3
DCHRemote.exe /INIT_BUDGET /INIT_FROM_WEB_CO 3
```

---

## Custom Procedures (SQL)

### `/EXECUTESQL [PROCEDURE_ID]`

Esegue una Custom Procedure registrata in `SYSTEM_CustomProcedure`. La procedura può essere di tipo:

- **`tsql`** (`Source = 0`): esegue il TSQL memorizzato nel campo `TSQL`
- **`sqlScript`** (`Source = 1`): legge ed esegue il file `.sql` nel percorso `ScriptPath`
- **`externalProcess`** (`Source = 2`): avvia l'eseguibile in `ProcessPath`

```cmd
DCHRemote.exe /EXECUTESQL TSQL1
DCHRemote.exe /EXECUTESQL SETUP_FR_PARALLEL
DCHRemote.exe /EXECUTESQL FREEZE_ALL_WRITE
```

> ⚠️ Il server DCH deve avere accesso in lettura al percorso specificato in `ScriptPath`.

---

## Approval Workflow

> Hanno effetto solo se `APPROVAL_WORKFLOW_ENABLED = 1`.

### `/SIGN_OFF_USER [USER_NAME]`

Forza il Sign-Off di un utente specifico.

```cmd
DCHRemote.exe /SIGN_OFF_USER system
DCHRemote.exe /SIGN_OFF_USER user1a
```

### `/SIGN_OFF_USER_LEVEL [USER_LEVEL]`

Forza il Sign-Off di **tutti** gli utenti di un livello gerarchico.

```cmd
DCHRemote.exe /SIGN_OFF_USER_LEVEL 1
```

### `/END_APPROVAL_WORKFLOW`

Termina il ciclo di approvazione corrente e ne crea uno nuovo. Tutti gli utenti tornano al loro stato iniziale.

```cmd
DCHRemote.exe /END_APPROVAL_WORKFLOW
```

### `/CHECK_AUTOMATIC_SIGN_OFF`

Esegue il Sign-Off automatico per gli utenti che hanno superato la data limite.

```cmd
DCHRemote.exe /CHECK_AUTOMATIC_SIGN_OFF
```

---

## Gestione utenti

### `/USER_FRC_WRITE_ENABLE [USER_NAME]`

Concede permessi di **scrittura** in Forecast Editing a un utente.

```cmd
DCHRemote.exe /USER_FRC_WRITE_ENABLE system
DCHRemote.exe /USER_FRC_WRITE_ENABLE user1a
```

> Modifica `CONFIG_UserFunction`: `FunctionName = 'ForecastEditing'`, `WritePermission = 1`.

### `/USER_FRC_WRITE_DISABLE [USER_NAME]`

Revoca i permessi di **scrittura** in Forecast Editing a un utente (mantiene la lettura).

```cmd
DCHRemote.exe /USER_FRC_WRITE_DISABLE system
```

### `/USER_INTERNAL_IMPORT [FILE_NAME]`

Importa utenti interni da un file CSV.

```cmd
DCHRemote.exe /USER_INTERNAL_IMPORT c:\dchImport\internalUsers.csv
```

### `/USER_EXTERNAL_IMPORT [FILE_NAME]`

Importa utenti esterni (Windows Auth) da un file CSV.

```cmd
DCHRemote.exe /USER_EXTERNAL_IMPORT c:\dchImport\externalUsers.csv
```

---

## Alert

### `/RUN_ALERT`

Ricalcola **tutti** gli alert configurati nella tabella `Alerts`.

```cmd
DCHRemote.exe /RUN_ALERT
```

### `/RUN_ALERT [ALERT_ID1-ALERT_ID2-...]`

Ricalcola solo gli alert specificati tramite i loro ID.

```cmd
DCHRemote.exe /RUN_ALERT 1-3-7
```

---

## Manutenzione

### `/CLEAR_CACHE`

Pulisce la cache di DCH, forzando il ricaricamento della configurazione e dei permessi. **Indispensabile** dopo aver modificato `CONFIG_UserFunction`, `CONFIG_ParamGen` o qualsiasi tabella di configurazione tramite SQL diretto.

```cmd
DCHRemote.exe /CLEAR_CACHE
```

### `/SET_FROZEN_PERIOD [FR] [FROZEN_PERIODS] [EDITABLE_PERIODS]`

Configura i periodi congelati (frozen) di una Forecast Revision.

```cmd
REM FR2: 3 periodi congelati, 5 periodi modificabili
DCHRemote.exe /SET_FROZEN_PERIOD 2 3 5
```

### `/SEND_EMAIL [TO] [SUBJECT] [BODY]`

Invia un'email da DCH.

```cmd
DCHRemote.exe /SEND_EMAIL username "DCH Data Imported" "All files have been imported successfully"
```

### `/ENCRYPT`

Cripta il file di configurazione di DCHRemote.

```cmd
DCHRemote.exe /ENCRYPT
```

### `/DECRYPT`

Decripta il file di configurazione di DCHRemote.

```cmd
DCHRemote.exe /DECRYPT
```

### `/TEST`

Verifica la connessione tra DCHRemote e il server DCH.

```cmd
DCHRemote.exe /TEST
```

---

> **Versione documento**: 1.0  
> **Data**: 2026-08-05  
> **Ambito**: DCH 440