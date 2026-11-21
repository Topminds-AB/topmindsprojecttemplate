# SoT – 00 Repository Index

<!-- NEXUS:GLOBAL-TEMPLATE:START:SOT-00 -->
> **Styrt block.** Texten mellan markörerna uppdateras centralt via Nexus och får inte ändras i repot. Projektets egna uppgifter skrivs **under** blocket.

> **Typ:** generell projektmall för DevLab-repon. **Ägare:** projektets Director. **Mål:** hitta rätt källor och körkommandon utan att läsa hela dokumentationssamlingen.

## Engångsinitiering – före första utvecklingsuppdraget

Projektdelen nedan innehåller **inga förvalda projektfakta**. Den agent som initierar projektet granskar befintliga källor och fyller endast i verifierade värden. Det är agentens arbete, inte en uppgift för projektägaren.

Ordningen är: läs rotens `AGENTS.md` → kontrollera faktisk repo-struktur och konfiguration → dokumentera källhänvisning och körkommandon → börja utveckla. Finns inte uppgiften skrivs **`SAKNAS`**; gissa inte repo, värd, tjänst, kommando eller inloggning. **`EJ_KARTLAGT` är en tydlig initialstatus, inte ett färdigt projektresultat.** Vid senare ändringar justerar Director endast de rader som berörs.

Kommandon fylls från **befintliga** skript, projektkonfigurationer, CI-definitioner och den faktiska körmiljön. Dokumentera inte ett kommando som inte har verifierats i repot. Behörigheter, hemligheter och produktionsmål får inte uppfinnas eller ändras för att fylla tabellen. En verifiering får aldrig påstås ha körts om kommandot, målet eller resultatet saknar faktiskt underlag.

## Dokument att öppna – endast vid behov

| Behov | Källa | Läsregel |
|---|---|---|
| Agentregler, säkerhet och arbetssätt | `AGENTS.md` i reporoten | Läs vid start och när regler ändras. |
| Vilka filer som får ändras | `.nexus/file-classes.json` **om filen finns** | `LOCKED` och `NEXUS_GENERATED` ändras aldrig i repot; i `MANAGED_BLOCK`-filer ändras bara projektdelen utanför markörerna. |
| Aktuell uppgift och delpaket | Den kanoniska projektplanen (se projektdelen) | Läs **relevant del**, inte hela historiken. |
| Verkliga användarflöden | `USER-FLOWS.md` **om filen finns**, annars faktisk kravkälla | Läs endast berörda flöden. |
| Övriga krav och arkitektur | Faktisk PRD/HLD/ADR **när de finns** | Läs endast vid konkret krav- eller arkitekturfråga. |
| Gemensam testpolicy | `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md` | Bindande vid val och körning av test. |
| Repo-lokal teststyrning | `docs/SoT/70_test_governance.md` och `docs/TESTING/TEST-STRATEGY.md` | Läs vid testplanering, inte vid varje kodrad. |
| Mockdata, endast vid tillåten mock | `docs/SoT/mock.md` och `docs/SoT/mock-registry.jsonl` | Verifiera faktiska poster, banner och länkmärkning. |

`CLAUDE.md` och `GEMINI.md` får peka på `AGENTS.md`, men ska inte introducera en konkurrerande uppsättning regler. Filer som **inte finns i det aktuella repot ska inte efterfrågas som obligatorisk läsning**.

## Testning, status och evidens

- **En testpolicy:** Obsidian 07, med fast ändringstabell. SoT/70 är endast en pekare och TEST-STRATEGY innehåller **projektets verkliga** kommandon/mappningar.
- **Ordning:** skriv acceptansfall och testpaket i projektplanen före kod → bygg högst fem leveranspunkter → skapa/kör de körbara testerna efter delpaketet → riktade omprov efter rättningar → en relevant fasgrind på slutversionen. Ingen obligatorisk RED eller trippelsvit.
- **En statuskälla:** projektets etablerade `PLAN.md`/projektplan. Ingen obligatorisk `TEST-CATALOG.md`, `TEST-LOG.md` eller separat manuell körkvittens.
- **Verklig funktion:** verifiera avsedd körmiljö och godkända identiteter; mockad eller enbart databasseedad funktion räcker inte som bevis på verkligt användarflöde.

## Underhåll

Uppdatera projektdelen bara när projektets faktiska körväg, viktiga komponenter, giltiga kommandon eller källhänvisningar förändras. Skapa inte kopior av fasstatus, testloggar eller fullständiga PRD/HLD-avsnitt här.
<!-- NEXUS:GLOBAL-TEMPLATE:END:SOT-00 -->

## 1. Projektuppgifter

| Projektuppgift | Verifierat värde | Källa i repot |
|---|---|---|
| Projektnamn och syfte | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Reporot och ansvarig kodbas | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Användare och viktigaste användarflöde | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Teknikstack och huvudkomponenter | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Verklig utvecklings-/testmålmiljö | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Kanonisk projektplan | `EJ_KARTLAGT` | `EJ_KARTLAGT` |

## 2. Faktiska kommandon och körmiljö

| Operation | Verifierat kommando eller etablerat flöde | Körmål | Status |
|---|---|---|---|
| Starta aktuell applikation | `EJ_KARTLAGT` | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Statisk kontroll (bygg, lint, typer) | `EJ_KARTLAGT` | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Kör riktat funktionstest | Se `docs/TESTING/TEST-STRATEGY.md` | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Verifiera verkligt användarflöde | `EJ_KARTLAGT` | `EJ_KARTLAGT` | `EJ_KARTLAGT` |
| Installera/verifiera ändrad version | `EJ_KARTLAGT` | `EJ_KARTLAGT` | `EJ_KARTLAGT` |

## 3. Arkitektur – verkliga referenser

| Fråga | Verifierat svar eller källhänvisning |
|---|---|
| Vilken komponent tar emot användarens begäran? | `EJ_KARTLAGT` |
| Var finns tjänstelogik och externa integrationer? | `EJ_KARTLAGT` |
| Var lagras beständiga data och hur migreras de? | `EJ_KARTLAGT` |
| Var ligger driftskonfiguration utan hemligheter? | `EJ_KARTLAGT` |
| Hur kontrolleras ändringen i verkligt körande version? | `EJ_KARTLAGT` |
