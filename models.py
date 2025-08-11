from app import db
from flask_login import UserMixin

post_categorias = db.Table(
    "post_categorias",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
    db.Column(
        "categoria_id", db.Integer, db.ForeignKey("categoria.id"), primary_key=True
    ),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_activate = db.Column(db.Boolean, default=True)

    def __str__(self):
        return self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.now())
    usuario_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    usuario = db.relationship("User", backref=db.backref("posts", lazy=True))
    categorias = db.relationship(
        "Categoria",
        secondary=post_categorias,
        lazy="subquery",
        backref=db.backref("posts", lazy=True),
    )


class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.now())
    usuario_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    usuario = db.relationship("User", backref=db.backref("comentarios", lazy=True))
    post = db.relationship("Post", backref=db.backref("comentarios", lazy=True))


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
