# DCH Weekly → Monthly — Guía SSRS

**Cliente:** Dr. Schaer  
**Versión:** 1.0  
**Fecha:** 2026-08-05  
**Ámbito:** DCH 440 — Modo Weekly  

**Documentos relacionados:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_es.md) ← Documento principal
- [DCH_WeeklyToMonthly_SQL.md](./DCH_WeeklyToMonthly_SQL_es.md) — Function SQL de agregación
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_es.md) — Alternativa Power BI
- [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_es.md) — Global Link en DCH
- [DCH_WeeklyToMonthly_HTML.md](./DCH_WeeklyToMonthly_HTML_es.md) — Alternativa HTML estático

---

## 1. ¿Qué es SSRS?

SQL Server Reporting Services es el motor de informes de Microsoft, **incluido en la licencia de SQL Server** (Standard o superior). Permite:

- Diseñar informes con tablas, gráficos y parámetros
- Publicarlos en un portal web (Report Server)
- Acceder vía URL (compatible con el Global Link de DCH)
- Exportar a Excel, PDF, CSV
- Ejecutar bajo demanda o programados

**No requiere licencia adicional** — ya está incluido en SQL Server Standard.

---

## 2. Verificar si SSRS está instalado

### En el servidor SQL Server

1. Abrir **SQL Server Configuration Manager**
2. Buscar **SQL Server Reporting Services** en la lista de servicios
3. Si el servicio existe y está corriendo, SSRS está instalado

Alternativamente, abrir en el navegador:
```
http://localhost/Reports
```
Si carga el portal web de SSRS, está instalado.

### Si no está instalado

1. Ejecutar el instalador de SQL Server
2. Seleccionar **Add features to an existing instance**
3. Marcar **Reporting Services - Native**
4. Completar la instalación
5. Configurar el Report Server (abre automáticamente el Configuration Manager al finalizar)

---

## 3. Configuración de SSRS

### 3.1 SQL Server Reporting Services Configuration Manager

1. Abrir **Reporting Services Configuration Manager**
2. Conectar a la instancia de SSRS
3. Configurar las siguientes secciones:

| Sección | Acción |
|---|---|
| **Web Service URL** | Configurar puerto (default: 80) y directorio virtual (`ReportServer`) |
| **Database** | Crear/confirmar la base de datos `ReportServer` (donde SSRS guarda sus metadatos) |
| **Web Portal URL** | Configurar el portal web (`Reports`) |

Al finalizar, verificar accediendo a:
- Portal: `http://server/Reports`
- Web Service: `http://server/ReportServer`

### 3.2 Configurar autenticación para iframe (DCH)

Para que SSRS se pueda embeber en el iframe de DCH, es necesario permitirlo:

1. En el servidor SSRS, editar el archivo `ReportServer\Pages\ReportViewer.aspx`
2. Añadir el header `X-Frame-Options: ALLOW-FROM http://dch-server` (o usar `SAMEORIGIN` si DCH y SSRS están en el mismo dominio)

Alternativa más simple: usar el parámetro `&rs:Embed=true` en la URL (funciona en SSRS 2016+).

---

## 4. Instalar Report Builder

**Report Builder** es la herramienta gratuita de Microsoft para diseñar informes SSRS.

1. Descargar de: https://www.microsoft.com/en-us/download/details.aspx?id=53613
2. Instalar en la máquina del desarrollador
3. Al abrir, conectarse al Report Server: `http://server/ReportServer`

---

## 5. Diseñar el informe mensual

### 5.1 Crear el Data Source

1. En Report Builder, crear un **New Report** (Blank Report)
2. Añadir un **Data Source**:
   - **Name**: `DCH_DataSource`
   - **Type**: Microsoft SQL Server
   - **Connection string**: `Data Source=SERVER_NAME;Initial Catalog=DCH_DATABASE`
   - **Credentials**: Stored credentials (usuario SQL con permisos de lectura sobre `WebCO_ForecastWeekly` y la function)

### 5.2 Crear el Dataset

1. Añadir un **Dataset**:
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

2. Los parámetros `@USER_NAME`, `@DATE_FORECAST_CURRENT`, `@DATE_FORECAST_END` se crean automáticamente. Configurar valores por defecto:
   - `@USER_NAME`: Default = `""`
   - `@DATE_FORECAST_CURRENT`: Default = `NULL` (no required)
   - `@DATE_FORECAST_END`: Default = `NULL` (no required)

### 5.3 Diseñar la tabla

1. Insertar una **Table** (matriz o tabla simple)
2. Columnas recomendadas:
   - `COProductId` / `ProductDescr` (si se usa la vista enriquecida)
   - `COMarketId` / `MarketDescr`
   - `Year`
   - `Month`
   - `Budget`
   - `FrcQty`
   - `COQty1` ... `COQty5` (Forecast Revisions)
   - `OutstQty`
   - `COSO99`

3. Agrupar por `COProductId` y `COMarketId` para permitir drill-down
4. Añadir **totales** por grupo

### 5.4 Añadir exportación a Excel

SSRS incluye exportación a Excel de forma nativa (botón en el toolbar). Si se usa `rs:Embed=true`, el toolbar se oculta. Para seguir permitiendo la exportación:

- Opción A: No usar `rs:Embed=true` y mantener el toolbar visible
- Opción B: Añadir un parámetro `&rs:Command=Render&rs:Format=EXCEL` en un enlace dentro del propio informe

---

## 6. Publicar el informe

1. En Report Builder: **File > Save As > Save to Report Server**
2. URL: `http://server/ReportServer`
3. Carpeta: `/` (raíz) o crear una carpeta `/DCH`
4. Nombre: `MonthlyForecast`

El informe queda accesible en:
```
http://server/ReportServer?/MonthlyForecast
```

### Verificar publicación

Abrir en el navegador:
```
http://server/ReportServer?/MonthlyForecast&USER_NAME=test&DATE_FORECAST_CURRENT=2026-01-01&DATE_FORECAST_END=2026-12-31
```

---

## 7. URL para el Global Link de DCH

La URL final para configurar en el Global Link de DCH:

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```

Los placeholders `{USER_NAME}`, `{DATE_FORECAST_CURRENT}`, `{DATE_FORECAST_END}` son reemplazados por DCH automáticamente antes de cargar la URL en el iframe.

> Ver [DCH_WeeklyToMonthly_GlobalLink.md](./DCH_WeeklyToMonthly_GlobalLink_es.md) para la configuración completa del Global Link.

---

## 8. Troubleshooting SSRS

| Problema | Solución |
|---|---|
| "The report server cannot access the data source" | Verificar credenciales en el Data Source (usar stored credentials, no Windows Integrated) |
| El informe no se ve en el iframe de DCH | Añadir `&rs:Embed=true` a la URL; verificar X-Frame-Options |
| Error al publicar desde Report Builder | Verificar permisos del usuario en el Report Server (Content Manager o Publisher) |
| La function no aparece en el explorador de objetos | Verificar que se creó correctamente con `SELECT * FROM sys.objects WHERE name = 'fn_WebCO_ForecastWeeklyToMonthly'` |
| Parámetros no se pasan correctamente | Los nombres en la URL deben coincidir **exactamente** (case-sensitive en algunos casos) con los definidos en el informe |

---

> **Documento versión**: 1.0  
> **Fecha**: 2026-08-05  
> **Ámbito**: DCH 440 — Modo Weekly  
> **Cliente**: Dr. Schaer