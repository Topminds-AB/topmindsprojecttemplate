@echo off
REM ====================================================================
REM  codex-start.bat - startar Codex direkt med vald modell + prestanda
REM  (ingen /model-klickning). Flyttbar: lagg filen i valfritt repo,
REM  den kor alltid Codex i katalogen dar filen ligger.
REM
REM  ANDRA HAR: modell och reasoning-effort.
REM    CODEX_MODEL   t.ex. gpt-5.6-sol, gpt-5-codex, o3
REM    CODEX_EFFORT  minimal | low | medium | high  (xhigh om modellen stodjer)
REM ====================================================================
set "CODEX_MODEL=gpt-5.6-sol"
set "CODEX_EFFORT=high"

REM Kor i bat-filens katalog (fungerar bade vid dubbelklick och terminal)
cd /d "%~dp0"

REM --dangerously-bypass-approvals-and-sandbox ar det formella namnet pa --yolo.
REM %* vidarebefordrar ev. extra argument, t.ex.:  codex-start.bat "min prompt"
codex --dangerously-bypass-approvals-and-sandbox -m %CODEX_MODEL% -c model_reasoning_effort=%CODEX_EFFORT% %*
