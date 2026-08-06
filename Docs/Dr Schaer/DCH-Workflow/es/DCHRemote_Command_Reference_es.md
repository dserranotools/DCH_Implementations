# DCH Remote — Referencia de Comandos

**Cliente:** Dr. Schaer  
**Versión:** 1.0  
**Fecha:** 2026-08-05  
**Ámbito:** DCH 440

---

## Uso general

```cmd
DCHRemote.exe [COMANDO] [PARÁMETROS...]
```

DCHRemote se comunica con DCH vía Web API. Cada ejecución realiza **una sola operación** y termina. Es adecuado para programar en batch o Windows Task Scheduler.

---

## Índice de comandos

| Categoría | Comandos |
|---|---|
| [Import / Export](#import--export) | `/IMPORT`, `/IMPORT_SINGLE_FILE`, `/IMPORT_MULTIPLE_FILES`, `/EXPORT` |
| [Inicialización de Forecast Revisions](#inicialización-de-forecast-revisions) | `/INIT_CO`, `/INIT_BUDGET`, `/REFRESH_SO99_FORECAST` |
| [Custom Procedures (SQL)](#custom-procedures-sql) | `/EXECUTESQL` |
| [Approval Workflow](#approval-workflow) | `/SIGN_OFF_USER`, `/SIGN_OFF_USER_LEVEL`, `/END_APPROVAL_WORKFLOW`, `/CHECK_AUTOMATIC_SIGN_OFF` |
| [Gestión de usuarios](#gestión-de-usuarios) | `/USER_FRC_WRITE_ENABLE`, `/USER_FRC_WRITE_DISABLE`, `/USER_INTERNAL_IMPORT`, `/USER_EXTERNAL_IMPORT` |
| [Alerts](#alerts) | `/RUN_ALERT` |
| [Mantenimiento](#mantenimiento) | `/CLEAR_CACHE`, `/SET_FROZEN_PERIOD`, `/SEND_EMAIL`, `/ENCRYPT`, `/DECRYPT`, `/TEST` |

---

## Import / Export

### `/IMPORT`

Ejecuta **todos** los imports configurados en DCH.

```cmd
DCHRemote.exe /IMPORT
```

### `/IMPORT_SINGLE_FILE [FILE_ID]`

Importa un **único fichero** por su `FILE_ID` (según `CONFIG_ImportFile`).

```cmd
DCHRemote.exe /IMPORT_SINGLE_FILE 1
```

### `/IMPORT_MULTIPLE_FILES [ID1-ID2-ID3...]`

Importa varios ficheros a la vez. Los IDs se separan con guiones.

```cmd
DCHRemote.exe /IMPORT_MULTIPLE_FILES 1-2-5-12
```

### `/EXPORT`

Ejecuta **todas** las exportaciones configuradas en DCH (según `CONFIG_ExportQuery`).

```cmd
DCHRemote.exe /EXPORT
```

---

## Inicialización de Forecast Revisions

Todos estos comandos copian datos de una serie fuente a una Forecast Revision destino. `CO_IDX_TO` = el índice de la FR (1 = FR1, 2 = FR2, etc.).

### Inicializar FR desde fuente

| Comando | Fuente → Destino |
|---|---|
| `/INIT_CO N /INIT_FROM_SO99_FRC` | SO99 Statistical Forecast → FR N |
| `/INIT_CO N /INIT_FROM_SO99_CO` | SO99 Customer Orders → FR N |
| `/INIT_CO N /INIT_FROM_WEB_CO M` | FR M → FR N |
| `/INIT_CO N /INIT_FROM_BUDGET` | Budget → FR N |
| `/INIT_CO N /INIT_FROM_DS M` | Display Serie M → FR N |

### Inicializar Budget desde fuente

| Comando | Fuente → Budget |
|---|---|
| `/INIT_BUDGET /INIT_FROM_SO99_FRC` | SO99 Statistical Forecast → Budget |
| `/INIT_BUDGET /INIT_FROM_SO99_CO` | SO99 Customer Orders → Budget |
| `/INIT_BUDGET /INIT_FROM_WEB_CO M` | FR M → Budget |
| `/INIT_BUDGET /INIT_FROM_DS M` | Display Serie M → Budget |

### Refrescar tabla de forecast

```cmd
DCHRemote.exe /REFRESH_SO99_FORECAST
```

Actualiza la tabla interna `Temp_SO99ForecastWeekly`/`Monthly` con los últimos datos de SO99+.

### Ejemplos

```cmd
REM Inicializar FR1 desde SO99 Statistical Forecast
DCHRemote.exe /INIT_CO 1 /INIT_FROM_SO99_FRC

REM Inicializar FR2 desde FR1 (encadenado)
DCHRemote.exe /INIT_CO 2 /INIT_FROM_WEB_CO 1

REM Inicializar Budget desde FR3
DCHRemote.exe /INIT_BUDGET /INIT_FROM_WEB_CO 3
```

---

## Custom Procedures (SQL)

### `/EXECUTESQL [PROCEDURE_ID]`

Ejecuta un Custom Procedure registrado en `SYSTEM_CustomProcedure`. El procedure puede ser de tipo:

- **`tsql`** (`Source = 0`): ejecuta el TSQL almacenado en el campo `TSQL`
- **`sqlScript`** (`Source = 1`): lee y ejecuta el fichero `.sql` en la ruta `ScriptPath`
- **`externalProcess`** (`Source = 2`): lanza el ejecutable en `ProcessPath`

```cmd
DCHRemote.exe /EXECUTESQL TSQL1
DCHRemote.exe /EXECUTESQL SETUP_FR_PARALLEL
DCHRemote.exe /EXECUTESQL FREEZE_ALL_WRITE
```

> ⚠️ El servidor DCH debe tener acceso de lectura a la ruta especificada en `ScriptPath`.

---

## Approval Workflow

> Solo tienen efecto si `APPROVAL_WORKFLOW_ENABLED = 1`.

### `/SIGN_OFF_USER [USER_NAME]`

Fuerza el Sign-Off de un usuario específico.

```cmd
DCHRemote.exe /SIGN_OFF_USER system
DCHRemote.exe /SIGN_OFF_USER user1a
```

### `/SIGN_OFF_USER_LEVEL [USER_LEVEL]`

Fuerza el Sign-Off de **todos** los usuarios de un nivel jerárquico.

```cmd
DCHRemote.exe /SIGN_OFF_USER_LEVEL 1
```

### `/END_APPROVAL_WORKFLOW`

Finaliza el ciclo de aprobación actual y crea uno nuevo. Todos los usuarios vuelven a su estado inicial.

```cmd
DCHRemote.exe /END_APPROVAL_WORKFLOW
```

### `/CHECK_AUTOMATIC_SIGN_OFF`

Ejecuta el Sign-Off automático para usuarios que hayan superado su fecha límite.

```cmd
DCHRemote.exe /CHECK_AUTOMATIC_SIGN_OFF
```

---

## Gestión de usuarios

### `/USER_FRC_WRITE_ENABLE [USER_NAME]`

Concede permisos de **escritura** en Forecast Editing a un usuario.

```cmd
DCHRemote.exe /USER_FRC_WRITE_ENABLE system
DCHRemote.exe /USER_FRC_WRITE_ENABLE user1a
```

> Modifica `CONFIG_UserFunction`: `FunctionName = 'ForecastEditing'`, `WritePermission = 1`.

### `/USER_FRC_WRITE_DISABLE [USER_NAME]`

Revoca permisos de **escritura** en Forecast Editing a un usuario (mantiene lectura).

```cmd
DCHRemote.exe /USER_FRC_WRITE_DISABLE system
```

### `/USER_INTERNAL_IMPORT [FILE_NAME]`

Importa usuarios internos desde un fichero CSV.

```cmd
DCHRemote.exe /USER_INTERNAL_IMPORT c:\dchImport\internalUsers.csv
```

### `/USER_EXTERNAL_IMPORT [FILE_NAME]`

Importa usuarios externos (Windows Auth) desde un fichero CSV.

```cmd
DCHRemote.exe /USER_EXTERNAL_IMPORT c:\dchImport\externalUsers.csv
```

---

## Alerts

### `/RUN_ALERT`

Recalcula **todas** las alerts configuradas en la tabla `Alerts`.

```cmd
DCHRemote.exe /RUN_ALERT
```

### `/RUN_ALERT [ALERT_ID1-ALERT_ID2-...]`

Recalcula solo las alerts especificadas por sus IDs.

```cmd
DCHRemote.exe /RUN_ALERT 1-3-7
```

---

## Mantenimiento

### `/CLEAR_CACHE`

Limpia la caché de DCH, forzando la recarga de configuración y permisos. **Imprescindible** tras modificar `CONFIG_UserFunction`, `CONFIG_ParamGen` o cualquier tabla de configuración por SQL directo.

```cmd
DCHRemote.exe /CLEAR_CACHE
```

### `/SET_FROZEN_PERIOD [FR] [FROZEN_PERIODS] [EDITABLE_PERIODS]`

Configura los frozen periods de una Forecast Revision.

```cmd
REM FR2: 3 periodos congelados, 5 periodos editables
DCHRemote.exe /SET_FROZEN_PERIOD 2 3 5
```

### `/SEND_EMAIL [TO] [SUBJECT] [BODY]`

Envía un email desde DCH.

```cmd
DCHRemote.exe /SEND_EMAIL username "DCH Data Imported" "All files have been imported successfully"
```

### `/ENCRYPT`

Encripta el fichero de configuración de DCHRemote.

```cmd
DCHRemote.exe /ENCRYPT
```

### `/DECRYPT`

Desencripta el fichero de configuración de DCHRemote.

```cmd
DCHRemote.exe /DECRYPT
```

### `/TEST`

Verifica la conexión entre DCHRemote y el servidor DCH.

```cmd
DCHRemote.exe /TEST
```

---

> **Documento versión**: 1.0  
> **Fecha**: 2026-08-05  
> **Ámbito**: DCH 440