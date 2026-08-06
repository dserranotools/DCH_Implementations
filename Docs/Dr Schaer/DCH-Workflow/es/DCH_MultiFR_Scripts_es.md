# DCH Multi-FR — Scripts de Implementación

**Cliente:** Dr. Schaer  
**Versión:** 1.0  
**Fecha:** 2026-08-05  
**Ámbito:** DCH 440 — Modo Weekly  
**Documentos relacionados:** [DCH_MultiFR_Parallel_Workflow.md](./DCH_MultiFR_Parallel_Workflow_1_Main_es.md)

---

## Gestión de usuarios en los scripts

### Cómo gestiona DCH los usuarios

DCH soporta dos tipos de usuarios almacenados en tablas distintas:

| Tipo | Tabla | Autenticación |
|---|---|---|
| **Internos** | `AspNetUsers` | Identity Framework (usuario/contraseña) |
| **Externos** | `User_Windows` | SSO / SAML / Windows Auth |

Ambos tipos comparten la misma tabla de permisos: **`CONFIG_UserFunction`**.

### Uso de `@UseAutoDetectUsers`

Los scripts `1_SETUP_FR_PARALLEL` y `4_SETUP_FR_CONSOLIDATE` incluyen un flag:

```sql
DECLARE @UseAutoDetectUsers INT = 1
```

**`@UseAutoDetectUsers = 1` (recomendado, valor por defecto):**

- Detecta automáticamente todos los usuarios que ya tienen el permiso `ForecastEditing` en `CONFIG_UserFunction`
- Consulta tanto `AspNetUsers` como `User_Windows`
- **Ventaja**: si se añaden nuevos usuarios a DCH, automáticamente se incluirán en el siguiente ciclo
- No es necesario mantener listas manuales

**`@UseAutoDetectUsers = 0`:**

- Usa la lista manual definida en `@UserList`
- Útil para pruebas o cuando se quiere un subconjunto específico de usuarios

### ⚠️ Advertencia: nuevos usuarios en mitad de una fase

Si se añade un nuevo usuario a DCH **en mitad de una fase** (ej: durante la edición paralela), este usuario **NO tendrá los permisos aplicados automáticamente**. En ese caso, ejecutar manualmente el script desde la UI de DCH:

1. Ir a `Menu > Admin > Custom Procedures`
2. Localizar el script correspondiente (ej: `1_SETUP_FR_PARALLEL`)
3. Hacer clic en el botón **`Run`** de esa fila
4. Verificar el resultado en `Menu > Admin > Custom Procedure Log`

---

## Scripts SQL y comandos batch para copiar directamente

---

## Ficheros .sql (carpeta `D:\DCH\Scripts\`)

### `1_SETUP_FR_PARALLEL.sql`

Asigna permisos de ForecastEditing global y LineForecastRevision por FR a los usuarios. Se ejecuta en **FASE 1**.

