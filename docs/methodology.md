# Aegis Methodology

## One-line method

```text
Problem
-> Authority
-> Contract
-> Evidence
-> Plan
-> Code
-> Gate
-> Release
-> Feedback
-> Problem
```

Aegis is not a replacement for Agile, DDD, TDD, ADRs, stage gates, CI, or product discovery. It is an orchestration layer that combines compatible parts of those methods into an AI-executable development lifecycle.

## Scarce resource in AI-native development

As code generation becomes cheaper, the scarce resources become:

- product and system judgment;
- explicit semantic contracts;
- coherent authority;
- verification design;
- failure classification;
- release and recovery evidence.

Aegis therefore optimizes for **correct decisions and executable proof**, not maximum code generation speed.

## The four questions that may not be deleted

Small projects may merge stages, but every Aegis profile retains:

1. Is the problem correct?
2. Is the authority / contract explicit?
3. What evidence proves the result?
4. What gate decides whether downstream work may proceed?

## Human / AI responsibilities

Aegis assumes a separation of responsibilities:

- Humans own value judgment, risk acceptance, final authority, and review accountability.
- ChatGPT-class reasoning agents help with problem framing, modeling, architecture, contracts, planning, and review.
- Coding agents implement bounded packages and produce evidence.
- CI, harnesses, oracles, and platform tests serve as executable truth where possible.

The goal is not to remove understanding. It is to make expert reasoning explicit enough to audit, teach, and reuse.
