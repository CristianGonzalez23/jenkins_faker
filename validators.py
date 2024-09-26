# validators.py
from jsonschema import validate, ValidationError
from schemas import user_schema, update_user_schema

class UserValidator:
    @staticmethod
    def validate_create_user(data):
        try:
            validate(instance=data, schema=user_schema)
        except ValidationError as e:
            raise ValueError(f"Error de validación al crear usuario: {e.message}")

    @staticmethod
    def validate_update_user(data):
        try:
            validate(instance=data, schema=update_user_schema)
        except ValidationError as e:
            raise ValueError(f"Error de validación al actualizar usuario: {e.message}")
