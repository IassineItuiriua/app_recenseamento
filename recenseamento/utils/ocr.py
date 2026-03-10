

import os
import re
from PIL import Image, ImageFilter
import pytesseract


def normalizar_texto_ocr(texto):

    if not texto:
        return ""

    texto = texto.upper()

    texto = texto.replace("O", "0")
    texto = texto.replace("I", "1")
    texto = texto.replace("L", "1")

    texto = re.sub(r"\s+", " ", texto)

    return texto


def preprocessar_imagem(img):

    img = img.convert("L")

    img = img.filter(ImageFilter.SHARPEN)

    img = img.point(lambda x: 0 if x < 140 else 255)

    return img


def extrair_texto_do_bi(caminho):

    if not os.path.exists(caminho):
        raise Exception(f"Arquivo não encontrado: {caminho}")

    with Image.open(caminho) as img:

        img = preprocessar_imagem(img)

        texto = pytesseract.image_to_string(
            img,
            lang="por",
            config="--oem 3 --psm 6"
        )

    return normalizar_texto_ocr(texto)

# # recenseamento/utils/ocr.py

# import os
# import re
# from PIL import Image, ImageFilter
# import pytesseract


# def normalizar_texto_ocr(texto):
#     if not texto:
#         return ""

#     texto = texto.upper()

#     # corrigir erros comuns do OCR
#     texto = texto.replace("O", "0")
#     texto = texto.replace("I", "1")
#     texto = texto.replace("L", "1")

#     texto = re.sub(r"\s+", " ", texto)

#     return texto


# def preprocessar_imagem(img):
#     """
#     Melhora a imagem para OCR
#     """

#     img = img.convert("L")  # grayscale

#     # aumentar nitidez
#     img = img.filter(ImageFilter.SHARPEN)

#     # aumentar contraste
#     img = img.point(lambda x: 0 if x < 140 else 255)

#     return img


# def extrair_texto_do_bi(caminho):

#     if not os.path.exists(caminho):
#         raise Exception(f"Arquivo não encontrado: {caminho}")

#     with Image.open(caminho) as img:

#         img = preprocessar_imagem(img)

#         texto = pytesseract.image_to_string(
#             img,
#             lang="por",
#             config="--oem 3 --psm 6"
#         )

#     return normalizar_texto_ocr(texto)