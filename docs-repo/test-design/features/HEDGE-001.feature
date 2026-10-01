@HEDGE-001
Feature: Propose interest-rate hedge for a loan
  Spec: features/hedges/HEDGE-001.md

  Background:
    Given I am logged in as advisor
    And client "ACME-SYN" has active loan "L-1"
    And client "ACME-SYN" has closed loan "L-2"
    And loan "L-1" has outstanding principal 1000000 EUR on 2027-01-01

  @api @BR-HEDGE-001-1
  Scenario: Proposal must reference an active loan
    When the advisor creates a proposal for loan "L-2"
      | notional | fixed_rate | tenor_months | start_date |
      | 500000   | 3.00       | 24           | 2027-01-01 |
    Then the request is rejected with error "LOAN_NOT_ACTIVE"

  @api @BR-HEDGE-001-2
  Scenario Outline: Notional vs outstanding principal boundary
    When the advisor sets notional <notional> EUR starting 2027-01-01
    Then the response status is <status>
    Examples:
      | notional   | status |
      | 999999.99  | 201    |
      | 1000000.00 | 201    |
      | 1000000.01 | 400    |

  @api @BR-HEDGE-001-3
  Scenario: Tenor exceeds client hedge limit
    Given the hedge limit for client "ACME-SYN" is 36 months
    When the advisor creates a proposal for loan "L-1"
      | notional | fixed_rate | tenor_months | start_date |
      | 500000   | 3.00       | 37           | 2027-01-01 |
    Then the request is rejected with error "TENOR_EXCEEDS_LIMIT"

  @calc @BR-HEDGE-001-4
  Scenario Outline: Monthly net cashflow (from domain/calculations/hedge_monthly_cashflow.md)
    Given market fixing EURIBOR-3M on <fixing_date> is <float_rate>%
    When the advisor sets notional <notional> EUR starting <fixing_date>
    And the preview is requested
    Then the net cashflow for that month is <expected>
    Examples:
      | case          | notional | fixed | float_rate | fixing_date | expected |
      | typical       | 1000000  | 3.00  | 2.50       | 2027-04-01  | 416.67   |
      | leap february | 1000000  | 3.00  | 2.50       | 2028-02-01  | 402.78   |
      | negative rate | 1000000  | 3.00  | -0.50      | 2027-03-01  | 3013.89  |

  @kafka @BR-HEDGE-001-5
  Scenario: Event published once on creation
    When the advisor creates a proposal for loan "L-1"
      | notional | fixed_rate | tenor_months | start_date |
      | 500000   | 3.00       | 24           | 2027-01-01 |
    Then exactly one "advisory.hedge.proposal.created" message with the proposal id is published
    And an audit entry "HEDGE_PROPOSAL_CREATED" exists for the proposal

  @api @authz
  Scenario: Read-only role cannot create proposals
    Given I am logged in as client-viewer
    When the advisor creates a proposal for loan "L-1"
      | notional | fixed_rate | tenor_months | start_date |
      | 500000   | 3.00       | 24           | 2027-01-01 |
    Then the response status is 403