```sql
-- ============================================
-- 1_SETUP_FR_PARALLEL
-- Asigna permisos ForecastEditing + LineForecastRevision
-- por usuario y Forecast Revision.
--
-- CONFIGURAR:
--   @UseAutoDetectUsers: 1 = auto (usuarios con ForecastEditing)
--                        0 = usar lista manual (@UserList)
--   @UserList (si @UseAutoDetectUsers = 0): 'user1,user2,...'
--   @FrcRevList: '1,2,3,4,5'
-- ============================================

SET NOCOUNT ON

DECLARE @UseAutoDetectUsers INT = 1
DECLARE @UserList NVARCHAR(MAX) = N''
DECLARE @FrcRevList NVARCHAR(MAX) = N'1,2,3,4,5'

-- Resolver lista de usuarios
IF @UseAutoDetectUsers = 1
BEGIN
    -- Detectar automáticamente todos los usuarios con ForecastEditing
    -- (internos en AspNetUsers + externos en User_Windows)
    SELECT @UserList = STRING_AGG(UserName, ',') WITHIN GROUP (ORDER BY UserName)
    FROM (
        SELECT DISTINCT cf.UserName
        FROM CONFIG_UserFunction cf
        INNER JOIN AspNetUsers u ON u.UserName = cf.UserName
        WHERE cf.FunctionName = 'ForecastEditing'

        UNION

        SELECT DISTINCT cf.UserName
        FROM CONFIG_UserFunction cf
        INNER JOIN User_Windows u ON u.UserName = cf.UserName
        WHERE cf.FunctionName = 'ForecastEditing'
    ) allUsers

    PRINT 'Auto-detected users: ' + ISNULL(@UserList, '(none)')
END

-- Si la lista está vacía, no hacer nada
IF @UserList = '' OR @UserList IS NULL
BEGIN
    PRINT 'WARNING: No users found. Check @UseAutoDetectUsers or @UserList.'
    RETURN
END

-- 1. ForecastEditing global (Read=1, Write=1)
MERGE CONFIG_UserFunction AS tgt
USING (
    SELECT value AS UserName 
    FROM STRING_SPLIT(@UserList, ',')
) AS src
    ON tgt.UserName = src.UserName 
    AND tgt.FunctionName = 'ForecastEditing'
    AND tgt.FunctionId = '-'
WHEN MATCHED THEN
    UPDATE SET ReadPermission = 1, WritePermission = 1
WHEN NOT MATCHED THEN
    INSERT (UserName, FunctionName, FunctionId, ReadPermission, WritePermission)
    VALUES (src.UserName, 'ForecastEditing', '-', 1, 1);

-- 2. LineForecastRevision (Read=1, Write=1) para cada usuario x FR
MERGE CONFIG_UserFunction AS tgt
USING (
    SELECT u.value AS UserName, f.value AS FunctionId
    FROM STRING_SPLIT(@UserList, ',') u
    CROSS JOIN STRING_SPLIT(@FrcRevList, ',') f
) AS src
    ON tgt.UserName = src.UserName 
    AND tgt.FunctionName = 'LineForecastRevision'
    AND tgt.FunctionId = src.FunctionId
WHEN MATCHED THEN
    UPDATE SET ReadPermission = 1, WritePermission = 1
WHEN NOT MATCHED THEN
    INSERT (UserName, FunctionName, FunctionId, ReadPermission, WritePermission)
    VALUES (src.UserName, 'LineForecastRevision', src.FunctionId, 1, 1);

-- 3. Limpiar permisos de FRs que ya no están en la lista
DELETE FROM CONFIG_UserFunction
WHERE FunctionName = 'LineForecastRevision'
  AND UserName IN (SELECT value FROM STRING_SPLIT(@UserList, ','))
  AND FunctionId NOT IN (SELECT value FROM STRING_SPLIT(@FrcRevList, ','))
  AND FunctionId <> '-'

PRINT '1_SETUP_FR_PARALLEL completed.'
```

---

### `2_FREEZE_ALL_WRITE.sql`

Quita permisos de escritura a **todos** los usuarios. Mantiene lectura. Se ejecuta en **FASE 2** y **FASE 4**.

```sql
-- ============================================
-- 2_FREEZE_ALL_WRITE
-- Quita escritura a TODOS los usuarios.
-- Mantiene lectura para que puedan seguir viendo.
-- ============================================

SET NOCOUNT ON

UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName = 'ForecastEditing'

UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName = 'LineForecastRevision'

UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName IN ('ForecastAnalysisSO99', 'ForecastAnalysisDCH')

PRINT '2_FREEZE_ALL_WRITE completed.'
```

---

### `3_UNFREEZE_ALL_WRITE.sql`

Devuelve permisos de escritura a usuarios que ya tenían `ReadPermission = 1`. Se ejecuta en **FASE 1** (tras asignar permisos) y **FASE 3** (tras configurar revisores).

```sql
-- ============================================
-- 3_UNFREEZE_ALL_WRITE
-- Devuelve escritura a quienes ya tenían Read=1.
-- ============================================

SET NOCOUNT ON

UPDATE CONFIG_UserFunction SET WritePermission = 1
WHERE FunctionName = 'ForecastEditing' AND ReadPermission = 1

UPDATE CONFIG_UserFunction SET WritePermission = 1
WHERE FunctionName = 'LineForecastRevision' AND ReadPermission = 1

UPDATE CONFIG_UserFunction SET WritePermission = 1
WHERE FunctionName IN ('ForecastAnalysisSO99', 'ForecastAnalysisDCH') AND ReadPermission = 1

PRINT '3_UNFREEZE_ALL_WRITE completed.'
```

---

### `4_SETUP_FR_CONSOLIDATE.sql`

Deja solo FR6 editable para los revisores. El resto de usuarios pierden escritura en todas las FRs. Se ejecuta en **FASE 3**.

