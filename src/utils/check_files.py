import os

from fastapi import UploadFile
from src.config.settings import env


def create_directory(dir_name: str):
    """
    Crea un directorio del Nombre (folder)
    Args:
        dir_name: str: pdf

    return: None (te crea el directorio uploads/pdf)
    """
    os.makedirs(dir_name, exist_ok=True)


def create_abs_path(file_name: str):
    """
    Create de absolute path with the name of the file.
    e.g: file_name="file.pdf"

    return "/usr/home/proy/file.pdf"

    Args:
        file_name: str -> file.pdf
    """
    return os.path.join(env.upload_dir, file_name)


def verify_folder_exists(file_name: str):
    """
    Verifica si un archivo existe usando os.path.exists()
    return: True /False
    """
    abs_path_file = create_abs_path(file_name)
    return os.path.exists(abs_path_file)


def verify_file_exists(file_name: str):
    """
    Verifica si existe un archivo (no un directorio) usando os.path.isfile()
    return: True si es un archivo
    """
    abs_path_file = create_abs_path(file_name)
    return os.path.isfile(abs_path_file)


def get_file_with_extencion(file: UploadFile):
    """
    te da el nombre 
    """
    ...


def stream_list_uploads_files(dir_path):
    files = os.listdir(dir_path)
    for file in files:
        ...
