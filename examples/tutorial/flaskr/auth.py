"""C do MVC: autenticação e cadastro (com upload de avatar)."""
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
)
from sqlalchemy.exc import IntegrityError

from .models import User, db
from .uploads import delete_image, save_image

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        error = None

        if not username:
            error = "Nome de usuário é obrigatório."
        elif not password:
            error = "Senha é obrigatória."
        elif db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none():
            error = f"Usuário {username} já está cadastrado."

        avatar_name = None
        if error is None:
            try:
                avatar_name = save_image(
                    request.files.get("avatar"), max_size=(256, 256)
                )
            except ValueError as e:
                error = str(e)

        if error is None:
            user = User(username=username, avatar=avatar_name)
            user.set_password(password)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                delete_image(avatar_name)
                error = f"Usuário {username} já está cadastrado."
            else:
                flash("Cadastro realizado! Faça login.", "success")
                return redirect(url_for("auth.login"))

        flash(error, "danger")

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()

        if user is None or not user.check_password(password):
            flash("Usuário ou senha incorretos.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