```sql
-- ============================================
-- 4_SETUP_FR_CONSOLIDATE
-- Solo revisores editan la FR consolidada (FR6).
-- El resto de usuarios: solo lectura.
--
-- CONFIGURAR:
--   @UseAutoDetectReviewers: 1 = auto (todos los usuarios con ForecastEditing)
--                            0 = usar lista manual (@ReviewerList)
--   @ReviewerList (si @UseAutoDetectReviewers = 0): 'revisor1,revisor2'
--   @ReadOnlyFrcRevList: '1,2,3,4,5'
--   @ConsolidatedFR: 6
-- ============================================

SET NOCOUNT ON

DECLARE @UseAutoDetectReviewers INT = 0
DECLARE @ReviewerList NVARCHAR(MAX) = N'revisor1,revisor2'
DECLARE @ReadOnlyFrcRevList NVARCHAR(MAX) = N'1,2,3,4,5'
DECLARE @ConsolidatedFR INT = 6

-- Resolver lista de revisores (si auto-detección)
IF @UseAutoDetectReviewers = 1
BEGIN
    SELECT @ReviewerList = STRING_AGG(UserName, ',') WITHIN GROUP (ORDER BY UserName)
    FROM (
        SELECT DISTINCT cf.UserName
        FROM CONFIG_UserFunction cf
        INNER JOIN AspNetUsers u ON u.UserName = cf.UserName
        WHERE cf.FunctionName = 'ForecastEditing'

        UNION

        SELECT DISTINCT cf.UserName
        FROM CONFIG_UserFunction cf
        INNER JOIN User_Windows u ON u.UserName = cf.UserName
        WHERE cf.FunctionName = 'ForecastEditing'
    ) allUsers

    PRINT 'Auto-detected reviewers: ' + ISNULL(@ReviewerList, '(none)')
END

-- 1. Quitar Write a TODOS en todas las FRs
UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName = 'LineForecastRevision'

-- 2. Quitar Write global a TODOS
UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName = 'ForecastEditing'

-- 3. Write global solo a revisores
UPDATE CONFIG_UserFunction SET WritePermission = 1
WHERE FunctionName = 'ForecastEditing'
  AND UserName IN (SELECT value FROM STRING_SPLIT(@ReviewerList, ','))

-- 4. Write en FR consolidada solo para revisores
MERGE CONFIG_UserFunction AS tgt
USING (
    SELECT value AS UserName
    FROM STRING_SPLIT(@ReviewerList, ',')
) AS src
    ON tgt.UserName = src.UserName 
    AND tgt.FunctionName = 'LineForecastRevision'
    AND tgt.FunctionId = CAST(@ConsolidatedFR AS VARCHAR(32))
WHEN MATCHED THEN
    UPDATE SET ReadPermission = 1, WritePermission = 1
WHEN NOT MATCHED THEN
    INSERT (UserName, FunctionName, FunctionId, ReadPermission, WritePermission)
    VALUES (src.UserName, 'LineForecastRevision', CAST(@ConsolidatedFR AS VARCHAR(32)), 1, 1);

-- 5. Read=1 en FRs 1-5 para revisores (para que vean los datos fuente)
MERGE CONFIG_UserFunction AS tgt
USING (
    SELECT r.value AS UserName, f.value AS FunctionId
    FROM STRING_SPLIT(@ReviewerList, ',') r
    CROSS JOIN STRING_SPLIT(@ReadOnlyFrcRevList, ',') f
) AS src
    ON tgt.UserName = src.UserName 
    AND tgt.FunctionName = 'LineForecastRevision'
    AND tgt.FunctionId = src.FunctionId
WHEN MATCHED THEN
    UPDATE SET ReadPermission = 1, WritePermission = 0
WHEN NOT MATCHED THEN
    INSERT (UserName, FunctionName, FunctionId, ReadPermission, WritePermission)
    VALUES (src.UserName, 'LineForecastRevision', src.FunctionId, 1, 0);

PRINT '4_SETUP_FR_CONSOLIDATE completed.'
```

---

### `5_CONSOLIDATE_FR6.sql` (plantilla)

Este script debe **personalizarse según la lógica de consolidación** que necesite el cliente. La plantilla asume que cada FR se almacena en `WebCO_ForecastWeekly` con un `COTypeId` diferente.

