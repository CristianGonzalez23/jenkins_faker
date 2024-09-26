Feature: Login
  Como un usuario registrado
  Quiero poder iniciar sesión
  Para poder acceder a la aplicación

  Scenario: Iniciar sesión con credenciales válidas
    Given I have random user data
    When I check if the user exists and create if necessary
    And I send a POST request to "/auth/login" with user data
    Then the response status code should be 200
    And the response body should contain the JWT token