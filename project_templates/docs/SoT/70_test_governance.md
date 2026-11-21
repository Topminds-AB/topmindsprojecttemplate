# SoT – 70 Test Governance (repo-adapter)

> **Typ:** generell adapter för nya DevLab-repon. Innehåller **inga egna undantag eller nya testgrindar**.

## En gemensam regelkälla

- **Obligatorisk process och fast ändringstabell:** `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md`.
- **Projektets faktiska körkommandon, miljö och testmappning:** `docs/TESTING/TEST-STRATEGY.md`.
- **Aktuella acceptansfall, valda paket och resultat:** projektets befintliga kanoniska plan enligt `AGENTS.md` och `docs/SoT/00_index.md`.

Den gemensamma 07-standarden gäller för alla delpaket. **Director** ansvarar för testval enligt ändringstabellen och för att den repo-lokala mappningen beskriver verklig kod och verkliga testvägar. En lokal strategi får bara tillföra tekniska uppgifter som har verifierats i just detta repo.

## Det här får inte återinföras lokalt

- Körbara tester, obligatorisk röd testkörning eller separat RED-kvitto före implementation.
- Manuell registrering av varje nytt test i `TEST-CATALOG.md`.
- Separat manuell `TEST-LOG.md`-post för varje omkörning.
- Automatisk två- eller trippelkörning av oförändrade gröna helsviter.
- Fritt val att hoppa över ett paket som ändringstabellen kräver.
- Mockade integrationer som påstås bevisa verklig produktfunktion.

## Så används filen i ett nytt repo

Vid första uppstarten identifierar Director **faktiskt** testmål, befintligt testverktyg och möjliga testkommandon, och uppdaterar enbart `docs/TESTING/TEST-STRATEGY.md` och projektets etablerade plan. Om en obligatorisk integration inte kan verifieras anges den som **BLOCKERAD**; den ersätts inte av en låtsaskörning.

För mockad frontend i uttryckligen godkänd designfas gäller den separata standarden `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/10-mock-registry-standard.md` samt repo-lokala `docs/SoT/mock.md`. Tidigare historiska loggar och testkataloger från andra projekt får aldrig kopieras hit.
