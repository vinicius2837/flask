"""M do MVC: modelos ORM (Flask-SQLAlchemy)."""
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.Text, nullable=True)  # nome do arquivo da foto de perfil

    # 1 usuário -> N posts
    posts = db.relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f"<User {self.username}>"


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    imagem_post = db.Column(db.Text, nullable=True)  # nome do arquivo da imagem

    author = db.relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post {self.id} {self.title!r}>"
