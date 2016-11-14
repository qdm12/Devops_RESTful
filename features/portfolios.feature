Feature: The Portfolio Management Service back-end
    As a Portfolio System Manager
    I need a scalable native cloud RESTful service
    So that I can manage user portfolios

Background:
    Given the server is started

Scenario: The server is running
    When I visit the "home page"
    Then I should not see "404 Not Found"

Scenario: Add a new user portfolio
    When I add a user "alice"
    Then I should see status "201"
    When I visit "/portfolios"
    Then I should see "alice"

Scenario: Add a conflict user portfolio
    Given the following user name
        | name          |
        | alice         |
    When I add a user "alice"
    Then I should see status "409"

Scenario: List all portfolios
    Given the following user name
        | name          |
        | alice         |
        | bob           |
        | cathy         |
    When I visit "/portfolios"
    Then I should see "alice"
    And I should see "bob"
    And I should see "cathy"

Scenario: Retrieve a the NAV of an unknown user portfolio
    When I visit "/portfolios/unknown/nav"
    Then I should see status "404"

Scenario: Retrieve a the NAV of a user portfolio
    Given the following user name
        | name          |
        | alice         |
    When I visit "portfolios/alice/nav"
    Then I should see "0"

Scenario: Remove a user portfolio
    Given the following user name
        | name          |
        | alice         |
    When I remove a user "alice"
    Then I should see status "204"
    When I visit "/portfolios"
    Then I should not see "alice"

Scenario: Add a new asset to a user portfolio
    Given the following user name
        | name          |
        | alice         |
    When I add an asset, id: "1" and quantity: "2" for "alice"
    Then I should see status "201"
    When I visit "/portfolios/alice/assets"
    Then I should see "1"

Scenario: Add a conflict asset to a user portfolio
    Given the following user name
        | name          |
        | alice         |
    Given the following asset for "alice"
        | asset_id      | quantity      |
        | 1             | 1             |
    When I add an asset, id: "1" and quantity: "2" for "alice"
    Then I should see status "409"

Scenario: Add an asset to an unknown user portfolio
    When I add an asset, id: "1" and quantity: "2" for "unknown"
    Then I should see status "404"

Scenario: List all assets of a user portfolio
    Given the following user name
        | name          |
        | alice         |
    Given the following asset for "alice"
        | asset_id      | quantity      |
        | 1             | 1             |
        | 2             | 2             |
        | 3             | 3             |
    When I visit "/portfolio/alice/assets"
    Then I should see "1"
    AND I should see "2"
    AND I should see "3"

Scenario: List all assets of an unknown user portfolio
    When I visit "/portfolio/unknown/assets"
    Then I should see status "404"

Scenario: Retrieve an asset in an unknown portfolio
    When I visit "/portfolios/unknown/assets/1"
    Then I should see status "404"

Scenario: Retrieve an unknown asset in a portfolio
    Given the following user name
        | name          |
        | alice         |
    When I visit "/portfolios/alice/assets/1"
    Then I should see status "404"

Scenario: Retrieve an asset of a user portfolio
    Given the following user name
        | name          |
        | alice         |
    Given the following asset for "alice"
        | asset_id      | quantity      |
        | 1             | 10            |
    When I visit "/portfolios/alice/assets/1"
    Then I should see "10"
    When I visit "/portfolios/alice/assets/2"
    Then I should see status "404"

Scenario: Update an asset of a user portfolio
    Given the following user name
        | name          |
        | alice         |
    Given the following asset for "alice"
        | asset_id      | quantity      |
        | 1             | 10            |
    When I update the quantity, quantity: "10", of an asset, id: "1", of "alice"
    Then I should see status "200"
    When I visit "/portfolios/alice/assets/1"
    Then I should not see "10.0"
    AND I should see "20.0"

Scenario: Update an asset of an unknown user portfolio
    When I update the quantity, quantity: "10", of an asset, id: "1", of "alice"
    Then I should see status "404"

Scenario: Update an unknown asset of a user portfolio
    Given the following user name
        | name          |
        | alice         |
    When I update the quantity, quantity: "10", of an asset, id: "1", of "alice"
    Then I should see status "404"

Scenario: Remove an asset of a user portfolio
    Given the following user name
        | name          |
        | alice         |
    Given the following asset for "alice"
        | asset_id      | quantity      |
        | 1             | 1             |
    When I remove an asset, id: "1" of "alice"
    Then I should see status "204"
    When I visit "/portfolios/alice/assets"
    Then I should not see "1"
    When I remove an asset, id: "1" of "alice"
    Then I should see status "204"

Scenario: Retrieve an asset of an known user portfolio
    When I remove an asset, id: "1" of "unknown"
    Then I should see status "204"
