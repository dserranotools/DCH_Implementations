[Overview](README.md) • [Option A](option-a-extend-setting-entry.md) • [Option B](option-b-extrasettings-json-column.md) • [Option C](option-c-relational-properties-table.md) • [Option D](option-d-centralized-metadata-model.md) • [Current workarounds](current-custom-dropdown-workarounds.md) • [Web client analysis](web-client-analysis.md) • [Extending to processors](extending-to-processors.md)

---

# Table of Content

# Web Client Analysis for SOA-7702

This report validates the proposed `NodeProperty` model against the actual SO99+ Web Client implementation.

## Scope

- Web root: `../SO99plus/Web/SO99WebClient`
- Area: `SystemArea/Batch`

## Key files inspected

| Layer | File | Purpose |
|-------|------|---------|
| Controller | `Areas/SystemArea/Controllers/BatchController.cs` | MVC entry point for `/SystemArea/Batch/*` endpoints. |
| Application layer | `Src/AF/System/BatchAF.cs` | Builds modal structures and maps business objects to TG control view-models. |
| Framework bootstrap | `Scripts/TGControlsCommonScripts.ts` | `initForm` instantiates TG controls from server JSON. |
| Generic modal | `Scripts/TGControls/Modal/TGModal.ts` | Renders tabs and controls (dropdown, switch, textbox, grid, etc.). |
| Settings modal | `Scripts/TGControls/Modal/TGSettings.ts` | Specialised modal used for the **node settings** dialog. |
| Processor modal | `Scripts/TGControls/Modal/TGBatchModal.ts` | Custom modal used for **pre/post processor** creation/editing. |
| Controls | `Scripts/TGControls/TGDropDownList.ts`, `TGSwitch.ts`, `TGTextBox.ts`, `TGFileBrowser.ts` | Concrete Kendo-based renderers. |
| Batch page | `Scripts/InitScripts/SystemArea/Batch/Batch.ts` | Wires `ModifyNodeModal` → `SETTINGS_NODE_MODAL`. |

## How the node settings modal is built

1. The user clicks the settings icon in the Batch grid.
2. `Batch.ts` sends `BatchRequestIds.MODIFY_NODE_MODAL` to `BatchController.BatchAction`.
3. For a non-processor node, `BatchController` calls `_batchAF.GetNodeModal(seldata)`.
4. `BatchAF.GetNodeModal` loads the node via `Logic.NodeSettingsGet(...)` and then calls `SettingsNodeGeneralPanel`.
5. `SettingsNodeGeneralPanel` loops over the **five fixed `SettingEntry` slots**:

   ```csharp
   for (short i = 1; i <= BatchConfigurationConstants.MaxNumBatchOptions; i++)
   {
       NodeGeneric.SettingEntry entry = nodeSettings.get_SettingEntryData(i);
       if (entry.isEnabled)
       {
           // Boolean -> TGSwitch
           // Text     -> TGTextBox
       }
   }
   ```

   There is **no generic branch for a dropdown/enum** in this panel today.

6. The panel also adds a few special controls that are **not** part of the five options:
   - `cmbScheduleTime` — activation day dropdown.
   - `cmbProfileSettings` — profile selection dropdown (when `ProfileEnabled`).
   - `gridProfile` — profile detail grid (when `ProfileDetailGridEnabled`).

## What the generic modal renderer already supports

`TGModal.createTGControl` has explicit cases for the controls we need:

- `TGComponentType.TGSwitch` — boolean.
- `TGComponentType.TGTextBox` — text / numeric.
- `TGComponentType.TGDropDownList` — dropdown list.
- `TGComponentType.TGGrid` — data grid.
- `TGComponentType.TGMultiSelect` — multi-select list.
- `TGComponentType.TGSortable` — reorderable list.
- `TGComponentType.TGFileBrowser` — remote file browser.

`TGSettings.SetSelectedValue` collects the value of every control generically:

```typescript
for (var i in that.controls) {
    value.push({ "id": i, "value": that.controls[i].SelectedValue() });
}
```

Therefore, if the server emits a `TGDropDownList` inside the settings node modal, the existing TypeScript code will render it and return its selected value without any framework change.

## How dropdown data reaches the client

`TGControlsAF.DropDownListInit` accepts a `List<TGValue>`:

```csharp
public static TGDropDownListInit DropDownListInit(
    ITranslator Translation,
    string parent,
    string label,
    List<TGValue> data,
    string? defaultValue = null,
    ...)
```

A `List` type in `NodeProperty` can be rendered by converting:

- **Enum values** — reflect over the .NET enum named in `EnumTypeName` to build `List<TGValue>`.
- **Arbitrary dictionary** — convert `DropdownValues` directly into `List<TGValue>`.

## Processor modal vs. node settings modal

The processor modal (`TGBatchModal`) is a **separate code path** used for pre/post processors. It currently contains many hardcoded dropdowns:

- SQL procedure list (`GetSQLProcedure`).
- Aggregate parameter type/table/set (`GetAggregateParameterSet`).
- Dump report DB/connection/profile (`GetDumpReport`).
- Azure storage list (`LoadAzureStorage`).
- Remote file browser (`GetExternalProcess`, `GetUploadToStorage`).

These dropdowns are **not** driven by the five `SettingEntry` slots; they are custom-built per processor subclass in `BatchAF`. Refactoring them is out of scope for SOA-7702 unless the ticket is explicitly broadened.

## Findings

1. **The Web client already supports a generic dropdown control.** No new TypeScript control needs to be written.
2. **The node settings modal is currently limited to switch/text because `SettingsNodeGeneralPanel` only maps `ObjOptionType.IsBoolean` / `IsText`.** Adding a `List` type to the server-side model is the only required change in this path.
3. **Value collection is generic.** `TGSettings.SetSelectedValue` will work for dropdowns without modification.
4. **Special controls should stay custom.** The remote file browser (`TGFileBrowser`) and the profile detail grid (`TGGrid`) have domain-specific behaviour and should not be folded into a generic `List` property.
5. **Processor dropdowns are a different problem.** They live in `TGBatchModal` and are hardcoded per processor type. Treat them separately from node-level properties.

## Does this confirm or challenge Option C / D?

**It confirms the direction.**

The proposed `NodePropertyType.List` maps cleanly to the existing `TGDropDownList` control. The Web client architecture does not need a framework refactor; it only needs `BatchAF.SettingsNodeGeneralPanel` (or its future metadata-driven equivalent) to emit a `TGDropDownList` when a property is typed as `List`.

No rethinking of the data model is required. The recommendation remains:

- Use **Option C** (relational `C_BATCONF_PROP`) for a contained, data-driven rollout.
- Or **Option D** (metadata model) if the organisation wants a fully configurable Batch configuration engine.