```sql
-- ============================================
-- 5_CONSOLIDATE_FR6
-- Consolida ediciones de FR1..FR5 en FR6.
--
-- ADAPTAR la lógica de consolidación según necesidad:
--   - Suma de cantidades
--   - Promedio
--   - Máximo
--   - Regla de negocio específica
-- ============================================

SET NOCOUNT ON

DECLARE @FrSourceList NVARCHAR(MAX) = N'4,5,6,7,8'  -- COTypeId de FR1..FR5
DECLARE @FrTarget INT = 9                             -- COTypeId de FR6
DECLARE @YearFrom INT, @YearTo INT, @WeekFrom INT, @WeekTo INT

-- Ajustar al horizonte de forecast configurado
SELECT @YearFrom = MIN(Year), @YearTo = MAX(Year)
FROM WebCO_ForecastWeekly
WHERE COTypeId IN (SELECT value FROM STRING_SPLIT(@FrSourceList, ','))

-- ============================================
-- EJEMPLO: Suma de FR1..FR5 -> FR6
-- Reemplazar con la lógica real del cliente
-- ============================================

-- Primero, poner FR6 a cero en el horizonte activo
UPDATE WebCO_ForecastWeekly
SET FrcQty = 0,
    EditedFlag = 0,
    EditedDate = NULL,
    EditedByUser = NULL
WHERE COTypeId = @FrTarget

-- Consolidar: suma de todas las FRs fuente
MERGE WebCO_ForecastWeekly AS tgt
USING (
    SELECT 
        COProductId,
        COMarketId,
        Year,
        Week,
        SUM(FrcQty) AS FrcQty
    FROM WebCO_ForecastWeekly
    WHERE COTypeId IN (SELECT value FROM STRING_SPLIT(@FrSourceList, ','))
    GROUP BY COProductId, COMarketId, Year, Week
) AS src
    ON tgt.COProductId = src.COProductId
    AND tgt.COMarketId = src.COMarketId
    AND tgt.Year = src.Year
    AND tgt.Week = src.Week
    AND tgt.COTypeId = @FrTarget
WHEN MATCHED THEN
    UPDATE SET 
        FrcQty = src.FrcQty,
        EditedFlag = 1,
        EditedDate = GETDATE(),
        EditedByUser = 'CONSOLIDATION'

PRINT '5_CONSOLIDATE_FR6 completed. FR1..FR5 consolidated into FR6.'
```

> ⚠️ **IMPORTANTE**: El `COTypeId` de cada FR se corresponde con `ForecastRevisionsEnum`:
> - FR1 = 4
> - FR2 = 5
> - FR3 = 6
> - FR4 = 7
> - FR5 = 8
> - FR6 = 9
>
> Verificar en `WebCO_ForecastWeekly` qué valores reales de `COTypeId` se están usando.

---

## Scripts .cmd (carpeta `D:\DCH\Batch\`)

### `FASE1_Init.cmd`

> **Pre-requisito**: Configurar en la UI de DCH: **Import settings > Forecast and Demand > Initialize Forecast Revisions after Forecast Import** = `SO99F-FR1;SO99F-FR2;SO99F-FR3;SO99F-FR4;SO99F-FR5;SO99F-FR6`

```cmd
@echo off
echo ============================================
echo FASE 1: Importar SO99+ y preparar edicion
echo ============================================

echo.
echo [1/4] Importando datos desde SO99+ (incluye init de FR1..FR6)...
DCHRemote.exe /IMPORT

echo.
echo [2/4] Asignando permisos por usuario y FR...
DCHRemote.exe /EXECUTESQL 1_SETUP_FR_PARALLEL

echo.
echo [3/4] Activando escritura para todos los usuarios...
DCHRemote.exe /EXECUTESQL 3_UNFREEZE_ALL_WRITE

echo.
echo [4/4] Limpiando cache de DCH...
DCHRemote.exe /CLEAR_CACHE

echo.
echo ============================================
echo FASE 1 COMPLETADA - Usuarios pueden editar
echo ============================================
```

### `FASE2_Freeze.cmd`

```cmd
@echo off
echo ============================================
echo FASE 2: Congelar edicion y consolidar
echo ============================================

echo.
echo [1/3] Congelando escritura de todos los usuarios...
DCHRemote.exe /EXECUTESQL 2_FREEZE_ALL_WRITE

echo.
echo [2/3] Limpiando cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo [3/3] Consolidando FR1..FR5 en FR6...
DCHRemote.exe /EXECUTESQL 5_CONSOLIDATE_FR6

echo.
echo ============================================
echo FASE 2 COMPLETADA - Datos consolidados en FR6
echo ============================================
```

