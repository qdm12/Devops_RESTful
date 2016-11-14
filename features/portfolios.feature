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
    When I add a user "dick"
    Then I should see status "201"
    When I visit "/portfolios"
    Then I should see "dick"

Scenario: Add a conflict user portfolio
    Given the following user names
        | name          |
        | dick          |
    When I add a user "dick"
    Then I should see status "409"

Scenario: List all portfolios
    Given the following user names
        | name          |
        | dick          |
        | bob           |
        | cathy         |
    When I visit "/portfolios"
    Then I should see "dick"
    And I should see "bob"
    And I should see "cathy"

Scenario: Retrieve a the NAV of an unknown user portfolio
    When I visit "/portfolios/unknown/nav"
    Then I should see status "404"

Scenario: Retrieve a the NAV of a user portfolio
    Given the following user names
        | name          |
        | dick          |
    When I visit "/api/v1/dick/nav"
    Then I should see "0"

Scenario: Remove a user portfolio
    Given the following user names
        | name          |
        | dick          |
    When I remove a user "dick"
    Then I should see status "204"
    When I visit "/portfolios"
    Then I should not see "dick"
