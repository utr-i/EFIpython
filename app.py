from flask import Flask, flash, render_template, request, redirect, url_for, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
# Iniciamos app Flask
app = Flask(__name__)
app.secret_key = "cualquiercosa"
# Configuramos la conexión a la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/miniblog"
# Iniciamos sqlalchemy y migrate para los modelos y migraciones
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Configuramos el login
login_manager = LoginManager(app)
login_manager.login_view = "login" # Si no está logueado, te manda al login

# Importamos los modelos de la base de datos
from models import User, Post, Comentario, Categoria


# Esta función carga un usuario desde la base de datos usando su ID (necesario para sesiones)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Hacemos que todas las plantillas tengan acceso a las categorías automáticamente
@app.context_processor
def inject_categorias():
    return dict(categorias=Categoria.query.all())


# Ruta principal que muestra todos los posts activos
@app.route("/")
def index():
    posts = (
        Post.query.filter_by(is_active=True).order_by(Post.fecha_creacion.desc()).all()
    )
    return render_template("index.html", posts=posts)


# Registro de nuevos usuarios
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        # Verificamos que no exista == usuario O == email
        if User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            flash("Usuario o email ya existe", "error")
            return redirect(url_for("register"))
        # Creamos el nuevo usuario con contraseña encriptada
        new_user = User(
            username=username,
            email=email,
            # Hasheo de contrasenia
            password_hash=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registro exitoso. Ahora puedes iniciar sesion.", "success")
        return redirect(url_for("login"))
    # Si es GET, mostramos el formulario
    return render_template("auth/register.html")


# Inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Chequeo de que exista el usuario
        usuario = User.query.filter_by(username=username).first()
        # Comparar contrasenias - la hasheada y la comun
        if usuario and check_password_hash(usuario.password_hash, password):
            login_user(usuario) # Inicia sesión
            flash("Sesión iniciada", "success")
            return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos", "error")

    return render_template("auth/login.html")


# Cierre de sesión (solo si está logueado)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "success")
    return redirect(url_for("index"))


# Crear un nuevo post
@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        # Obtenemos todos los valores de los checkboxes marcados
        categorias_ids = request.form.getlist("categorias_seleccionadas")
        # Creamos el post asociándolo al usuario actual
        nuevo_post = Post(
            titulo=titulo, contenido=contenido, usuario_id=current_user.id
        )
        
        # Si seleccionó categorías, las agregamos al post
        if categorias_ids:
            # Buscamos los objetos Categoria correspondientes a los IDs
            categorias = Categoria.query.filter(Categoria.id.in_(categorias_ids)).all()
            # Se aniaden al POST
            nuevo_post.categorias.extend(categorias)

        db.session.add(nuevo_post)
        db.session.commit()

        flash("Post creado correctamente", "success")
        return redirect(url_for("index"))

    return render_template("new_post.html")


# Ver un post en detalle y agregar comentarios
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    # Si el usuario está logueado y envía un comentario
    if request.method == "POST" and current_user.is_authenticated:
        texto = request.form["texto"]
        comentario = Comentario(
            texto=texto, usuario_id=current_user.id, post_id=post.id
        )
        db.session.add(comentario)
        db.session.commit()
        flash("Comentario agregado", "success")
        return redirect(url_for("post_detail", post_id=post.id))

    return render_template("post_detail.html", post=post)


# Editar un post
@app.route("/post/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Solo el autor puede editar
    if post.usuario_id != current_user.id:
        abort(403)  # Error 403 = Prohibido

    if request.method == "POST":
        post.titulo = request.form["titulo"]
        post.contenido = request.form["contenido"]

        # Actualizar categorías
        categorias_ids = request.form.getlist("categorias_seleccionadas")
        post.categorias.clear()  # Limpiar las categorías existentes
        if categorias_ids:
            categorias = Categoria.query.filter(Categoria.id.in_(categorias_ids)).all()
            post.categorias.extend(categorias)

        db.session.commit()
        flash("Post actualizado correctamente", "success")
        return redirect(url_for("post_detail", post_id=post.id))

    return render_template("edit_post.html", post=post)


# Eliminar un post (borrado lógico)
@app.route("/post/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Autorización: solo el autor puede eliminar
    if post.usuario_id != current_user.id:
        abort(403)

    # Eliminado lógico
    post.is_active = False
    db.session.commit()

    flash("Post eliminado correctamente", "success")
    return redirect(url_for("index"))


# Eliminar un comentario
@app.route("/comment/delete/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comentario.query.get_or_404(comment_id)
    post_id = comment.post_id  # Guardamos el ID para la redirección

    # El autor del comentario O el autor del post pueden eliminar el comentario
    if (
        current_user.id != comment.usuario_id
        and current_user.id != comment.post.usuario_id
    ):
        abort(403)

    # Eliminado directo de la base de datos
    db.session.delete(comment)
    db.session.commit()

    flash("Comentario eliminado", "success")
    return redirect(url_for("post_detail", post_id=post_id))
