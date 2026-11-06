"""C do MVC: CRUD de posts (com upload de imagem)."""
from flask import (
    Blueprint, abort, flash, g, redirect, render_template, request, url_for,
)

from .auth import login_required
from .models import Post, db
from .uploads import delete_image, save_image

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    posts = db.session.execute(
        db.select(Post).order_by(Post.created.desc())
    ).scalars().all()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    post = db.session.get(Post, id)
    if post is None:
        abort(404, f"Post id {id} não existe.")
    if check_author and post.author_id != g.user.id:
        abort(403)
    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"].strip()
        body = request.form["body"].strip()
        error = None
        image_name = None

        if not title:
            error = "Título é obrigatório."
        else:
            try:
                image_name = save_image(request.files.get("imagem_post"))
            except ValueError as e:
                error = str(e)

        if error is not None:
            flash(error, "danger")
        else:
            db.session.add(
                Post(title=title, body=body, author_id=g.user.id,
                     imagem_post=image_name)
            )
            db.session.commit()
            flash("Post publicado!", "success")
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"].strip()
        body = request.form["body"].strip()
        error = None
        new_image = None

        if not title:
            error = "Título é obrigatório."
        else:
            try:
                new_image = save_image(request.files.get("imagem_post"))
            except ValueError as e:
                error = str(e)

        if error is not None:
            flash(error, "danger")
        else:
            post.title = title
            post.body = body
            if new_image:  # substitui a imagem antiga
                delete_image(post.imagem_post)
                post.imagem_post = new_image
            db.session.commit()
            flash("Post atualizado!", "success")
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    delete_image(post.imagem_post)
    db.session.delete(post)
    db.session.commit()
    flash("Post excluído.", "info")
    return redirect(url_for("blog.index"))
