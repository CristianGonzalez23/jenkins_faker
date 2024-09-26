# schemas.py
user_schema = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "clave": {"type": "string", "minLength": 6}
    },
    "required": ["nombre", "email", "clave"]
}

update_user_schema = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "additionalProperties": False  # No permitir campos adicionales
}
