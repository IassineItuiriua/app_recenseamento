# recenseamento/utils/ocr.py
import os
import re
from PIL import Image
import pytesseract

def normalizar_texto_ocr(texto):
    texto = texto.upper()
    texto = texto.replace("O", "0").replace("I", "1").replace("L", "1")
    texto = re.sub(r"[^A-Z0-9]", "", texto)
    return texto

def extrair_texto_do_bi(caminho):
    if not os.path.exists(caminho):
        raise Exception(f"Arquivo não encontrado: {caminho}")

    with Image.open(caminho) as img:
        img = img.convert("RGB")
        texto = pytesseract.image_to_string(
            img,
            lang="por"
        )

    return texto
