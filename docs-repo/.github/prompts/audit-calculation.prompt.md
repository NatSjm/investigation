---
name: audit-calculation
description: Verify a calculation concept or a legacy formula page against the implementation and its unit test; record findings, never silently change numbers.
argument-hint: "calculation name | spec ID | legacy page path"
agent: calc-auditor
---
Subject: ${input:subject:stress_test_monthly}

Build the context pack, locate the implementation via `generated/be/docs-tags.md`, open only the calculator class
and its test, compare formula / parameters / thresholds / rounding / sign conventions / worked examples, write the
`## Audit <date>` findings table into the concept, set status and open questions, validate, rebuild indexes, log.
Report findings by severity and the specs that inherit the uncertainty (<= 12 lines).
