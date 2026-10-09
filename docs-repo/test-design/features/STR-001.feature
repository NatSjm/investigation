@STR-001
Feature: Stress test per scenario and dimension
  Spec: features/stress/STR-001.md
  Calculation: domain/calculations/stress_test_monthly.md (worked examples)

  Background:
    Given I am logged in as representative
    And client "ACME-SYN" exists with external reference "REG-1001"
    And an open product1 session "11111111-1111-4111-8111-111111111111" for client "ACME-SYN"
    And session "11111111-1111-4111-8111-111111111111" has horizon 12 months
    And baseline price 10.00 and baseline transport price 2.00 for every month
    And a cover policy covering 33.3333% of P1-STD
    And actual movement 2027-01 P1-STD Aldmoor IN quantity 150 unit price 10.00
    And actual movement 2027-02 P1-STD Aldmoor IN quantity 150 unit price 10.00
    And scenario "price-up" with price change 10% and transport change 25% from month 1
    And scenario "price-up" with price change 9.0909% and transport change 0% from month 2

  @calc @BR-STR-001-2
  Scenario: Importer sign — a price rise is a positive exposure
    Given client "ACME-SYN" has role IMPORTER for product group product1
    When the representative runs the stress test
    Then the stress row for month 1 and Aldmoor has exposure 100.00, transport cost delta 75.00, cumulative 175.00

  @calc @BR-STR-001-2
  Scenario: Exporter sign — the same price rise is a negative exposure
    Given client "ACME-SYN" has role EXPORTER for product group product1
    When the representative runs the stress test
    Then the stress row for month 1 and Aldmoor has exposure -100.00, transport cost delta 75.00, cumulative -25.00

  @calc @BR-STR-001-2
  Scenario: Mixed role uses the net direction quantity
    Given client "ACME-SYN" has role MIXED for product group product1
    And actual movement 2027-01 P1-STD Aldmoor IN quantity 90 unit price 10.00
    And actual movement 2027-01 P1-STD Aldmoor OUT quantity 60 unit price 10.00
    When the representative runs the stress test
    Then the stress row for month 1 and Aldmoor has exposure 20.00, transport cost delta 75.00, cumulative 95.00

  @calc @BR-STR-001-3
  Scenario: Cumulative exposure adds exposure and transport cost delta month by month
    Given client "ACME-SYN" has role IMPORTER for product group product1
    When the representative runs the stress test
    Then the stress row for month 1 and Aldmoor has exposure 100.00, transport cost delta 75.00, cumulative 175.00
    And the stress row for month 2 and Aldmoor has exposure 200.00, transport cost delta 75.00, cumulative 450.00
    And the stress table matches fixture "STR-001-stress-run.json"

  @api @BR-STR-001-1
  Scenario: Running again replaces the previous results
    Given client "ACME-SYN" has role IMPORTER for product group product1
    And the stress test was run for session "11111111-1111-4111-8111-111111111111"
    When the representative runs the stress test
    Then the response status is 200
    And the stress table matches fixture "STR-001-stress-run.json"

  @api @BR-STR-001-5
  Scenario Outline: Dimension must match the product group of the session
    Given client "ACME-SYN" has role IMPORTER for product group product1
    And the stress test was run for session "11111111-1111-4111-8111-111111111111"
    When the representative requests the stress test with dimension <dimension>
    Then the response status is <status>
    Examples:
      | dimension      | status |
      | CITY           | 200    |
      | TRANSPORT_MODE | 400    |

  @ui @BR-STR-001-5
  Scenario: Dimension toggle shows cities for a Product 1 session
    Given client "ACME-SYN" has role IMPORTER for product group product1
    And the stress test was run for session "11111111-1111-4111-8111-111111111111"
    When the representative requests the stress test with dimension CITY
    Then the stress table has one column per city

  @api @BR-STR-001-6
  Scenario: Reading before any run returns an empty result
    When the representative requests the stress test with dimension CITY
    Then the response status is 200

  @api @BR-STR-001-8
  Scenario Outline: Missing session header is rejected with 428
    When the request is sent without the session header
    And the representative <action>
    Then the response status is 428
    Examples:
      | action                                              |
      | runs the stress test                                |
      | requests the stress test with dimension CITY        |
