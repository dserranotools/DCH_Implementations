# DCH Remote — Command Reference

**Client:** Dr. Schaer  
**Version:** 1.0  
**Date:** 2026-08-05  
**Scope:** DCH 440

---

## General Usage

```cmd
DCHRemote.exe [COMMAND] [PARAMETERS...]
```

DCHRemote communicates with DCH via Web API. Each execution performs **a single operation** and then terminates. It is suitable for scheduling in batch or Windows Task Scheduler.

---

## Command Index

| Category | Commands |
|---|---|
| [Import / Export](#import--export) | `/IMPORT`, `/IMPORT_SINGLE_FILE`, `/IMPORT_MULTIPLE_FILES`, `/EXPORT` |
| [Forecast Revisions Initialization](#forecast-revisions-initialization) | `/INIT_CO`, `/INIT_BUDGET`, `/REFRESH_SO99_FORECAST` |
| [Custom Procedures (SQL)](#custom-procedures-sql) | `/EXECUTESQL` |
| [Approval Workflow](#approval-workflow) | `/SIGN_OFF_USER`, `/SIGN_OFF_USER_LEVEL`, `/END_APPROVAL_WORKFLOW`, `/CHECK_AUTOMATIC_SIGN_OFF` |
| [User Management](#user-management) | `/USER_FRC_WRITE_ENABLE`, `/USER_FRC_WRITE_DISABLE`, `/USER_INTERNAL_IMPORT`, `/USER_EXTERNAL_IMPORT` |
| [Alerts](#alerts) | `/RUN_ALERT` |
| [Maintenance](#maintenance) | `/CLEAR_CACHE`, `/SET_FROZEN_PERIOD`, `/SEND_EMAIL`, `/ENCRYPT`, `/DECRYPT`, `/TEST` |

---

## Import / Export

### `/IMPORT`

Executes **all** imports configured in DCH.

```cmd
DCHRemote.exe /IMPORT
```

### `/IMPORT_SINGLE_FILE [FILE_ID]`

Imports a **single file** by its `FILE_ID` (as defined in `CONFIG_ImportFile`).

```cmd
DCHRemote.exe /IMPORT_SINGLE_FILE 1
```

### `/IMPORT_MULTIPLE_FILES [ID1-ID2-ID3...]`

Imports several files at once. IDs are separated with hyphens.

```cmd
DCHRemote.exe /IMPORT_MULTIPLE_FILES 1-2-5-12
```

### `/EXPORT`

Executes **all** exports configured in DCH (as defined in `CONFIG_ExportQuery`).

```cmd
DCHRemote.exe /EXPORT
```

---

## Forecast Revisions Initialization

All of these commands copy data from a source series to a target Forecast Revision. `CO_IDX_TO` = the FR index (1 = FR1, 2 = FR2, etc.).

### Initialize FR from Source

| Command | Source → Target |
|---|---|
| `/INIT_CO N /INIT_FROM_SO99_FRC` | SO99 Statistical Forecast → FR N |
| `/INIT_CO N /INIT_FROM_SO99_CO` | SO99 Customer Orders → FR N |
| `/INIT_CO N /INIT_FROM_WEB_CO M` | FR M → FR N |
| `/INIT_CO N /INIT_FROM_BUDGET` | Budget → FR N |
| `/INIT_CO N /INIT_FROM_DS M` | Display Serie M → FR N |

### Initialize Budget from Source

| Command | Source → Budget |
|---|---|
| `/INIT_BUDGET /INIT_FROM_SO99_FRC` | SO99 Statistical Forecast → Budget |
| `/INIT_BUDGET /INIT_FROM_SO99_CO` | SO99 Customer Orders → Budget |
| `/INIT_BUDGET /INIT_FROM_WEB_CO M` | FR M → Budget |
| `/INIT_BUDGET /INIT_FROM_DS M` | Display Serie M → Budget |

### Refresh Forecast Table

```cmd
DCHRemote.exe /REFRESH_SO99_FORECAST
```

Updates the internal table `Temp_SO99ForecastWeekly`/`Monthly` with the latest data from SO99+.

### Examples

```cmd
REM Initialize FR1 from SO99 Statistical Forecast
DCHRemote.exe /INIT_CO 1 /INIT_FROM_SO99_FRC

REM Initialize FR2 from FR1 (chained)
DCHRemote.exe /INIT_CO 2 /INIT_FROM_WEB_CO 1

REM Initialize Budget from FR3
DCHRemote.exe /INIT_BUDGET /INIT_FROM_WEB_CO 3
```

---

## Custom Procedures (SQL)

### `/EXECUTESQL [PROCEDURE_ID]`

Executes a Custom Procedure registered in `SYSTEM_CustomProcedure`. The procedure can be of type:

- **`tsql`** (`Source = 0`): executes the TSQL stored in the `TSQL` field
- **`sqlScript`** (`Source = 1`): reads and executes the `.sql` file at the `ScriptPath` path
- **`externalProcess`** (`Source = 2`): launches the executable at `ProcessPath`

```cmd
DCHRemote.exe /EXECUTESQL TSQL1
DCHRemote.exe /EXECUTESQL SETUP_FR_PARALLEL
DCHRemote.exe /EXECUTESQL FREEZE_ALL_WRITE
```

> ⚠️ The DCH server must have read access to the path specified in `ScriptPath`.

---

## Approval Workflow

> Only take effect if `APPROVAL_WORKFLOW_ENABLED = 1`.

### `/SIGN_OFF_USER [USER_NAME]`

Forces the Sign-Off of a specific user.

```cmd
DCHRemote.exe /SIGN_OFF_USER system
DCHRemote.exe /SIGN_OFF_USER user1a
```

### `/SIGN_OFF_USER_LEVEL [USER_LEVEL]`

Forces the Sign-Off of **all** users at a hierarchical level.

```cmd
DCHRemote.exe /SIGN_OFF_USER_LEVEL 1
```

### `/END_APPROVAL_WORKFLOW`

Ends the current approval cycle and creates a new one. All users return to their initial state.

```cmd
DCHRemote.exe /END_APPROVAL_WORKFLOW
```

### `/CHECK_AUTOMATIC_SIGN_OFF`

Runs the automatic Sign-Off for users who have exceeded their deadline.

```cmd
DCHRemote.exe /CHECK_AUTOMATIC_SIGN_OFF
```

---

## User Management

### `/USER_FRC_WRITE_ENABLE [USER_NAME]`

Grants **write** permissions in Forecast Editing to a user.

```cmd
DCHRemote.exe /USER_FRC_WRITE_ENABLE system
DCHRemote.exe /USER_FRC_WRITE_ENABLE user1a
```

> Modifies `CONFIG_UserFunction`: `FunctionName = 'ForecastEditing'`, `WritePermission = 1`.

### `/USER_FRC_WRITE_DISABLE [USER_NAME]`

Revokes **write** permissions in Forecast Editing from a user (keeps read-only).

```cmd
DCHRemote.exe /USER_FRC_WRITE_DISABLE system
```

### `/USER_INTERNAL_IMPORT [FILE_NAME]`

Imports internal users from a CSV file.

```cmd
DCHRemote.exe /USER_INTERNAL_IMPORT c:\dchImport\internalUsers.csv
```

### `/USER_EXTERNAL_IMPORT [FILE_NAME]`

Imports external users (Windows Auth) from a CSV file.

```cmd
DCHRemote.exe /USER_EXTERNAL_IMPORT c:\dchImport\externalUsers.csv
```

---

## Alerts

### `/RUN_ALERT`

Recalculates **all** alerts configured in the `Alerts` table.

```cmd
DCHRemote.exe /RUN_ALERT
```

### `/RUN_ALERT [ALERT_ID1-ALERT_ID2-...]`

Recalculates only the alerts specified by their IDs.

```cmd
DCHRemote.exe /RUN_ALERT 1-3-7
```

---

## Maintenance

### `/CLEAR_CACHE`

Clears the DCH cache, forcing a reload of configuration and permissions. **Essential** after modifying `CONFIG_UserFunction`, `CONFIG_ParamGen`, or any configuration table via direct SQL.

```cmd
DCHRemote.exe /CLEAR_CACHE
```

### `/SET_FROZEN_PERIOD [FR] [FROZEN_PERIODS] [EDITABLE_PERIODS]`

Configures the frozen periods of a Forecast Revision.

```cmd
REM FR2: 3 frozen periods, 5 editable periods
DCHRemote.exe /SET_FROZEN_PERIOD 2 3 5
```

### `/SEND_EMAIL [TO] [SUBJECT] [BODY]`

Sends an email from DCH.

```cmd
DCHRemote.exe /SEND_EMAIL username "DCH Data Imported" "All files have been imported successfully"
```

### `/ENCRYPT`

Encrypts the DCHRemote configuration file.

```cmd
DCHRemote.exe /ENCRYPT
```

### `/DECRYPT`

Decrypts the DCHRemote configuration file.

```cmd
DCHRemote.exe /DECRYPT
```

### `/TEST`

Verifies the connection between DCHRemote and the DCH server.

```cmd
DCHRemote.exe /TEST
```

---

> **Document version**: 1.0  
> **Date**: 2026-08-05  
> **Scope**: DCH 440