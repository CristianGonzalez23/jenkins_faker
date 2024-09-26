from behave import given, when, then
import requests
import allure
import json
from werkzeug.security import generate_password_hash
from faker import Faker
import logging

API_URL = "http://192.168.200.131:5000"

# Inicializa Faker
fake = Faker()

def generate_random_user():
    return {
        'nombre': fake.name(),
        'email': fake.email(),
        'clave': fake.password()
    }

@given('un correo aleatorio puede no existir en el sistema')
def step_given_random_email_might_not_exist(context):
    # Generar un correo aleatorio
    context.email = fake.email()

@when('el usuario solicita restablecer la contraseña')
def step_when_user_requests_password_reset(context):
    # Verificar si el usuario existe
    response = requests.get(f"{API_URL}/usuarios/?email={context.email}")
    if response.status_code == 404:
        # Crear el usuario si no existe
        user_data = generate_random_user()
        user_data['email'] = context.email  # Usar el correo aleatorio generado
        create_response = requests.post(f"{API_URL}/usuarios", json=user_data)
        assert create_response.status_code == 201, 'No se pudo crear el usuario.'
    
    # Solicitar restablecimiento de contraseña
    reset_response = requests.post(f"{API_URL}/auth/reset_password", json={'email': context.email})
    
    # Si el usuario no existe, crearlo y volver a intentar
    if reset_response.status_code == 404 and reset_response.json().get('error') == 'El usuario no existe.':
        user_data = generate_random_user()
        user_data['email'] = context.email  # Usar el correo aleatorio generado
        create_response = requests.post(f"{API_URL}/usuarios", json=user_data)
        assert create_response.status_code == 201, 'No se pudo crear el usuario.'
        reset_response = requests.post(f"{API_URL}/auth/reset_password", json={'email': context.email})
    
    context.response = reset_response

@then('la respuesta debe indicar que se ha enviado un correo de restablecimiento')
def step_then_response_should_indicate_reset_email_sent(context):
    try:
        response_data = context.response.json()
    except ValueError:
        logging.error('La respuesta no es un JSON válido.')
        assert False, 'La respuesta no es un JSON válido.'

    # Validar que la respuesta contenga el mensaje esperado
    expected_message = 'Se ha enviado un enlace para restablecer la contraseña al correo electrónico proporcionado.'
    assert 'mensaje' in response_data, f'La respuesta no contiene el mensaje esperado. Respuesta: {response_data}'
    assert response_data['mensaje'] == expected_message, f'El mensaje de la respuesta no es el esperado. Esperado: "{expected_message}", Recibido: "{response_data["mensaje"]}"'
    
    # Guardar el token para el siguiente paso
    context.reset_token = response_data['token para restablecer contraseña'].split('/')[-1]
    
    # Utiliza logging en lugar de print para asegurar que se muestre en la salida de Behave
    logging.info(f'Response data: {response_data}')
    
    # Adjuntar la respuesta al reporte de Allure
    allure.attach(json.dumps(response_data, indent=2), name="Password Reset Response", attachment_type=allure.attachment_type.JSON)

@when('el usuario restablece la contraseña usando el token')
def step_when_user_resets_password_using_token(context):
    # Generar una nueva contraseña aleatoria
    new_password = fake.password()
    context.new_password = new_password
    
    # Usar el token para restablecer la contraseña
    reset_response = requests.post(f"{API_URL}/auth/reset_password/{context.reset_token}", json={'new_password': new_password})
    context.response = reset_response

@then('la respuesta debe indicar que la contraseña ha sido restablecida exitosamente')
def step_then_response_should_indicate_password_reset_successful(context):
    try:
        response_data = context.response.json()
    except ValueError:
        logging.error('La respuesta no es un JSON válido.')
        assert False, 'La respuesta no es un JSON válido.'

    # Validar que la respuesta contenga el mensaje esperado
    expected_message = 'Contraseña restablecida exitosamente.'
    assert 'mensaje' in response_data, f'La respuesta no contiene el mensaje esperado. Respuesta: {response_data}'
    assert response_data['mensaje'] == expected_message, f'El mensaje de la respuesta no es el esperado. Esperado: "{expected_message}", Recibido: "{response_data["mensaje"]}"'
    
    # Utiliza logging en lugar de print para asegurar que se muestre en la salida de Behave
    logging.info(f'Response data: {response_data}')
    
    # Adjuntar la respuesta al reporte de Allure
    allure.attach(json.dumps(response_data, indent=2), name="Password Reset Confirmation Response", attachment_type=allure.attachment_type.JSON)