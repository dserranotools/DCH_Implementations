| [Workflow](DCH_MultiFR_Parallel_Workflow_1_Main_it.md) | 📄 Scripts | [DCH Remote](DCHRemote_Command_Reference_it.md) |
|:---:|:---:|:---:|

&nbsp;

# DCH Multi-FR — Script di Implementazione

**Cliente:** Dr. Schaer  
**Versione:** 1.0  
**Data:** 2026-08-05  
**Ambito:** DCH 440 — Modalità Weekly  
**Documenti correlati:** [DCH_MultiFR_Parallel_Workflow.md](./DCH_MultiFR_Parallel_Workflow_1_Main_it.md)

---

## Gestione degli utenti negli script

### Come DCH gestisce gli utenti

DCH supporta due tipi di utenti memorizzati in tabelle distinte:

| Tipo | Tabella | Autenticazione |
|---|---|---|
| **Interni** | `AspNetUsers` | Identity Framework (utente/password) |
| **Esterni** | `User_Windows` | SSO / SAML / Windows Auth |

Entrambi i tipi condividono la stessa tabella dei permessi: **`CONFIG_UserFunction`**.

### Uso di `@UseAutoDetectUsers`

Gli script `1_SETUP_FR_PARALLEL` e `4_SETUP_FR_CONSOLIDATE` includono un flag:

```sql
DECLARE @UseAutoDetectUsers INT = 1
```

**`@UseAutoDetectUsers = 1` (raccomandato, valore predefinito):**

- Rileva automaticamente tutti gli utenti che hanno già il permesso `ForecastEditing` in `CONFIG_UserFunction`
- Interroga sia `AspNetUsers` che `User_Windows`
- **Vantaggio**: se vengono aggiunti nuovi utenti a DCH, saranno automaticamente inclusi nel ciclo successivo
- Non è necessario mantenere elenchi manuali

**`@UseAutoDetectUsers = 0`:**

- Usa l'elenco manuale definito in `@UserList`
- Utile per test o quando si desidera un sottoinsieme specifico di utenti

### ⚠️ Avvertenza: nuovi utenti a metà fase

Se un nuovo utente viene aggiunto a DCH **a metà di una fase** (es: durante la modifica parallela), tale utente **NON avrà i permessi applicati automaticamente**. In tal caso, eseguire manualmente lo script dall'interfaccia DCH:

1. Andare a `Menu > Admin > Custom Procedures`
2. Individuare lo script corrispondente (es: `1_SETUP_FR_PARALLEL`)
3. Fare clic sul pulsante **`Run`** su quella riga
4. Verificare il risultato in `Menu > Admin > Custom Procedure Log`

---

## Script SQL e comandi batch da copiare direttamente

---

## File .sql (cartella `D:\DCH\Scripts\`)

### `1_SETUP_FR_PARALLEL.sql`

Assegna i permessi globali ForecastEditing e LineForecastRevision per FR agli utenti. Viene eseguito nella **FASE 1**.

```sql
-- ============================================
-- 1_SETUP_FR_PARALLEL
-- Assegna permessi ForecastEditing + LineForecastRevision
-- per utente e Forecast Revision.
--
-- CONFIGURARE:
--   @UseAutoDetectUsers: 1 = auto (utenti con ForecastEditing)
--                        0 = usa elenco manuale (@UserList)
--   @UserList (se @UseAutoDetectUsers = 0): 'user1,user2,...'
--   @FrcRevList: '1,2,3,4,5'
-- ============================================

SET NOCOUNT ON

DECLARE @UseAutoDetectUsers INT = 1
DECLARE @UserList NVARCHAR(MAX) = N''
DECLARE @FrcRevList NVARCHAR(MAX) = N'1,2,3,4,5'

-- Risolvi elenco utenti
IF @UseAutoDetectUsers = 1
BEGIN
    -- Rileva automaticamente tutti gli utenti con ForecastEditing
    -- (interni in AspNetUsers + esterni in User_Windows)
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

-- Se l'elenco è vuoto, non fare nulla
IF @UserList = '' OR @UserList IS NULL
BEGIN
    PRINT 'WARNING: No users found. Check @UseAutoDetectUsers or @UserList.'
    RETURN
END

-- 1. ForecastEditing globale (Read=1, Write=1)
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

-- 2. LineForecastRevision (Read=1, Write=1) per ogni utente x FR
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

-- 3. Pulisci permessi per FR non più nell'elenco
DELETE FROM CONFIG_UserFunction
WHERE FunctionName = 'LineForecastRevision'
  AND UserName IN (SELECT value FROM STRING_SPLIT(@UserList, ','))
  AND FunctionId NOT IN (SELECT value FROM STRING_SPLIT(@FrcRevList, ','))
  AND FunctionId <> '-'

PRINT '1_SETUP_FR_PARALLEL completed.'
```

