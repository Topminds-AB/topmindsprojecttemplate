# Team Topminds — Playbook v1.0

> **Syfte:** En enkel, förutsägbar och snabb process för att ta idé → PRD → implementation i faser → audit → leverans, utan att fastna i byråkrati.

---

## 1) Roller (enkelt förklarat)

### **PO — Product Owner**

PO är den människa som styr arbetet och driver processen framåt. PO kan vara en eller flera personer i teamet, beroende på projekt och fas.

PO gör i praktiken:
- Har dialog med **OA** för att få fram komplett funktionsbild.
- Granskar **HLD** och **PRD** innan implementation.
- Styr hur stora faserna ska vara och när något är “klart nog”.
- Startar implementation via **IA** och driver review-loopar.

---

### **OA — Orchestration Agent**

OA är den “kloka planerings- och audit-agenten” (t.ex. ChatGPT). OA styr processen, strukturen och kvaliteten över IA.

OA gör i praktiken:
- Driver fram tydlighet genom frågor, struktur och dokument.
- Producerar HLD, PRD, SoT, Implementation Plan och IA-startprompter.
- Audit: läser snapshot och verifierar leverabler mot PRD/SoT/HLD/Plan.
- Håller koll på att SoT/PRD/HLD uppdateras vid större förändringar.
- Håller koll på agentbiblioteket i `/agents` och viktiga agentfiler som:
  - `CLAUDE.md`, `Agents.md`, `Gemini.md` (och eventuella motsvarande).

---

### **IA — Implementation Agent**

IA är agenten som gör det faktiska kodarbetet (t.ex. Claude/Codex i VSCode).

IA gör i praktiken:
- Implementerar fas för fas enligt Implementation Plan.
- Arbetar i brancher enligt Git-reglerna i denna playbook.
- Kör tester och skapar underlag för audit (manifest/evidence).
- Dokumenterar fasens arbete i worklog (enligt AO/OA-instruktion).
- Skapar snapshot med `create_codebase` enligt standard.

---

## 2) Grundprinciper
1. **En källa till sanning**: PRD + SoT + Implementation Plan är de dokument som styr arbetet.
2. **Fart med räcken**: Vi prioriterar framdrift, men med miniminivå på säkerhet/test/reproducerbarhet.
3. **Steg som passar ändamålet**: Vi jobbar i faser, men fasernas storlek anpassas efter behov och tid.
4. **Automatisera friktion**: Snapshot/manifest/loggar ska gå att skapa med ett kommando.
5. **Tydlighet > tolkning**: Skriv hellre korta, konkreta krav än långa generella texter.

> **Praktiskt:** Låt IA arbeta under lunch/vila. Review sker när PO är tillbaka på plats.

---

## 3) Dokumenten (vad de är och varför de finns)

### **HLD — High Level Design**
Övergripande arkitektur och systemkarta som är begriplig och praktisk:
- huvudkomponenter
- dataflöden
- data stores
- drift-/deploy-tänk
- risker/avgränsningar

HLD är PO:s första “granskningsstopp” innan PRD.

---

### **PRD — Product Requirements Document**

Heltäckande kravdokument:
- funktioner och beteenden
- acceptance criteria
- edge cases
- icke-funktionella krav (drift, prestanda, säkerhet på den nivå som behövs)
- tydliga avgränsningar (“ingår” / “ingår inte”)

---

### **SoT — Source of Truth**
Repo-specifik sanning om hur systemet hänger ihop:
- var saker finns (repo-map)
- hur man kör lokalt
- var config finns
- hur data hanteras (DB, dumps, migrations)
- referenser till PRD/Plan och “hur vi jobbar i detta repo”

SoT ska vara praktisk och fungera som “orienteringskarta” vid review/audit.

---

### **Implementation Plan**
Fasindelad plan som IA ska följa:
- mål per fas
- scope per fas (in/out)
- leverabler (kod + evidens)
- testkrav
- hur snapshot ska tas

> **Viktigt:** Planen är ett grunddokument som kan förändras under implementationen.

---

### **Worklog (dagbok per fas)**
Worklog är fasens dagboksanteckning och ska skrivas av **IA** efter varje fas.

- Worklog ligger i dokumentationen.
- OA ska trigga detta i IA-prompten så att:
  - IA gör en anteckning i worklog i samband med commit/avslut av fasen.
- Worklog ska beskriva:
  - vad som gjordes
  - varför
  - vilka tester som kördes
  - vad som återstår / risker

---

## 4) Processen: Idé → Plan → Implementation → Audit

### Steg 0 — Initiering (PO ↔ OA)
1. PO har dialog med OA om produkten och funktionen.
2. Alla önskemål och kontext tas fram och inkluderas.
3. PO ska alltid avsluta detta steg med:
   - “Har du några frågor innan du går vidare?”
4. Om PO inte frågar detta ska OA ställa frågor ändå tills bilden är tillräckligt tydlig.

**Output:** En tydlig funktionsbeskrivning som OA kan designa utifrån.

---

### Steg 1 — HLD - High Level Design - (OA skapar, PO granskar)

1. OA tar fram **HLD**.
2. PO granskar HLD.
3. PO frågar uttryckligen om OA har frågor.
4. Frågor bollas tills HLD känns “rätt”.

**Output:** HLD som båda är överens om.

---

### Steg 2 — PRD (OA skapar, PO granskar)

1. OA skapar en fullständig **PRD** baserad på funktionsbeskrivning + HLD.
2. PO granskar PRD.
3. PO frågar om OA har frågor och driver tydlighet.

**Output:** PRD som styr implementationen.

