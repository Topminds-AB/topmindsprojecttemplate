# Questions for PO Protocol (Mandatory)

## Do not ask the PO during implementation
If you identify ambiguities, missing requirements, or decision points:
- do not interrupt execution to ask
- proceed with the best implementable path that preserves correctness and scope
- record questions in `manifest/questions_for_po.md`

## `manifest/questions_for_po.md` format rules
- The file must always exist.
- If there are no questions, it must contain exactly one line:
  - `No questions.`
- If there are questions, list bullets. Each bullet must include:
  - exact file/path/context that triggered the question
  - why it matters (impact)
  - two concrete options (A/B)
  - a recommended default based on repo evidence (PRD/SoT/tests)