---

### `2_FREEZE_ALL_WRITE.sql`

Rimuove i permessi di scrittura a **tutti** gli utenti. Mantiene la lettura. Viene eseguito nella **FASE 2** e **FASE 4**.

```sql
-- ============================================
-- 2_FREEZE_ALL_WRITE
-- Rimuove scrittura a TUTTI gli utenti.
-- Mantiene lettura per consentire la visualizzazione.
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

Ripristina i permessi di scrittura agli utenti che avevano già `ReadPermission = 1`. Viene eseguito nella **FASE 1** (dopo aver assegnato i permessi) e **FASE 3** (dopo aver configurato i revisori).

```sql
-- ============================================
-- 3_UNFREEZE_ALL_WRITE
-- Ripristina scrittura a chi aveva già Read=1.
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

Lascia solo FR6 modificabile per i revisori. Tutti gli altri utenti perdono la scrittura su tutte le FR. Viene eseguito nella **FASE 3**.

```sql
-- ============================================
-- 4_SETUP_FR_CONSOLIDATE
-- Solo i revisori modificano la FR consolidata (FR6).
-- Tutti gli altri utenti: sola lettura.
--
-- CONFIGURARE:
--   @UseAutoDetectReviewers: 1 = auto (tutti gli utenti con ForecastEditing)
--                            0 = usa elenco manuale (@ReviewerList)
--   @ReviewerList (se @UseAutoDetectReviewers = 0): 'revisore1,revisore2'
--   @ReadOnlyFrcRevList: '1,2,3,4,5'
--   @ConsolidatedFR: 6
-- ============================================

SET NOCOUNT ON

DECLARE @UseAutoDetectReviewers INT = 0
DECLARE @ReviewerList NVARCHAR(MAX) = N'revisore1,revisore2'
DECLARE @ReadOnlyFrcRevList NVARCHAR(MAX) = N'1,2,3,4,5'
DECLARE @ConsolidatedFR INT = 6

-- Risolvi elenco revisori (se rilevamento automatico)
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

-- 1. Rimuovi Write a TUTTI su tutte le FR
UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName = 'LineForecastRevision'

-- 2. Rimuovi Write globale a TUTTI
UPDATE CONFIG_UserFunction SET WritePermission = 0
WHERE FunctionName = 'ForecastEditing'

-- 3. Write globale solo ai revisori
UPDATE CONFIG_UserFunction SET WritePermission = 1
WHERE FunctionName = 'ForecastEditing'
  AND UserName IN (SELECT value FROM STRING_SPLIT(@ReviewerList, ','))

-- 4. Write su FR consolidata solo per i revisori
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

-- 5. Read=1 su FR 1-5 per i revisori (per visualizzare i dati sorgente)
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

### `5_CONSOLIDATE_FR6.sql` (modello)

Questo script deve essere **personalizzato secondo la logica di consolidamento** richiesta dal cliente. Il modello presuppone che ogni FR sia memorizzato in `WebCO_ForecastWeekly` con un `COTypeId` diverso.

```sql
-- ============================================
-- 5_CONSOLIDATE_FR6
-- Consolida le modifiche da FR1..FR5 in FR6.
--
-- ADATTARE la logica di consolidamento secondo necessità:
--   - Somma delle quantità
--   - Media
--   - Massimo
--   - Regola di business specifica
-- ============================================

