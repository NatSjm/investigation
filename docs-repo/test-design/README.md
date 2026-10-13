# Test design

Gherkin cases + synthetic fixtures consumed by the **automated tests repo** (already exists). That repo owns
step definitions; this repo owns *what* to test. Sync: `scripts/push-to-tests-repo.ps1` opens a PR copying
`features/*.feature` and `fixtures/*` into the tests repo.

Tags: `@<ID>` on the feature, `@BR-<ID>-<n>` on every scenario (one rule per scenario), plus a layer tag
`@api`, `@ui`, `@calc` or `@kafka`.

## Step vocabulary (shared contract with tests repo)

Keep steps generic and data-driven. Add new steps here **before** using them.

- `Given I am logged in as <role>` (`representative`, `admin`, `client-viewer`)
- `Given dataset "<name>" is loaded` - a named dataset from `generated/be/datasets.md` (seeds and integration fixtures of the
  backend, synthetic); prefer it over listing rows, then add explicit `Given` rows only for values the scenario asserts on
- `Given client "<id>" exists with external reference "<ref>"`
- `Given client "<id>" has role <ROLE> for product group <group>` / `has a manual role override <ROLE>`
- `Given an open <group> session "<id>" for client "<cid>"` / `a closed <group> session "<id>" for client "<cid>"`
- `Given session "<id>" has price basis <basis>` / `has horizon <n> months`
- `Given actual movement <yyyy-mm> <subProduct> <dimension> <IN|OUT> quantity <q> unit price <p>`
- `Given modelled movement <yyyy-mm> <subProduct> <dimension> <IN|OUT> quantity <q> unit price <p>`
- `Given a cover policy covering <pct>% of <subProduct>`
- `Given baseline price <p> and baseline transport price <t> for every month`
- `Given scenario "<name>" with price change <pct>% and transport change <pct>% from month <n>`
- `Given the stress test was run for session "<id>"`

### Actions
- `When the representative requests the Product 1 overview` (`with city "<city>"`)
- `When the representative requests the Product 1 projection`
- `When the representative saves <n> modelled movement rows` / `saves a modelled movement ...`
- `When the representative runs the peer simulation for segment "<seg>" with scaling factor <f>`
- `When the representative runs the stress test`
- `When the representative requests the stress test with dimension <CITY|TRANSPORT_MODE>`
- `When the request is sent without the session header`
- `When the representative closes session "<id>"`
- `When message from fixture "<file>" is published to "<topic>"`

### Assertions
- `Then the response status is <code>`
- `Then the response contains tables "<a>", "<b>", ...`
- `Then the stress row for month <n> and <dimension value> has exposure <x>, transport cost delta <y>, cumulative <z>`
- `Then the stress table matches fixture "<file>"`
- `Then the stress table has one column per <city|transport mode>`
- `Then exactly one "<topic>" message with the session id is published`
- `Then the projection of session "<id>" is recomputed` / `is unchanged`

Rules: `.github/instructions/test-design.instructions.md` · Skill: `.github/skills/gherkin-test-design/SKILL.md`
· Agent: `test-designer`.
