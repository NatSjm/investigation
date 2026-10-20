# Slicing heuristics

- **Meeting flow steps**: client overview -> product overview -> scenarios -> stress test -> summary / report.
- **Business rule variations**: standard vs exceptional (UNDETERMINED role, zero movements, closed session, missing cover policy).
- **Data variations**: actual movements only -> actual + modelled -> peer simulation; one city / mode -> all.
- **Operations**: view first, then enter (modal), then edit, then delete / reset.
- **Interfaces**: UI happy path first; Kafka consumers and external contracts as separate stories with contract tests.
- **Performance / NFR**: separate story when a computation spans `horizon months x scenarios x dimension values`.
- **Defer**: PDF layout polish, admin parameter screens, audit views - unless they are the feature.

- **Cross-context requests** (request epics): slice by the flow step the request changes, not by context - a story
  that ends where the user sees the result may span two contexts (P1 modal save -> stress table); the contract /
  table / topic that must exist first is its own story the others `depends_on`; the mirrored product (P2 "as BR-P1")
  is a story of its own only when its rules differ, otherwise one story cites both specs' rules.
- **Existing + new**: a story reusing an existing calculation cites its spec's rule; a story building a new
  calculation cites the draft rule written for it and is labelled `needs-spec-review` (never a story on an
  undocumented formula).

Anti-patterns: "BE story" + "FE story" for the same behaviour (unless team mode = component); stories without a
demonstrable outcome; subtasks > 1 day; acceptance criteria that do not cite a `BR-*`; one epic per context for one
request.