SET NOCOUNT ON

DECLARE @FrSourceList NVARCHAR(MAX) = N'4,5,6,7,8'  -- COTypeId per FR1..FR5
DECLARE @FrTarget INT = 9                             -- COTypeId per FR6
DECLARE @YearFrom INT, @YearTo INT, @WeekFrom INT, @WeekTo INT

-- Adatta all'orizzonte di forecast configurato
SELECT @YearFrom = MIN(Year), @YearTo = MAX(Year)
FROM WebCO_ForecastWeekly
WHERE COTypeId IN (SELECT value FROM STRING_SPLIT(@FrSourceList, ','))

-- ============================================
-- ESEMPIO: Somma di FR1..FR5 -> FR6
-- Sostituire con la logica reale del cliente
-- ============================================

-- Prima, azzera FR6 nell'orizzonte attivo
UPDATE WebCO_ForecastWeekly
SET FrcQty = 0,
    EditedFlag = 0,
    EditedDate = NULL,
    EditedByUser = NULL
WHERE COTypeId = @FrTarget

-- Consolida: somma di tutte le FR sorgente
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

> ⚠️ **IMPORTANTE**: Il `COTypeId` di ogni FR corrisponde a `ForecastRevisionsEnum`:
> - FR1 = 4
> - FR2 = 5
> - FR3 = 6
> - FR4 = 7
> - FR5 = 8
> - FR6 = 9
>
> Verificare in `WebCO_ForecastWeekly` quali valori effettivi di `COTypeId` sono in uso.

---

## Script .cmd (cartella `D:\DCH\Batch\`)

### `FASE1_Init.cmd`

> **Prerequisito**: Configurare nell'interfaccia DCH: **Import settings > Forecast and Demand > Initialize Forecast Revisions after Forecast Import** = `SO99F-FR1;SO99F-FR2;SO99F-FR3;SO99F-FR4;SO99F-FR5;SO99F-FR6`

```cmd
@echo off
echo ============================================
echo FASE 1: Importare SO99+ e preparare la modifica
echo ============================================

echo.
echo [1/4] Importazione dati da SO99+ (include init FR1..FR6)...
DCHRemote.exe /IMPORT

echo.
echo [2/4] Assegnazione permessi per utente e FR...
DCHRemote.exe /EXECUTESQL 1_SETUP_FR_PARALLEL

echo.
echo [3/4] Abilitazione accesso in scrittura per tutti gli utenti...
DCHRemote.exe /EXECUTESQL 3_UNFREEZE_ALL_WRITE

echo.
echo [4/4] Pulizia cache DCH...
DCHRemote.exe /CLEAR_CACHE

echo.
echo ============================================
echo FASE 1 COMPLETATA - Gli utenti possono modificare
echo ============================================
```

### `FASE2_Freeze.cmd`

```cmd
@echo off
echo ============================================
echo FASE 2: Bloccare modifiche e consolidare
echo ============================================

echo.
echo [1/3] Blocco accesso in scrittura per tutti gli utenti...
DCHRemote.exe /EXECUTESQL 2_FREEZE_ALL_WRITE

echo.
echo [2/3] Pulizia cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo [3/3] Consolidamento FR1..FR5 in FR6...
DCHRemote.exe /EXECUTESQL 5_CONSOLIDATE_FR6

echo.
echo ============================================
echo FASE 2 COMPLETATA - Dati consolidati in FR6
echo ============================================
```

### `FASE3_Review.cmd`

```cmd
@echo off
echo ============================================
echo FASE 3: Abilitare revisione FR6
echo ============================================

echo.
echo [1/3] Configurazione permessi di revisione...
DCHRemote.exe /EXECUTESQL 4_SETUP_FR_CONSOLIDATE

echo.
echo [2/3] Abilitazione accesso in scrittura per i revisori...
DCHRemote.exe /EXECUTESQL 3_UNFREEZE_ALL_WRITE

echo.
echo [3/3] Pulizia cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo ============================================
echo FASE 3 COMPLETATA - I revisori possono modificare FR6
echo ============================================
```

