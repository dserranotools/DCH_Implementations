| [Workflow](DCH_MultiFR_Parallel_Workflow_1_Main_en.md) | 📄 Scripts | [DCH Remote](DCHRemote_Command_Reference_en.md) |
|:---:|:---:|:---:|

&nbsp;

# DCH Multi-FR — Implementation Scripts

**Client:** Dr. Schaer  
**Version:** 1.0  
**Date:** 2026-08-05  
**Scope:** DCH 440 — Weekly Mode  
**Related documents:** [DCH_MultiFR_Parallel_Workflow.md](./DCH_MultiFR_Parallel_Workflow_1_Main_en.md)

---

## User management in the scripts

### How DCH manages users

DCH supports two types of users stored in separate tables:

| Type | Table | Authentication |
|---|---|---|
| **Internal** | `AspNetUsers` | Identity Framework (username/password) |
| **External** | `User_Windows` | SSO / SAML / Windows Auth |

Both types share the same permissions table: **`CONFIG_UserFunction`**.

### Using `@UseAutoDetectUsers`

The `1_SETUP_FR_PARALLEL` and `4_SETUP_FR_CONSOLIDATE` scripts include a flag:

```sql
DECLARE @UseAutoDetectUsers INT = 1
```

**`@UseAutoDetectUsers = 1` (recommended, default value):**

- Automatically detects all users who already have the `ForecastEditing` permission in `CONFIG_UserFunction`
- Queries both `AspNetUsers` and `User_Windows`
- **Advantage**: if new users are added to DCH, they will automatically be included in the next cycle
- No need to maintain manual lists

**`@UseAutoDetectUsers = 0`:**

- Uses the manual list defined in `@UserList`
- Useful for testing or when a specific subset of users is desired

### ⚠️ Warning: new users mid-phase

If a new user is added to DCH **mid-phase** (e.g., during parallel editing), this user will **NOT have the permissions applied automatically**. In that case, manually run the script from the DCH UI:

1. Go to `Menu > Admin > Custom Procedures`
2. Locate the corresponding script (e.g., `1_SETUP_FR_PARALLEL`)
3. Click the **`Run`** button on that row
4. Verify the result in `Menu > Admin > Custom Procedure Log`

---

## SQL scripts and batch commands to copy directly

---

## .sql files (`D:\DCH\Scripts\` folder)

### `1_SETUP_FR_PARALLEL.sql`

Assigns global ForecastEditing and per-FR LineForecastRevision permissions to users. Runs in **PHASE 1**.

```sql
-- ============================================
-- 1_SETUP_FR_PARALLEL
-- Assigns ForecastEditing + LineForecastRevision permissions
-- per user and Forecast Revision.
--
-- CONFIGURE:
--   @UseAutoDetectUsers: 1 = auto (users with ForecastEditing)
--                        0 = use manual list (@UserList)
--   @UserList (if @UseAutoDetectUsers = 0): 'user1,user2,...'
--   @FrcRevList: '1,2,3,4,5'
-- ============================================

SET NOCOUNT ON

DECLARE @UseAutoDetectUsers INT = 1
DECLARE @UserList NVARCHAR(MAX) = N''
DECLARE @FrcRevList NVARCHAR(MAX) = N'1,2,3,4,5'

-- Resolve user list
IF @UseAutoDetectUsers = 1
BEGIN
    -- Automatically detect all users with ForecastEditing
    -- (internal in AspNetUsers + external in User_Windows)
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

-- If the list is empty, do nothing
IF @UserList = '' OR @UserList IS NULL
BEGIN
    PRINT 'WARNING: No users found. Check @UseAutoDetectUsers or @UserList.'
    RETURN
END

-- 1. Global ForecastEditing (Read=1, Write=1)
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

-- 2. LineForecastRevision (Read=1, Write=1) for each user x FR
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

-- 3. Clean up permissions for FRs no longer in the list
DELETE FROM CONFIG_UserFunction
WHERE FunctionName = 'LineForecastRevision'
  AND UserName IN (SELECT value FROM STRING_SPLIT(@UserList, ','))
  AND FunctionId NOT IN (SELECT value FROM STRING_SPLIT(@FrcRevList, ','))
  AND FunctionId <> '-'

PRINT '1_SETUP_FR_PARALLEL completed.'
```

---

### `2_FREEZE_ALL_WRITE.sql`

Removes write permissions from **all** users. Keeps read access. Runs in **PHASE 2** and **PHASE 4**.

```sql
-- ============================================
-- 2_FREEZE_ALL_WRITE
-- Removes write access from ALL users.
-- Keeps read access so they can continue viewing.
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

Restores write permissions to users who already had `ReadPermission = 1`. Runs in **PHASE 1** (after assigning permissions) and **PHASE 3** (after setting up reviewers).

```sql
-- ============================================
-- 3_UNFREEZE_ALL_WRITE
-- Restores write access to those who already had Read=1.
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

