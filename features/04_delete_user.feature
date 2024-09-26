Feature: Delete User
  Como un administrador
  Quiero poder eliminar un usuario
  Para mantener la base de datos limpia

  Scenario: Eliminar un usuario con datos válidos
    Given I have random user data for delete
    When I check if the user exists and create if necessary for delete
    And I obtain a JWT token for the user to delete
    And I send a DELETE request to "/usuarios/eliminar" with user data
    Then the response status code should be 204
    And the response body should match the delete user schema