### `FASE4_Export.cmd`

```cmd
@echo off
echo ============================================
echo FASE 4: Esportare e preparare ciclo successivo
echo ============================================

echo.
echo [1/3] Blocco accesso in scrittura...
DCHRemote.exe /EXECUTESQL 2_FREEZE_ALL_WRITE

echo.
echo [2/3] Pulizia cache...
DCHRemote.exe /CLEAR_CACHE

echo.
echo [3/3] Esportazione dati verso SO99+...
DCHRemote.exe /EXPORT

echo.
echo ============================================
echo FASE 4 COMPLETATA - Avviare FASE 1 per il ciclo successivo
echo ============================================
```

---

## SQL di registrazione in `SYSTEM_CustomProcedure`

Eseguire **una volta** nel database DCH:

```sql
-- Pulisci procedure precedenti (se esistenti)
DELETE FROM SYSTEM_CustomProcedure WHERE CustomProcedureId IN (
    '1_SETUP_FR_PARALLEL', '2_FREEZE_ALL_WRITE', '3_UNFREEZE_ALL_WRITE', 
    '4_SETUP_FR_CONSOLIDATE', '5_CONSOLIDATE_FR6'
)

-- Registra le nuove procedure (Source = 1 = sqlScript)
INSERT INTO SYSTEM_CustomProcedure (CustomProcedureId, Descr, Source, tsql, scriptPath, processPath)
VALUES 
('1_SETUP_FR_PARALLEL',    'Setup FR parallelo: permessi utente per FR',           1, '', 'D:\DCH\Scripts\1_SETUP_FR_PARALLEL.sql',    ''),
('2_FREEZE_ALL_WRITE',     'Blocca accesso scrittura per tutti gli utenti',        1, '', 'D:\DCH\Scripts\2_FREEZE_ALL_WRITE.sql',     ''),
('3_UNFREEZE_ALL_WRITE',   'Sblocca accesso scrittura per tutti gli utenti',       1, '', 'D:\DCH\Scripts\3_UNFREEZE_ALL_WRITE.sql',   ''),
('4_SETUP_FR_CONSOLIDATE', 'Setup revisione finale: solo FR6 modificabile per revisori', 1, '', 'D:\DCH\Scripts\4_SETUP_FR_CONSOLIDATE.sql', ''),
('5_CONSOLIDATE_FR6',      'Consolida FR1..FR5 in FR6',                            1, '', 'D:\DCH\Scripts\5_CONSOLIDATE_FR6.sql',     '')
```

---

## SQL di verifica post-implementazione

```sql
-- Verifica che le Custom Procedure siano registrate
SELECT CustomProcedureId, Descr, Source, scriptPath 
FROM SYSTEM_CustomProcedure 
WHERE CustomProcedureId LIKE '1_SETUP_FR%' 
   OR CustomProcedureId LIKE '2_FREEZE%' 
   OR CustomProcedureId LIKE '3_UNFREEZE%'
   OR CustomProcedureId LIKE '4_SETUP_FR%'
   OR CustomProcedureId = '5_CONSOLIDATE_FR6'
ORDER BY CustomProcedureId

-- Verifica stato dei permessi
SELECT UserName, FunctionName, FunctionId, 
       CASE ReadPermission WHEN 1 THEN 'R' ELSE '-' END + 
       CASE WritePermission WHEN 1 THEN 'W' ELSE '-' END AS Perms
FROM CONFIG_UserFunction
WHERE FunctionName IN ('ForecastEditing', 'LineForecastRevision')
ORDER BY UserName, FunctionName, CAST(FunctionId AS INT)
```

---

> **Versione documento**: 1.0  
> **Data**: 2026-08-05  
> **Ambito**: DCH 440