### `FASE3_Review.cmd`

```cmd
@echo off
echo ============================================
echo FASE 3: Activar revision FR6
echo ============================================

echo.
echo [1/3] Configurando permisos de revision...
DCHRemote.exe /EXECUTESQL 4_SETUP_FR_CONSOLIDATE

echo.
echo [2/3] Activando escritura para revisores...
DCHRemote.exe /EXECUTESQL 3_UNFREEZE_ALL_WRITE

echo.
echo [3/3] Limpiando cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo ============================================
echo FASE 3 COMPLETADA - Revisores pueden editar FR6
echo ============================================
```

### `FASE4_Export.cmd`

```cmd
@echo off
echo ============================================
echo FASE 4: Exportar y preparar siguiente ciclo
echo ============================================

echo.
echo [1/3] Congelando escritura...
DCHRemote.exe /EXECUTESQL 2_FREEZE_ALL_WRITE

echo.
echo [2/3] Limpiando cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo [3/3] Exportando datos a SO99+...
DCHRemote.exe /EXPORT

echo.
echo ============================================
echo FASE 4 COMPLETADA - Iniciar FASE 1 para siguiente ciclo
echo ============================================
```

---

## SQL de registro en `SYSTEM_CustomProcedure`

Ejecutar **una sola vez** en la base de datos DCH:

```sql
-- Limpiar procedures anteriores (si existen)
DELETE FROM SYSTEM_CustomProcedure WHERE CustomProcedureId IN (
    '1_SETUP_FR_PARALLEL', '2_FREEZE_ALL_WRITE', '3_UNFREEZE_ALL_WRITE', 
    '4_SETUP_FR_CONSOLIDATE', '5_CONSOLIDATE_FR6'
)

-- Registrar los nuevos procedures (Source = 1 = sqlScript)
INSERT INTO SYSTEM_CustomProcedure (CustomProcedureId, Descr, Source, tsql, scriptPath, processPath)
VALUES 
('1_SETUP_FR_PARALLEL',    'Setup FR parallel: permisos usuarios por FR',           1, '', 'D:\DCH\Scripts\1_SETUP_FR_PARALLEL.sql',    ''),
('2_FREEZE_ALL_WRITE',     'Congelar escritura de todos los usuarios',             1, '', 'D:\DCH\Scripts\2_FREEZE_ALL_WRITE.sql',     ''),
('3_UNFREEZE_ALL_WRITE',   'Descongelar escritura de todos los usuarios',          1, '', 'D:\DCH\Scripts\3_UNFREEZE_ALL_WRITE.sql',   ''),
('4_SETUP_FR_CONSOLIDATE', 'Setup revision final: solo FR6 editable para revisores', 1, '', 'D:\DCH\Scripts\4_SETUP_FR_CONSOLIDATE.sql', ''),
('5_CONSOLIDATE_FR6',      'Consolidar FR1..FR5 en FR6',                           1, '', 'D:\DCH\Scripts\5_CONSOLIDATE_FR6.sql',     '')
```

---

## SQL de verificación post-implementación

```sql
-- Verificar que los Custom Procedures están registrados
SELECT CustomProcedureId, Descr, Source, scriptPath 
FROM SYSTEM_CustomProcedure 
WHERE CustomProcedureId LIKE '1_SETUP_FR%' 
   OR CustomProcedureId LIKE '2_FREEZE%' 
   OR CustomProcedureId LIKE '3_UNFREEZE%'
   OR CustomProcedureId LIKE '4_SETUP_FR%'
   OR CustomProcedureId = '5_CONSOLIDATE_FR6'
ORDER BY CustomProcedureId

-- Ver estado de permisos
SELECT UserName, FunctionName, FunctionId, 
       CASE ReadPermission WHEN 1 THEN 'R' ELSE '-' END + 
       CASE WritePermission WHEN 1 THEN 'W' ELSE '-' END AS Perms
FROM CONFIG_UserFunction
WHERE FunctionName IN ('ForecastEditing', 'LineForecastRevision')
ORDER BY UserName, FunctionName, CAST(FunctionId AS INT)
```

---

> **Documento versión**: 1.0  
> **Fecha**: 2026-08-05  
> **Ámbito**: DCH 440