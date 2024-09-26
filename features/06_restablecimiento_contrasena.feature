Feature: Restablecimiento de Contraseña
  Como un usuario
  Quiero poder restablecer mi contraseña
  Para poder acceder a mi cuenta si olvido mi contraseña

  Scenario: Solicitar y restablecer la contraseña con un correo aleatorio
    Given un correo aleatorio puede no existir en el sistema
    When el usuario solicita restablecer la contraseña
    Then la respuesta debe indicar que se ha enviado un correo de restablecimiento
    When el usuario restablece la contraseña usando el token
    Then la respuesta debe indicar que la contraseña ha sido restablecida exitosamente