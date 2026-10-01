# Slicing heuristics

- **Workflow steps**: propose → review → approve → send to client.
- **Business rule variations**: standard vs. exceptional (e.g. limits exceeded, negative rates).
- **Data variations**: one currency → multi-currency; one instrument → portfolio.
- **Operations**: view first, then create, then edit, then delete.
- **Interfaces**: UI happy path first; Kafka/integration as separate story with contract tests.
- **Performance/NFR**: separate story when computation spans months × scenarios (stress test).
- **Defer**: reporting/export, admin configuration, audit views — unless they are the feature.

Anti-patterns: "BE story" + "FE story" for the same behaviour (unless team mode = component); stories without a
demonstrable outcome; subtasks > 1 day.