---

### Steg 3 — SoT (OA skapar, PO lägger in i repo)
1. OA skapar **SoT** som kopieras in till `/docs/SoT/`.
2. OA ger PO instruktioner för vilka filer som ska placeras var.

**Output:** SoT på plats i repot.

---

### Steg 4 — Implementation Plan (OA skapar, PO lägger in i repo)
1. OA skapar fasindelad **Implementation Plan** och kopieras till `/docs/implementation/<project>/`.
2. PO informerar (eller OA frågar) om hur långa faserna ska vara:
   - kortare faser vid osäkerhet/hög risk
   - längre faser vid stabil och tydlig implementation

**Output:** Implementation Plan på plats.

---

### Steg 5 — Startprompt (OA → IA)
1. OA skriver första startprompten (på engelska) för IA.
2. PO startar IA med prompten i VSCode.

**Output:** IA kan börja implementera Fas 00/01.

---

### Steg 6 — Implementation & Audit-loop (per fas)
För varje fas i planen:

1. **PO startar fasen**
   - PO ska starta om agenten (ny session) så kontext rensas.
   - OA ska i startprompten ge precis så mycket referenser/paths att IA får “lagom” kontext.

2. **IA implementerar**
   - arbetar i rätt branch (se Git-regler)
   - uppdaterar/producerar evidens enligt fasen
   - skriver worklog-notering enligt instruktion

3. **IA skapar snapshot**
   - använder `create_codebase`-mallen för zip/snapshot
   - inkluderar manifest/loggar/dumps enligt behov
   - exkluderar tunga/hemliga filer

4. **OA audit:ar**
   - kontrollerar att leverabler matchar PRD/SoT/HLD/Plan
   - rapporterar avvikelser/risker
   - skriver nästa systemprompt för IA (engelska)

5. **Fortsätt eller justera**
   - om plan/HLD/PRD behöver uppdateras vid större ändringar ska OA initiera det
   - OA godkänner justeringar och beslutar om nästa fas samt skriver ny systemprompt till IA

---

## 5) Leveransprofiler (kort version)
> Leveransprofiler används för att bestämma hur tung “bevisnivå” som behövs. Detta förtydligas senare.

### **MVP_FAST**

- Fokus: framdrift.
- Minimikrav: startbart, smoke test, inga secrets, snapshot + minimal manifest.

### **STANDARD**
- Fokus: stabilitet.
- Krav: relevanta tester, tydligare evidens, SoT uppdateras vid större ändringar.

### **AUDIT_STRICT**

- Fokus: revisionsbar leverans.
- Krav: mer omfattande worklog/evidence och striktare DoD.

---

## 6) Git-flöde (förenklat men tydligt)

### Grundregler
- Arbete sker **aldrig direkt på `main`**.
- Det finns en långlivad **implementations-branch** som är en fork från `main`.
- För varje fas skapas en **fas-branch** från implementations-branchen.

### Branchstruktur
1. `main`  
2. `implementation/<project>` (långlivad, från `main`)  
3. `phase-XX/<kort-namn>` (kortlivad, från implementations-branch)

### Flöde per fas
1. Skapa `phase-XX/...` från `implementation/<project>`
2. Implementera fasen
3. Commit (en eller flera, “bra nog” men begripliga)
4. Merge `phase-XX/...` → `implementation/<project>`
5. Push implementations-branchen

### När allt är klart
- Skapa en PR: `implementation/<project>` → `main`
- PR används som sista check innan merge till `main`

> **Viktigt för IA:** Git-flödet ska följas noggrant, men utan att fastna i perfektion. Målet är spårbarhet och ordning, inte tidsförlust.

---

## 7) Snapshot och `create_codebase`
Snapshot tas enligt standard med `create_codebase` (mallen ni redan använder).

### Krav (minimum)
- Snapshot ska gå att audit:a utan att man behöver fråga om basics.
- Snapshot ska inte innehålla secrets eller stora onödiga filer.

### OA:s ansvar här
- OA ska i IA-prompten tala om exakt:
  - hur snapshot ska tas (vilket kommando/script)
  - vilka mappar/filer som ska ingå som evidens för fasen
  - vad som ska exkluderas

> `create_codebase` kan ses över separat för förbättringar, men standarden är att den används.

---

## 8) Definitioner (DoR / DoD)

### Definition of Ready (innan fas startar)

- Fasens mål är tydligt.
- PRD/SoT/HLD/Plan-paths är kända och refererade i prompten.
- Testkrav för fasen är tydliga.

### Definition of Done (när fasen är klar)

- Fasens acceptance criteria uppfyllda.
- Tester körda enligt fasens krav.
- Worklog uppdaterad.
- Snapshot skapad och kan audit:as.

---

## 9) /agents — agentbiblioteket
- Alla agenter använder biblioteket i `/agents`.
- OA ansvarar för att hålla agentfiler aktuella:
  - `CLAUDE.md`, `Agents.md`, `Gemini.md` och andra relevanta agentinstruktioner.
- `/agents` ska vara praktiskt: det ska hjälpa, inte bromsa.

---

## 10) Underhåll av sanning (OA:s löpande ansvar)
Vid större förändringar ska OA initiera uppdatering av:
- **HLD** (om arkitekturen ändras)
- **PRD** (om krav/acceptance criteria ändras)
- **SoT** (om repo-map/run/config/dataflöden ändras)
- **Implementation Plan** (om planens faser eller scope förändras)
- **Agentfiler** (om agentinstruktioner måste ändras)

PO godkänner förändringar som påverkar scope och prioritet.

---
Slut.