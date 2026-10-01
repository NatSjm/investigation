# Test design

Gherkin cases + synthetic fixtures consumed by the **automated tests repo** (already exists). That repo owns
step definitions; this repo owns *what* to test. Sync: `scripts/push-to-tests-repo.ps1` opens a PR copying
`features/*.feature` and `fixtures/*` into the tests repo.

## Step vocabulary (shared contract with tests repo)

Keep steps generic and data-driven. Add new steps here **before** using them.

### Setup
- `Given client "<id>" has active loan "<loan>"` / `closed loan "<loan>"`
- `Given loan "<loan>" has outstanding principal <amount> <ccy> on <date>`
- `Given the hedge limit for client "<id>" is <months> months`
- `Given market fixing <index> on <date> is <rate>%`
- `Given stress scenario "<name>" with shock <bp> bp`
- `Given I am logged in as <role>`

### Actions
- `When the advisor creates a proposal for loan "<loan>"` (+ data table)
- `When the advisor sets notional <amount> <ccy> starting <date>`
- `When the preview is requested`
- `When the monthly run executes for <yyyy-mm>`
- `When the stress test runs for proposal "<id>" with scenario "<name>"`
- `When message from fixture "<file>" is published to "<topic>"`

### Assertions
- `Then the request is rejected with error "<CODE>"`
- `Then the response status is <code>`
- `Then the net cashflow for that month is <amount>`
- `Then the cashflow table matches fixture "<file>"`
- `Then exactly one "<topic>" message with the proposal id is published`
- `Then an audit entry "<action>" exists for the proposal`
- `Then the graph shows <n> data points`

Rules: `.github/instructions/test-design.instructions.md` · Skill: `.github/skills/gherkin-test-design/SKILL.md`
· Agent: `test-designer`.
