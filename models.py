from app import db  # Importa la instancia de la base de datos (SQLAlchemy) desde la aplicación principal
from flask_login import UserMixin  # Clase auxiliar para integrar el modelo de usuario con Flask-Login

# Tabla intermedia para la relación muchos-a-muchos entre Post y Categoria
post_categorias = db.Table(
    "post_categorias",  # Nombre de la tabla en la base de datos
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),  # ID del post
    db.Column(
        "categoria_id", db.Integer, db.ForeignKey("categoria.id"), primary_key=True  # ID de la categoría
    ),
)

# Modelo de usuario
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único
    username = db.Column(db.String(100), nullable=False, unique=True)  # Nombre de usuario único
    email = db.Column(db.String(100), nullable=False, unique=True)  # Email único
    password_hash = db.Column(db.String(256), nullable=False)  # Contraseña en formato hash
    is_activate = db.Column(db.Boolean, default=True)  # Estado de activación del usuario

    def __str__(self):
        return self.username  # Representación en texto del usuario (su nombre de usuario)

# Modelo de post o publicación
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único
    titulo = db.Column(db.String(150), nullable=False)  # Título de la publicación
    contenido = db.Column(db.Text, nullable=False)  # Contenido de la publicación
    fecha_creacion = db.Column(db.DateTime, default=db.func.now())  # Fecha de creación automática
    usuario_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # Relación con usuario
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Estado de activación

    # Relación: un post pertenece a un usuario
    usuario = db.relationship("User", backref=db.backref("posts", lazy=True))

    # Relación muchos-a-muchos: un post puede tener varias categorías
    categorias = db.relationship(
        "Categoria",
        secondary=post_categorias,  # Usa la tabla intermedia definida antes
        lazy="subquery",  # Carga anticipada de datos
        backref=db.backref("posts", lazy=True),  # Desde categoría se puede acceder a sus posts
    )

# Modelo de comentario
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único
    texto = db.Column(db.Text, nullable=False)  # Texto del comentario
    fecha_creacion = db.Column(db.DateTime, default=db.func.now())  # Fecha automática
    usuario_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # Usuario autor
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)  # Post al que pertenece

    # Relación: un comentario pertenece a un usuario
    usuario = db.relationship("User", backref=db.backref("comentarios", lazy=True))

    # Relación: un comentario pertenece a un post
    post = db.relationship("Post", backref=db.backref("comentarios", lazy=True))

# Modelo de categoría
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único
    nombre = db.Column(db.String(100), nullable=False, unique=True)  # Nombre de la categoría, único
