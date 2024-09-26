Feature: Update User
  Como un administrador
  Quiero poder actualizar la información de un usuario
  Para mantener los datos actualizados

  Scenario: Actualizar un usuario con datos válidos
    Given I have random user data for update
    When I check if the user exists and create if necessary for update
    And I obtain a JWT token for the user
    And I send a PUT request to "/usuarios/actualizar" with user data
    Then the response status code should be 200
    And the response body should match the update user schema