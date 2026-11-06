"""Utilitários de upload seguro de imagens (usado pelos controllers)."""
import os
import uuid

from flask import current_app
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file_storage, max_size=None):
    """Valida e salva a imagem em static/uploads/.

    Retorna o nome do arquivo salvo, ou None se nenhum arquivo foi enviado.
    Levanta ValueError se o arquivo for inválido.
    """
    if file_storage is None or file_storage.filename == "":
        return None

    original = secure_filename(file_storage.filename)
    if not original or not _allowed(original):
        raise ValueError("Formato inválido. Use png, jpg, jpeg, gif ou webp.")

    # Confere o conteúdo real com o Pillow (não confia só na extensão)
    try:
        img = Image.open(file_storage.stream)
        img.verify()
        file_storage.stream.seek(0)
        img = Image.open(file_storage.stream)
    except (UnidentifiedImageError, OSError):
        raise ValueError("O arquivo enviado não é uma imagem válida.")

    if max_size:
        img.thumbnail(max_size)

    ext = original.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}_{original}"
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, unique_name)

    if max_size:  # ex.: avatar -> miniatura 256x256
        img.thumbnail(max_size)
        if ext in {"jpg", "jpeg"} and img.mode != "RGB":
            img = img.convert("RGB")
        img.save(path)
    else:
        file_storage.stream.seek(0)
        file_storage.save(path)
    return unique_name


def delete_image(filename):
    """Remove fisicamente um arquivo de upload (se existir)."""
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        os.remove(path)
