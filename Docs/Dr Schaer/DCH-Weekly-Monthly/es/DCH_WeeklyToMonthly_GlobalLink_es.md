# DCH Weekly → Monthly — Configuración del Global Link

**Cliente:** Dr. Schaer  
**Versión:** 1.0  
**Fecha:** 2026-08-05  
**Ámbito:** DCH 440 — Modo Weekly  

**Documentos relacionados:**
- [DCH_WeeklyToMonthly_Main.md](./DCH_WeeklyToMonthly_1_Main_es.md) ← Documento principal
- [DCH_WeeklyToMonthly_SQL.md](./DCH_WeeklyToMonthly_SQL_es.md) — Function SQL de agregación
- [DCH_WeeklyToMonthly_SSRS.md](./DCH_WeeklyToMonthly_SSRS_es.md) — Guía SSRS
- [DCH_WeeklyToMonthly_PowerBI.md](./DCH_WeeklyToMonthly_PowerBI_es.md) — Alternativa Power BI
- [DCH_WeeklyToMonthly_HTML.md](./DCH_WeeklyToMonthly_HTML_es.md) — Alternativa HTML estático

---

## 1. ¿Qué es un Global Link?

DCH permite configurar **enlaces externos** que se muestran en el menú **Cockpit**. Estos enlaces:

- Se abren en un **iframe embebido** dentro de la interfaz de DCH
- Soportan **placeholders** que se reemplazan dinámicamente con datos del usuario y del forecast
- Pueden ser **Globales** (visibles para todos los usuarios) o por **Usuario** (cada usuario configura los suyos)
- Se gestionan desde `Auxiliary Data > Global Links` (admin) o `Users > Links` (usuario)

---

## 2. Placeholders disponibles

| Placeholder | Valor reemplazado | Ejemplo |
|---|---|---|
| `{USER_NAME}` | Nombre de usuario autenticado (lowercase) | `john.doe` |
| `{DATE_FORECAST_CURRENT}` | Fecha de inicio del horizonte de forecast, en el formato configurado en `PARAM_GLOBAL_LINKS_DATE_FORMAT` | `2026-01-05` |
| `{DATE_FORECAST_END}` | Fecha de fin del horizonte de forecast | `2026-12-28` |

> El formato de fecha se configura en `CONFIG_ParamGen`: `PARAM_GLOBAL_LINKS_DATE_FORMAT`. Por defecto: `yyyy-MM-dd`.

---

## 3. Configuración paso a paso

### 3.1 Acceder a Global Links

1. Entrar en DCH como **admin**
2. Ir a `Menu > Auxiliary Data > Global Links`
3. Ver la lista de links existentes (si los hay)

### 3.2 Crear un nuevo Global Link

Hacer clic en **New** y rellenar:

| Campo | Valor |
|---|---|
| **Description** | `Monthly Forecast Report` o el nombre descriptivo que prefiera el cliente |
| **Link (URL)** | La URL del informe SSRS con placeholders |

**URL completa:**
```
http://SSRS_SERVER/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```

Donde:
- `SSRS_SERVER` = nombre o IP del servidor donde corre SSRS
- `/MonthlyForecast` = ruta del informe en el Report Server
- `&rs:Embed=true` = oculta el toolbar de SSRS para una visualización limpia en el iframe

### 3.3 Guardar

Hacer clic en **Save**. El link aparece en la lista de Global Links.

### 3.4 Verificar en Cockpit

1. Ir a `Cockpit`
2. Buscar la entrada **"Monthly Forecast Report"** (o el nombre elegido)
3. Hacer clic — debe abrirse el informe SSRS embebido en DCH

---

## 4. Configuración por usuario (User Links)

Si se desea que **cada usuario tenga su propio link** (en lugar de uno global para todos):

1. Ir a `Users > [nombre de usuario] > Links`
2. Hacer clic en **New**
3. Configurar igual que el Global Link
4. Guardar

El link aparecerá en `Cockpit` solo para ese usuario.

> **Recomendación**: Usar Global Link a menos que haya una necesidad específica de personalización por usuario. Es más fácil de mantener.

---

## 5. Ejemplo: dos links (global + forecast actual)

Se pueden crear múltiples links para diferentes vistas:

### Link 1: Forecast completo (con fechas del horizonte)

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&DATE_FORECAST_CURRENT={DATE_FORECAST_CURRENT}&DATE_FORECAST_END={DATE_FORECAST_END}&rs:Embed=true
```
- **Description**: `Monthly Forecast (Horizon)`
- Muestra el informe filtrado al horizonte de forecast actual

### Link 2: Forecast sin filtro de fechas (todos los datos)

```
http://server/ReportServer?/MonthlyForecast&USER_NAME={USER_NAME}&rs:Embed=true
```
- **Description**: `Monthly Forecast (All Data)`
- Muestra el informe con todos los datos históricos

---

## 6. Troubleshooting

| Problema | Solución |
|---|---|
| El link no aparece en Cockpit | Verificar que se ha guardado correctamente en `Auxiliary Data > Global Links` |
| El iframe muestra "X-Frame-Options" error | Usar `&rs:Embed=true` en la URL; configurar SSRS para permitir embedding |
| Los placeholders no se reemplazan | Verificar que las llaves son `{PLACEHOLDER}` (no `%PLACEHOLDER%` ni `[PLACEHOLDER]`) |
| El informe carga pero sin datos | Verificar que la function SQL devuelve datos para ese rango de fechas; probar la URL directamente en el navegador |
| Error de credenciales SSRS | Configurar **stored credentials** en el Data Source del informe, no Windows Integrated |

---

> **Documento versión**: 1.0  
> **Fecha**: 2026-08-05  
> **Ámbito**: DCH 440 — Modo Weekly  
> **Cliente**: Dr. Schaer