from flask import Flask, jsonify, request
from config import Config
from models import db, User
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    decode_token,
)
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError  # Importar desde jwt.exceptions
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta  # Importar timedelta correctamente
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(Config)

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Cambia esto por una clave más segura
jwt = JWTManager(app)

db.init_app(app)

# Ruta para la documentación de Swagger
SWAGGER_URL = '/swagger'  # Ruta donde se visualizará Swagger UI
API_URL = '/static/swagger.yaml'  # Ruta del archivo swagger.yaml

# Configurar Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,            # URL para acceder a Swagger UI
    API_URL,                # Ruta del archivo YAML
    config={                # Configuraciones opcionales
        'app_name': "API de Usuarios"
    }
)

# Registrar Swagger en la app Flask
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Función para crear un nuevo usuario
def create_user(username, email, password_hash):
    new_user = User(username=username, email=email, password_hash=password_hash)
    try:
        db.session.add(new_user)
        db.session.commit()
        return {"id": new_user.id, "nombre": new_user.username, "email": new_user.email}, 201
    except IntegrityError as e:
        db.session.rollback()  # Deshacer los cambios en caso de error
        if 'unique constraint' in str(e.orig):
            return {"error": "El usuario ya existe."}, 409  # Mensaje personalizado
        return {"error": "Error al crear el usuario."}, 500  # Mensaje genérico
    finally:
        db.session.close()

# Definición de rutas de la API
@app.route('/usuarios/', methods=['GET'])
@jwt_required()  # Requiere token válido
def get_users():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    users = User.query.paginate(page=page, per_page=limit, error_out=False).items
    total = User.query.count()
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'users': [{'id': user.id, 'nombre': user.username, 'email': user.email} for user in users]
    })

# Obtener un usuario específico por su ID (JWT requerido)
@app.route('/usuarios/<int:id>', methods=['GET'])
@jwt_required()  # Requiere token válido
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({
            'id': user.id,
            'nombre': user.username,
            'email': user.email,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        })
    return jsonify({'error': 'Usuario no encontrado'}), 404

# Crear un nuevo usuario
@app.route('/usuarios/', methods=['POST'])
def register_user():
    data = request.get_json()
    if 'nombre' not in data or 'email' not in data or 'clave' not in data:
        return jsonify({'error': 'Campos obligatorios faltantes'}), 400

    # Generar el hash de la contraseña
    password_hash = generate_password_hash(data['clave'])

    # Llamar a la función create_user
    result, status_code = create_user(data['nombre'], data['email'], password_hash)
    return jsonify(result), status_code

# Actualizar un usuario por correo electrónico (JWT requerido)
@app.route('/usuarios/actualizar', methods=['PUT'])
@jwt_required()  # Requiere token válido
def update_user():
    current_user_email = get_jwt_identity()  # Obtener el correo del usuario autenticado
    data = request.get_json()
    email_to_update = data.get('email')

    if current_user_email != email_to_update:
        return jsonify({'error': 'No autorizado para actualizar este usuario'}), 403

    user = User.query.filter_by(email=email_to_update).first()
    if user:
        user.username = data.get('nombre', user.username)
        user.email = data.get('email', user.email)
        db.session.commit()
        return jsonify({
            'id': user.id,
            'nombre': user.username,
            'email': user.email,
            'updated_at': user.updated_at
        })
    return jsonify({'error': 'Usuario no encontrado'}), 404


# Eliminar un usuario por correo electrónico (JWT requerido)
@app.route('/usuarios/eliminar', methods=['DELETE'])
@jwt_required()  # Requiere token válido
def delete_user():
    current_user_email = get_jwt_identity()  # Obtener el correo del usuario autenticado
    data = request.get_json()
    email_to_delete = data.get('email')

    if current_user_email != email_to_delete:
        return jsonify({'error': 'No autorizado para eliminar este usuario'}), 403

    user = User.query.filter_by(email=email_to_delete).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return '', 204  # Código 204 sin contenido
    return jsonify({'error': 'Usuario no encontrado'}), 404

# Inicio de sesión y generación de JWT
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Verificar si los campos obligatorios están presentes
    if 'email' not in data or 'clave' not in data:
        return jsonify({'error': 'Faltan campos'}), 400

    # Buscar el usuario por email
    user = User.query.filter_by(email=data['email']).first()
    
    # Verificar la contraseña
    if user and check_password_hash(user.password_hash, data['clave']):
        # Generar el token JWT
        access_token = create_access_token(identity=user.email)
        return jsonify({'token': access_token}), 200
    
    # Responder con un error si las credenciales son incorrectas
    return jsonify({'error': 'Credenciales incorrectas'}), 401


# Solicitar restablecimiento de contraseña
@app.route('/auth/reset_password', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'El correo electrónico es obligatorio.'}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        # Crear token de restablecimiento de contraseña (válido por 30 minutos)
        expires = timedelta(minutes=30)  # Corregido timedelta
        reset_token = create_access_token(identity=user.email, expires_delta=expires)
        
        # Aquí debes enviar el correo con el token
        # Enviar enlace por correo (omitido aquí)
        reset_link = f"http://localhost:5000/auth/reset_password/{reset_token}"
        print(f"Enviar este enlace para restablecer la contraseña: {reset_link}")

        return jsonify({
            'mensaje': 'Se ha enviado un enlace para restablecer la contraseña al correo electrónico proporcionado.',
            'token para restablecer contraseña': reset_link  # Incluir el reset_link en la respuesta
        }), 200
    else:
        return jsonify({'error': 'El usuario no existe.'}), 404

@app.route('/auth/reset_password/<string:token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('new_password')

    # Verificar que new_password no sea None
    if new_password is None:
        return jsonify({'error': 'La nueva contraseña es obligatoria.'}), 400

    try:
        # Decodificar el token usando la clave secreta de JWT
        decoded = decode_token(token)
        user = User.query.filter_by(email=decoded['sub']).first()

        if user:
            # Actualizar la contraseña con el nuevo valor
            user.password_hash = generate_password_hash(new_password)  # Aquí se generará el hash
            db.session.commit()
            return jsonify({'mensaje': 'Contraseña restablecida exitosamente.'}), 200
        else:
            return jsonify({'error': 'Usuario no encontrado.'}), 404

    except ExpiredSignatureError:
        return jsonify({'error': 'El token ha expirado.'}), 400
    except InvalidTokenError:
        return jsonify({'error': 'Token inválido.'}), 401

# Verificar si el usuario existe y eliminarlo por correo electrónico
@app.route('/usuarios/verificar_y_eliminar', methods=['DELETE'])
def verify_and_delete_user_by_email():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'El correo electrónico es obligatorio.'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'mensaje': 'Usuario eliminado exitosamente.'}), 200  # Código 200 con mensaje
    return jsonify({'error': 'Usuario no encontrado.'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas antes de ejecutar la aplicación
    app.run(debug=True)
