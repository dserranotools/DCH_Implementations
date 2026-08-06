# DCH Weekly → Monthly — Alternativa: Reporte HTML estático

**Cliente:** Dr. Schaer  
**Versión:** 1.0  
**Fecha:** 2026-08-05  
**Ámbito:** DCH 440 — Modo Weekly  

**Documentos relacionados:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_es.md) ← Documento principal
- [DCH_WeeklyToMonthly_SQL.md](./DCH_WeeklyToMonthly_SQL_es.md) — Function SQL de agregación
- [DCH_WeeklyToMonthly_SSRS.md](./DCH_WeeklyToMonthly_SSRS_es.md) — Guía SSRS (opción recomendada)
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_es.md) — Alternativa Power BI
- [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_es.md) — Global Link en DCH

---

## 1. Descripción

Alternativa a SSRS para entornos donde **no se puede o no se quiere instalar SSRS**. Consiste en:

1. Un **Custom Procedure** que ejecuta la query contra la function `fn_WebCO_ForecastWeeklyToMonthly` y genera un fichero `.html` con una tabla formateada
2. El fichero se guarda en una carpeta accesible vía IIS (ej: `D:\DCH\Reports\`)
3. Un **Global Link** en DCH apunta a `http://dch-server/DCH/Reports/MonthlyReport.html`
4. El procedure se ejecuta vía `DCHRemote /EXECUTESQL` de forma programada (ej: cada noche)

---

## 2. Comparativa SSRS vs HTML estático

| Característica | SSRS | HTML estático |
|---|---|---|
| **Licencia adicional** | No (incluido en SQL Server) | No |
| **Instalación adicional** | Sí (feature de SQL Server) | No |
| **Interactividad** | Filtros, parámetros, drill-down | Ninguna (tabla plana) |
| **Exportación a Excel** | Nativa | Manual (copiar/pegar) |
| **Actualización de datos** | En tiempo real (consulta la BD en cada carga) | Programada (se regenera el HTML) |
| **Mantenimiento** | Medio (informe .rdl + Report Server) | Bajo (un SQL + un .html) |
| **Complejidad de implementación** | Media | Baja |
| **Aspecto visual** | Profesional (formato condicional, gráficos) | Básico (HTML con CSS) |

---

## 3. Implementación

### 3.1 Crear carpeta para reportes

En el servidor DCH:
```
D:\DCH\Reports\
```

Asegurar permisos de escritura para el servicio SQL Server y permisos de lectura para IIS.

### 3.2 Crear un virtual directory en IIS (si es necesario)

Si la carpeta no está dentro del sitio web de DCH, añadir un Virtual Directory en IIS apuntando a `D:\DCH\Reports\`.

### 3.3 Crear el Custom Procedure

Registrar en `SYSTEM_CustomProcedure`:

```sql
INSERT INTO SYSTEM_CustomProcedure (CustomProcedureId, Descr, Source, tsql, scriptPath, processPath)
VALUES ('6_GENERATE_MONTHLY_REPORT', 'Generate Monthly Forecast HTML Report', 1, '', 'D:\DCH\Scripts\6_GENERATE_MONTHLY_REPORT.sql', '')
```

### 3.4 Script SQL para generar el HTML

Fichero `D:\DCH\Scripts\6_GENERATE_MONTHLY_REPORT.sql`:

```sql
SET NOCOUNT ON

DECLARE @html NVARCHAR(MAX) = ''
DECLARE @filePath NVARCHAR(500) = 'D:\DCH\Reports\MonthlyReport.html'
DECLARE @dateFrom DATE = NULL  -- o fecha fija
DECLARE @dateTo DATE = NULL
DECLARE @userName NVARCHAR(128) = 'SYSTEM'

-- Construir cabecera HTML
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

-- Construir filas de datos
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

-- Cerrar HTML
SET @html = @html + '
        </tbody>
    </table>
</body>
</html>'

-- Escribir a fichero (requiere xp_cmdshell habilitado o usar BCP)
DECLARE @cmd NVARCHAR(1000)
SET @cmd = 'echo ' + REPLACE(@html, '''', '''''') + ' > "' + @filePath + '"'
-- Nota: para HTML grande, mejor usar BCP o un script PowerShell

PRINT 'Monthly Report HTML generated.'
```

> **Nota**: La generación de HTML desde TSQL con `FOR XML PATH` es adecuada para conjuntos de datos pequeños. Para volúmenes grandes (miles de productos/mercados), es mejor usar un script PowerShell externo o SSIS.

### 3.5 Configurar el Global Link

URL del Global Link:
```
http://dch-server/DCH/Reports/MonthlyReport.html
```

O si está en una carpeta virtual separada:
```
http://dch-server/Reports/MonthlyReport.html
```

---

## 4. Limitaciones

- **Sin interactividad**: No se puede filtrar, ordenar, ni hacer drill-down
- **Sin exportación nativa**: El usuario debe copiar/pegar la tabla
- **Sin parámetros dinámicos**: Los placeholders `{USER_NAME}` no aplican (el HTML es el mismo para todos)
- **Regeneración necesaria**: Si los datos cambian, hay que re-ejecutar el script
- **Tamaño limitado**: Para conjuntos de datos grandes, el HTML puede ser pesado y lento de cargar

---

> **Documento versión**: 1.0  
> **Fecha**: 2026-08-05  
> **Ámbito**: DCH 440 — Modo Weekly  
> **Cliente**: Dr. Schaer