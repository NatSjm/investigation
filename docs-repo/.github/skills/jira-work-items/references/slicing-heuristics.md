# Slicing heuristics

- **Meeting flow steps**: client overview -> product overview -> scenarios -> stress test -> summary / report.
- **Business rule variations**: standard vs exceptional (UNDETERMINED role, zero movements, closed session, missing cover policy).
- **Data variations**: actual movements only -> actual + modelled -> peer simulation; one city / mode -> all.
- **Operations**: view first, then enter (modal), then edit, then delete / reset.
- **Interfaces**: UI happy path first; Kafka consumers and external contracts as separate stories with contract tests.
- **Performance / NFR**: separate story when a computation spans `horizon months x scenarios x dimension values`.
- **Defer**: PDF layout polish, admin parameter screens, audit views - unless they are the feature.

Anti-patterns: "BE story" + "FE story" for the same behaviour (unless team mode = component); stories without a
demonstrable outcome; subtasks > 1 day; acceptance criteria that do not cite a `BR-*`.
