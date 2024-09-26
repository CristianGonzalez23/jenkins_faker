import json
from behave import given, when, then
import requests
import logging
from jsonschema import validate, ValidationError
from faker import Faker

# Configura el logging al nivel INFO
logging.basicConfig(level=logging.INFO)

# Inicializa Faker
fake = Faker()

# Esquema JSON para validar la respuesta de eliminación de usuario
delete_user_response_schema = {
    "type": "object",
    "properties": {
        "message": {"type": "string"}
    },
    "required": ["message"]
}

def validate_response(response, schema):
    try:
        validate(instance=response, schema=schema)
    except ValidationError as e:
        return False, str(e)
    return True, ""

def generate_random_user():
    return {
        'nombre': fake.name(),
        'email': fake.email(),
        'clave': fake.password()
    }

# Paso para definir los datos del usuario para eliminar uno existente
@given('I have random user data for delete')
def step_given_random_user_data_for_delete(context):
    context.user_data = generate_random_user()

@when('I check if the user exists and create if necessary for delete')
def step_when_check_and_create_user_for_delete(context):
    check_url = f'http://localhost:5000/usuarios/verificar'
    response = requests.post(check_url, json={'email': context.user_data['email']})

    if response.status_code == 404:
        logging.info('User does not exist, creating user.')
        create_url = f'http://localhost:5000/usuarios'
        create_response = requests.post(create_url, json=context.user_data)
        logging.info(f'Create user response status code: {create_response.status_code}')  # Logging create user response status code
        logging.info(f'Create user response body: {create_response.text}')  # Logging create user response body
        assert create_response.status_code == 201, 'No se pudo crear el usuario.'
    elif response.status_code not in (200, 204):
        assert False, 'Error al verificar la existencia del usuario.'

    logging.info(f'Response status code: {response.status_code}')  # Debugging line

@when('I obtain a JWT token for the user to delete')
def step_when_obtain_jwt_token_for_delete(context):
    login_url = 'http://localhost:5000/auth/login'
    login_data = {
        'email': context.user_data['email'],
        'clave': context.user_data['clave']
    }
    response = requests.post(login_url, json=login_data)
    logging.info(f'Login response status code: {response.status_code}')  # Logging login response status code
    logging.info(f'Login response body: {response.text}')  # Logging login response body
    assert response.status_code == 200, 'No se pudo obtener el token JWT.'
    context.jwt_token = response.json()['token']

# Paso para enviar la solicitud DELETE para eliminar el usuario
@when('I send a DELETE request to "{endpoint}" with user data')
def step_when_send_delete_request(context, endpoint):
    url = f'http://localhost:5000{endpoint}'  # Asegúrate de que la URL sea correcta
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {context.jwt_token}'  # Incluimos el token JWT en el encabezado
    }
    logging.info(f'Sending DELETE request to URL: {url} with data: {context.user_data}')  # Logging URL and data
    response = requests.delete(url, json=context.user_data, headers=headers)  # Asegura el formato JSON
    logging.info(f'Response status code: {response.status_code}')  # Logging response status code
    logging.info(f'Response body: {response.text}')  # Logging response body
    context.response = response

# Paso para verificar el código de estado
@then('the response status code should be {status_code:d}')
def step_then_check_status_code(context, status_code):
    logging.info(f'Response status code: {context.response.status_code}')  # Logging response status code
    assert context.response.status_code == status_code, f'Expected status code {status_code}, but got {context.response.status_code}'

# Paso para verificar el esquema de la respuesta
@then('the response body should match the delete user schema')
def step_then_check_delete_user_schema(context):
    if context.response.status_code == 204:
        logging.info('No content in response, as expected for status code 204.')
        return

    response_data = context.response.json()
    
    # Validar la respuesta con el esquema
    is_valid, error_message = validate_response(response_data, delete_user_response_schema)
    assert is_valid, f"Response validation failed: {error_message}"
    
    # Utiliza logging en lugar de print para asegurar que se muestre en la salida de Behave
    logging.info(f'Response data: {response_data}')