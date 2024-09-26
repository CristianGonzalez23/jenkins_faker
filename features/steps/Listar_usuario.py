from behave import given, when, then
import requests
from werkzeug.security import generate_password_hash
import allure
import json
from jsonschema import validate, ValidationError
from faker import Faker
import logging

API_URL = "http://localhost:5000"

# Inicializa Faker
fake = Faker()

# Esquema JSON para validar la respuesta de listar usuarios
list_users_response_schema = {
    "type": "object",
    "properties": {
        "limit": {"type": "integer"},
        "page": {"type": "integer"},
        "total": {"type": "integer"},
        "users": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "nombre": {"type": "string"},
                    "email": {"type": "string"}
                },
                "required": ["id", "nombre", "email"]
            }
        }
    },
    "required": ["limit", "page", "total", "users"]
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

@given('un usuario aleatorio existe y ha iniciado sesión para listar usuarios')
def step_given_random_user_exists_and_logs_in_for_list(context):
    # Generar datos de usuario aleatorios
    user_data = generate_random_user()
    
    # Crear el usuario
    data = {
        'nombre': user_data['nombre'],
        'email': user_data['email'],
        'clave': generate_password_hash(user_data['clave'])
    }
    requests.post(f"{API_URL}/usuarios", json=data)
    
    # Intentar iniciar sesión
    login_data = {
        'email': user_data['email'],
        'clave': user_data['clave']
    }
    login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    # Si el inicio de sesión falla, crear un nuevo usuario y volver a intentar
    if login_response.status_code != 200:
        logging.info('No se pudo iniciar sesión, creando un nuevo usuario.')
        user_data = generate_random_user()
        requests.post(f"{API_URL}/usuarios", json=user_data)
        login_data = {
            'email': user_data['email'],
            'clave': user_data['clave']
        }
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    assert login_response.status_code == 200, 'No se pudo iniciar sesión.'
    context.jwt_token = login_response.json()['token']

@when('el usuario solicita la lista de usuarios')
def step_when_user_requests_user_list(context):
    headers = {
        'Authorization': f'Bearer {context.jwt_token}'
    }
    response = requests.get(f"{API_URL}/usuarios", headers=headers)
    context.response = response

@then('la respuesta debe contener una lista de usuarios')
def step_then_response_should_contain_user_list(context):
    response_data = context.response.json()
    
    # Validar la respuesta con el esquema
    is_valid, error_message = validate_response(response_data, list_users_response_schema)
    assert is_valid, f"Response validation failed: {error_message}"
    
    # Utiliza logging en lugar de print para asegurar que se muestre en la salida de Behave
    logging.info(f'Response data: {response_data}')
    
    # Adjuntar la respuesta al reporte de Allure
    allure.attach(json.dumps(response_data, indent=2), name="User List Response", attachment_type=allure.attachment_type.JSON)