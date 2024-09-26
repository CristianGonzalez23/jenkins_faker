import json
from behave import given, when, then
import requests
import logging
from jsonschema import validate, ValidationError
from faker import Faker

API_URL = "http://192.168.1.108:5000"

# Configura el logging al nivel INFO
logging.basicConfig(level=logging.INFO)

# Inicializa Faker
fake = Faker()

# Esquema JSON para validar la respuesta de inicio de sesión
login_response_schema = {
    "type": "object",
    "properties": {
        "token": {"type": "string"}
    },
    "required": ["token"]
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

# Paso para definir los datos del usuario para crear uno nuevo
@given('I have random user data')
def step_given_random_user_data(context):
    context.user_data = generate_random_user()

@when('I check if the user exists and create if necessary')
def step_when_check_and_create_user(context):
    check_url = f'{API_URL}/usuarios/verificar'
    response = requests.post(check_url, json={'email': context.user_data['email']})

    if response.status_code == 404:
        logging.info('User does not exist, creating user.')
        create_url = f'{API_URL}/usuarios'
        create_response = requests.post(create_url, json=context.user_data)
        logging.info(f'Create user response status code: {create_response.status_code}')  # Logging create user response status code
        logging.info(f'Create user response body: {create_response.text}')  # Logging create user response body
        assert create_response.status_code == 201, 'No se pudo crear el usuario.'
    elif response.status_code not in (200, 204):
        assert False, 'Error al verificar la existencia del usuario.'

    logging.info(f'Response status code: {response.status_code}')  # Debugging line

# Paso para enviar la solicitud POST
@when('I send a POST request to "{endpoint}" with user data')
def step_when_send_post_request(context, endpoint):
    url = f'{API_URL}{endpoint}'  # Asegúrate de que la URL sea correcta
    headers = {'Content-Type': 'application/json'}  # Incluimos los headers manualmente
    logging.info(f'Sending POST request to URL: {url} with data: {context.user_data}')  # Logging URL and data
    response = requests.post(url, json=context.user_data, headers=headers)  # Asegura el formato JSON
    logging.info(f'Response status code: {response.status_code}')  # Logging response status code
    logging.info(f'Response body: {response.text}')  # Logging response body
    context.response = response

# Paso para verificar el código de estado
@then('the response status code should be {status_code:d}')
def step_then_check_status_code(context, status_code):
    logging.info(f'Response status code: {context.response.status_code}')  # Logging response status code
    assert context.response.status_code == status_code, f'Expected status code {status_code}, but got {context.response.status_code}'

@then('the response body should contain the JWT token')
def step_then_check_token(context):
    response_data = context.response.json()
    
    # Ajusta la clave según la respuesta de tu API
    token_key = 'token'  # Cambia a 'access_token' si es necesario
    
    assert token_key in response_data, f'JWT token "{token_key}" no está en la respuesta'
    
    context.jwt_token = response_data[token_key]
    
    # Validar la respuesta con el esquema
    is_valid, error_message = validate_response(response_data, login_response_schema)
    assert is_valid, f"Response validation failed: {error_message}"
    
    # Utiliza logging en lugar de print para asegurar que se muestre en la salida de Behave
    logging.info(f'Token JWT Generado: {context.jwt_token}')