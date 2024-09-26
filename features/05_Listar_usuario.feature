Feature: Listar Usuarios
  Como un administrador
  Quiero poder listar los usuarios
  Para ver la información de todos los usuarios registrados

  Scenario: Listar usuarios con datos válidos
    Given un usuario aleatorio existe y ha iniciado sesión para listar usuarios
    When el usuario solicita la lista de usuarios
    Then la respuesta debe contener una lista de usuarios