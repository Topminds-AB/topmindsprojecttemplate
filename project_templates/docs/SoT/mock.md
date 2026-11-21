# SoT – Mockregister (generell projektmall)

<!-- NEXUS:GLOBAL-TEMPLATE:START:MOCK -->
> **Styrt block.** Mockreglerna mellan markörerna uppdateras centralt via Nexus och får inte ändras i repot. Projektets egna noteringar skrivs **under** blocket.

> **Syfte:** varje uttryckligen tillåten mock ska kunna hittas, granskas och senare avvecklas. **Ingen mock är tillåten bara för att registret finns.**

## Styrande standarder

- Gemensam mockpolicy: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/10-mock-registry-standard.md`.
- Gemensam testpolicy: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md`.
- Detta repos aktuella maskinläsbara register: `docs/SoT/mock-registry.jsonl`.

Nya projekt startar med en **tom** JSONL-fil. Kopiera aldrig en annan applikations mockposter till ett nytt projekt.

## När får registret användas?

1. En mock måste vara **uttryckligen godkänd** i uppdraget eller omfattas av en uttryckligen beställd frontend-first-designfas.
2. En godkänd mock ska få en registerpost **i samma ändring** som den tillkommer. Registrera varje simulerad funktion, endpoint, datakälla eller annan väg separat så att den går att avveckla.
3. Varje sida/vy med mockinnehåll ska ha en **tydlig, kvarstående `MOCK DATA / DEMO`-banner**. Varje länk som leder till mockat innehåll ska märkas `MOCK` **före klick**.
4. En automatiserad integrationstest får inte ersätta verkligt beteende med en dold fake. Om en testmock alls tillåts krävs ett dokumenterat godkännande/ADR enligt den centrala test- och mockpolicyn.
5. När en mock ersatts av verklig funktion behålls historikposten men får status `retired`. Ta inte bort spårningen.
6. **Hårdkodad exempeldata är en mock.** Data som ser verklig ut men inte kommer från den verkliga källan (fasta listor, exempelkunder, påhittade siffror, statiska JSON-svar) får bara finnas som godkänd och registrerad mock med banner. Annars ska vyn visa ett tomt läge eller ett tydligt fel – aldrig låtsas fungera.
7. En mockad funktion rapporteras alltid som prototyp, aldrig som färdig integration, och räknas aldrig som verifierad funktion.

## Filformat

- Kodning: UTF-8; **en fullständig JSON-post per rad**, inga kommentarer eller platshållarrader.
- Det aktuella repots namn, verkliga filväg, radnummer och tidsstämpel ska hämtas från **faktiska källor**. Inga värden från den ursprungliga mallen får föras in som riktiga poster.
- Obligatoriska fält: `mock_repo`, `mock_id`, `mock_title`, `mock_type`, `mock_scope`, `mock_status`, `mock_description`, `mock_reason`, `mock_file_name`, `mock_file_path`, `mock_file_row_start`, `mock_file_row_end`, `mock_timestamp`, `mock_created_by`, `mock_removal_condition`.
- Rekommenderade fält: `mock_review_at`, `mock_linked_issue_or_adr`, `mock_tags`, `mock_notes`.
- Tillåtna `mock_status`: `active`, `retired`.
- Rekommenderade `mock_type`: `file`, `db-row`, `db-seed`, `api-response`, `image`, `ui-placeholder`, `fixture`, `test-double`, `generated-content`, `static-json`, `static-csv`, `other`.
- Rekommenderade `mock_scope`: `test`, `dev`, `demo`, `staging`, `migration`, `bootstrap`, `docs`, `benchmark`, `other`.

## Dokumentationsmall – **lägg inte in oförändrad i JSONL-filen**

Detta är ett **schemaexempel med tydliga fältnamn**, inte en registrerad mock eller godkänd testdata. Agenten ska skapa ett riktigt objekt från aktuell kod, faktisk radposition och uttryckligt beslut.

```json
{
  "mock_repo": "<verified-current-repo>",
  "mock_id": "<unique-id-in-current-repo>",
  "mock_title": "<short-descriptive-name>",
  "mock_type": "<valid-type>",
  "mock_scope": "<valid-scope>",
  "mock_status": "active",
  "mock_description": "<actual-simulated-behavior>",
  "mock_reason": "<reference-to-explicit-approval>",
  "mock_file_name": "<actual-file-name>",
  "mock_file_path": "<actual-repo-relative-path>",
  "mock_file_row_start": 0,
  "mock_file_row_end": 0,
  "mock_timestamp": "<actual-ISO-8601-timestamp>",
  "mock_created_by": "<actual-author>",
  "mock_removal_condition": "<verifiable-removal-condition>"
}
```

**Radnummer 0 och vinkelparenteser är ogiltiga mallmarkörer och får aldrig sparas i den verkliga JSONL-filen.** `mock_timestamp` uppdateras när postens metadata ändras.

## Snabb sökning i detta repo

```bash
rg -n '"mock_status"[[:space:]]*:[[:space:]]*"active"' docs/SoT/mock-registry.jsonl
rg -n '"mock_scope"[[:space:]]*:[[:space:]]*"test"' docs/SoT/mock-registry.jsonl
```

Vid ny mock: lägg till raden, kontrollera att JSON är giltigt och att berörda sidor/länkar är märkta. Vid avveckling: markera posten `retired`, kontrollera verklig funktion och ta bort synlig mockmarkering **endast** för den avvecklade delen.
<!-- NEXUS:GLOBAL-TEMPLATE:END:MOCK -->

## Projektets mockar

Själva registret är `docs/SoT/mock-registry.jsonl`. Här noteras bara det som inte står i registret, till exempel var bannerkomponenten och MOCK-märkningen av länkar finns i koden.

| Uppgift | Verifierat värde | Källa |
|---|---|---|
| Bannerkomponent för `MOCK DATA / DEMO` | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Hur länkar till mockat innehåll märks `MOCK` | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
