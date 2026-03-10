from PIL import Image
from pdf2image import convert_from_path
import pytesseract
from django.conf import settings


# configurar tesseract
pytesseract.pytesseract.tesseract_cmd = getattr(
    settings,
    "TESSERACT_CMD",
    "/usr/bin/tesseract"
)


def extrair_texto_bi(caminho):
    """
    Extrai texto do BI (PDF ou imagem)
    """

    texto = ""

    if caminho.lower().endswith(".pdf"):

        paginas = convert_from_path(caminho)

        for pagina in paginas:
            texto += pytesseract.image_to_string(pagina)

    else:

        img = Image.open(caminho)

        texto = pytesseract.image_to_string(img)

    return texto
# import pytesseract
# from PIL import Image
# from pdf2image import convert_from_path
# import unicodedata
# import re
# from django.conf import settings


# # configurar tesseract
# pytesseract.pytesseract.tesseract_cmd = getattr(
#     settings,
#     "TESSERACT_CMD",
#     "/usr/bin/tesseract"
# )


# def extrair_texto_bi(caminho):

#     texto = ""

#     if caminho.lower().endswith(".pdf"):

#         paginas = convert_from_path(caminho)

#         for pagina in paginas:
#             texto += pytesseract.image_to_string(pagina)

#     else:

#         img = Image.open(caminho)

#         texto = pytesseract.image_to_string(img)

#     return texto


# def extrair_nome_do_bi(texto):

#     if not texto:
#         return ""

#     linhas = [
#         l.strip()
#         for l in texto.upper().splitlines()
#         if len(l.strip()) > 5
#     ]

#     # tentar linha com NOME
#     for linha in linhas:
#         if "NOME" in linha:
#             return linha.replace("NOME", "").strip()

#     # fallback
#     candidatas = []

#     for l in linhas:

#         if sum(c.isalpha() for c in l) > 10 and not any(
#             palavra in l for palavra in [
#                 "REPUBLICA",
#                 "MINISTERIO",
#                 "DATA",
#                 "EMISSAO",
#                 "VALIDADE"
#             ]
#         ):
#             candidatas.append(l)

#     if candidatas:
#         return max(candidatas, key=len)

#     return ""


# def normalizar_texto(texto):

#     if not texto:
#         return ""

#     texto = unicodedata.normalize("NFKD", texto)
#     texto = texto.encode("ASCII", "ignore").decode("ASCII")
#     texto = texto.upper()

#     texto = re.sub(r"[^A-Z\s]", " ", texto)
#     texto = re.sub(r"\s+", " ", texto)

#     return texto.strip()

# import os
# import re
# from PIL import Image, ImageFilter
# import pytesseract


# def normalizar_texto_ocr(texto):

#     if not texto:
#         return ""

#     texto = texto.upper()

#     texto = texto.replace("O", "0")
#     texto = texto.replace("I", "1")
#     texto = texto.replace("L", "1")

#     texto = re.sub(r"\s+", " ", texto)

#     return texto


# def preprocessar_imagem(img):

#     img = img.convert("L")

#     img = img.filter(ImageFilter.SHARPEN)

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