Leaves only FR6 editable for reviewers. All other users lose write access on all FRs. Runs in **PHASE 3**.

```sql
-- ============================================
-- 4_SETUP_FR_CONSOLIDATE
-- Only reviewers edit the consolidated FR (FR6).
-- All other users: read-only.
--
-- CONFIGURE:
--   @UseAutoDetectReviewers: 1 = auto (all users with ForecastEditing)
--                            0 = use manual list (@ReviewerList)
--   @ReviewerList (if @UseAutoDetectReviewers = 0): 'reviewer1,reviewer2'
--   @ReadOnlyFrcRevList: '1,2,3,4,5'
--   @ConsolidatedFR: 6
-- ============================================

SET NOCOUNT ON

DECLARE @UseAutoDetectReviewers INT = 0
DECLARE @ReviewerList NVARCHAR(MAX) = N'reviewer1,reviewer2'
DECLARE @ReadOnlyFrcRevList NVARCHAR(MAX) = N'1,2,3,4,5'
DECLARE @ConsolidatedFR INT = 6

-- Resolve reviewer list (if auto-detection)
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

-- 1. Remove Write from ALL on all FRs
UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName = 'LineForecastRevision'

-- 2. Remove global Write from ALL
UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName = 'ForecastEditing'

-- 3. Global Write only to reviewers
UPDATE CONFIG_UserFunction SET WritePermission = 1
WHERE FunctionName = 'ForecastEditing'
  AND UserName IN (SELECT value FROM STRING_SPLIT(@ReviewerList, ','))

-- 4. Write on consolidated FR only for reviewers
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

-- 5. Read=1 on FRs 1-5 for reviewers (so they can see source data)
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

### `5_CONSOLIDATE_FR6.sql` (template)

This script must be **customized according to the consolidation logic** the client needs. The template assumes each FR is stored in `WebCO_ForecastWeekly` with a different `COTypeId`.

```sql
-- ============================================
-- 5_CONSOLIDATE_FR6
-- Consolidates edits from FR1..FR5 into FR6.
--
-- ADAPT the consolidation logic as needed:
--   - Sum of quantities
--   - Average
--   - Maximum
--   - Specific business rule
-- ============================================

SET NOCOUNT ON

DECLARE @FrSourceList NVARCHAR(MAX) = N'4,5,6,7,8'  -- COTypeId for FR1..FR5
DECLARE @FrTarget INT = 9                             -- COTypeId for FR6
DECLARE @YearFrom INT, @YearTo INT, @WeekFrom INT, @WeekTo INT

-- Adjust to the configured forecast horizon
SELECT @YearFrom = MIN(Year), @YearTo = MAX(Year)
FROM WebCO_ForecastWeekly
WHERE COTypeId IN (SELECT value FROM STRING_SPLIT(@FrSourceList, ','))

-- ============================================
-- EXAMPLE: Sum of FR1..FR5 -> FR6
-- Replace with actual client logic
-- ============================================

-- First, zero out FR6 in the active horizon
UPDATE WebCO_ForecastWeekly
SET FrcQty = 0,
    EditedFlag = 0,
    EditedDate = NULL,
    EditedByUser = NULL
WHERE COTypeId = @FrTarget

-- Consolidate: sum of all source FRs
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

> ⚠️ **IMPORTANT**: The `COTypeId` of each FR corresponds to `ForecastRevisionsEnum`:
> - FR1 = 4
> - FR2 = 5
> - FR3 = 6
> - FR4 = 7
> - FR5 = 8
> - FR6 = 9
>
> Verify in `WebCO_ForecastWeekly` which actual `COTypeId` values are being used.

---

## .cmd scripts (`D:\DCH\Batch\` folder)

### `PHASE1_Init.cmd`

> **Prerequisite**: Configure in the DCH UI: **Import settings > Forecast and Demand > Initialize Forecast Revisions after Forecast Import** = `SO99F-FR1;SO99F-FR2;SO99F-FR3;SO99F-FR4;SO99F-FR5;SO99F-FR6`

```cmd
@echo off
echo ============================================
echo PHASE 1: Import SO99+ and prepare editing
echo ============================================

echo.
echo [1/4] Importing data from SO99+ (includes FR1..FR6 init)...
DCHRemote.exe /IMPORT

echo.
echo [2/4] Assigning permissions per user and FR...
DCHRemote.exe /EXECUTESQL 1_SETUP_FR_PARALLEL

echo.
echo [3/4] Enabling write access for all users...
DCHRemote.exe /EXECUTESQL 3_UNFREEZE_ALL_WRITE

echo.
echo [4/4] Clearing DCH cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo ============================================
echo PHASE 1 COMPLETED - Users can edit
echo ============================================
```

