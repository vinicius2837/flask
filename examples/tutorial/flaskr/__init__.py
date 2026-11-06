import os

from flask import Flask

from .models import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",  # troque em produção
        # caminho relativo -> Flask-SQLAlchemy grava em instance/flaskr.sqlite
        SQLALCHEMY_DATABASE_URI="sqlite:///flaskr.sqlite",
        UPLOAD_FOLDER=os.path.join(app.root_path, "static", "uploads"),
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,  # 8 MB por requisição
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Banco de dados (SQLAlchemy substitui db.py e schema.sql)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from . import auth, blog, calculos

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(calculos.bp)
    app.add_url_rule("/", endpoint="index")

    return app
