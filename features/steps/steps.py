import json
from behave import given, when, then
import requests
from jsonschema import validate, ValidationError
from faker import Faker

API_URL = "http://192.168.200.131:5000"

# Variable global para almacenar los datos del usuario
user_data = {}
fake = Faker()

user_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "nombre": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["id", "nombre", "email"]
}

def validate_response(response, schema):
    try:
        validate(instance=response, schema=schema)
    except ValidationError as e:
        return False, str(e)
    return True, ""

def generate_random_users(count):
    users = []
    for _ in range(count):
        users.append({
            'nombre': fake.name(),
            'email': fake.email(),
            'clave': fake.password()
        })
    return users

# Generar un grupo de usuarios
user_group = generate_random_users(10)

@given('I have user data with name "{nombre}", email "{email}", and password "{clave}"')
def step_given_user_data(context, nombre, email, clave):
    if not hasattr(context, 'user_index'):
        context.user_index = 0
    context.user_data = user_group[context.user_index]
    context.user_index += 1

@when('I check if the user exists and delete if necessary')
def step_when_check_and_delete_user(context):
    delete_url = f'{API_URL}/usuarios/verificar_y_eliminar'
    response = requests.delete(delete_url, json={'email': context.user_data['email']})

    if response.status_code == 404:
        print('User does not exist, nothing to delete.')
    elif response.status_code not in (200, 204):
        print('Error deleting user.')

@when('I send a POST request to "{endpoint}" with the user data')
def step_when_send_post_request(context, endpoint):
    url = f'{API_URL}{endpoint}'
    response = requests.post(url, json=context.user_data)
    context.response = response

@then('the response status code should be {status_code:d}')
def step_then_check_status_code(context, status_code):
    assert context.response.status_code == status_code, f'Expected {status_code}, but got {context.response.status_code}'

@then('the response body should contain the user ID')
def step_then_check_user_id(context):
    response_data = context.response.json()
    assert 'id' in response_data, 'User ID is not in the response'
    is_valid, error_message = validate_response(response_data, user_response_schema)
    assert is_valid, f"Response validation failed: {error_message}"