### `PHASE2_Freeze.cmd`

```cmd
@echo off
echo ============================================
echo PHASE 2: Freeze editing and consolidate
echo ============================================

echo.
echo [1/3] Freezing write access for all users...
DCHRemote.exe /EXECUTESQL 2_FREEZE_ALL_WRITE

echo.
echo [2/3] Clearing cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo [3/3] Consolidating FR1..FR5 into FR6...
DCHRemote.exe /EXECUTESQL 5_CONSOLIDATE_FR6

echo.
echo ============================================
echo PHASE 2 COMPLETED - Data consolidated in FR6
echo ============================================
```

### `PHASE3_Review.cmd`

```cmd
@echo off
echo ============================================
echo PHASE 3: Enable FR6 review
echo ============================================

echo.
echo [1/3] Configuring review permissions...
DCHRemote.exe /EXECUTESQL 4_SETUP_FR_CONSOLIDATE

echo.
echo [2/3] Enabling write access for reviewers...
DCHRemote.exe /EXECUTESQL 3_UNFREEZE_ALL_WRITE

echo.
echo [3/3] Clearing cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo ============================================
echo PHASE 3 COMPLETED - Reviewers can edit FR6
echo ============================================
```

### `PHASE4_Export.cmd`

```cmd
@echo off
echo ============================================
echo PHASE 4: Export and prepare next cycle
echo ============================================

echo.
echo [1/3] Freezing write access...
DCHRemote.exe /EXECUTESQL 2_FREEZE_ALL_WRITE

echo.
echo [2/3] Clearing cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo [3/3] Exporting data to SO99+...
DCHRemote.exe /EXPORT

echo.
echo ============================================
echo PHASE 4 COMPLETED - Start PHASE 1 for next cycle
echo ============================================
```

---

## Registration SQL in `SYSTEM_CustomProcedure`

Run **once** in the DCH database:

```sql
-- Clean up previous procedures (if they exist)
DELETE FROM SYSTEM_CustomProcedure WHERE CustomProcedureId IN (
    '1_SETUP_FR_PARALLEL', '2_FREEZE_ALL_WRITE', '3_UNFREEZE_ALL_WRITE', 
    '4_SETUP_FR_CONSOLIDATE', '5_CONSOLIDATE_FR6'
)

-- Register the new procedures (Source = 1 = sqlScript)
INSERT INTO SYSTEM_CustomProcedure (CustomProcedureId, Descr, Source, tsql, scriptPath, processPath)
VALUES 
('1_SETUP_FR_PARALLEL',    'Setup FR parallel: user permissions per FR',           1, '', 'D:\DCH\Scripts\1_SETUP_FR_PARALLEL.sql',    ''),
('2_FREEZE_ALL_WRITE',     'Freeze write access for all users',                    1, '', 'D:\DCH\Scripts\2_FREEZE_ALL_WRITE.sql',     ''),
('3_UNFREEZE_ALL_WRITE',   'Unfreeze write access for all users',                 1, '', 'D:\DCH\Scripts\3_UNFREEZE_ALL_WRITE.sql',   ''),
('4_SETUP_FR_CONSOLIDATE', 'Setup final review: only FR6 editable for reviewers', 1, '', 'D:\DCH\Scripts\4_SETUP_FR_CONSOLIDATE.sql', ''),
('5_CONSOLIDATE_FR6',      'Consolidate FR1..FR5 into FR6',                       1, '', 'D:\DCH\Scripts\5_CONSOLIDATE_FR6.sql',     '')
```

---

## Post-implementation verification SQL

```sql
-- Verify that Custom Procedures are registered
SELECT CustomProcedureId, Descr, Source, scriptPath 
FROM SYSTEM_CustomProcedure 
WHERE CustomProcedureId LIKE '1_SETUP_FR%' 
   OR CustomProcedureId LIKE '2_FREEZE%' 
   OR CustomProcedureId LIKE '3_UNFREEZE%'
   OR CustomProcedureId LIKE '4_SETUP_FR%'
   OR CustomProcedureId = '5_CONSOLIDATE_FR6'
ORDER BY CustomProcedureId

-- Check permission status
SELECT UserName, FunctionName, FunctionId, 
       CASE ReadPermission WHEN 1 THEN 'R' ELSE '-' END + 
       CASE WritePermission WHEN 1 THEN 'W' ELSE '-' END AS Perms
FROM CONFIG_UserFunction
WHERE FunctionName IN ('ForecastEditing', 'LineForecastRevision')
ORDER BY UserName, FunctionName, CAST(FunctionId AS INT)
```

---

> **Document version**: 1.0  
> **Date**: 2026-08-05  
> **Scope**: DCH 440