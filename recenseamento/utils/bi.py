import unicodedata
from difflib import SequenceMatcher
from django.core.exceptions import ValidationError


def normalizar_nome(nome):

    if not nome:
        return ""

    nome = nome.upper().strip()

    nome = unicodedata.normalize("NFD", nome)

    nome = "".join(
        c for c in nome
        if unicodedata.category(c) != "Mn"
    )

    return nome


def similaridade_nome(nome1, nome2):

    nome1 = normalizar_nome(nome1)
    nome2 = normalizar_nome(nome2)

    return SequenceMatcher(None, nome1, nome2).ratio()


def validar_documento_completo(
    nome_form,
    bi_file,
    selfie_file,
    threshold_nome=0.55
):

    """
    Validação básica:
    - verifica se arquivos existem
    - compara nome digitado com nome detectado (simulado)
    """

    if not nome_form:
        raise ValidationError(
            "Nome completo é obrigatório."
        )

    if not bi_file:
        raise ValidationError(
            "Documento de identidade é obrigatório."
        )

    if not selfie_file:
        raise ValidationError(
            "Selfie é obrigatória."
        )

    # Simulação de nome encontrado no documento
    # (OCR será implementado depois)
    nome_documento = nome_form

    score = similaridade_nome(nome_form, nome_documento)

    if score < threshold_nome:
        raise ValidationError(
            "O nome informado não corresponde suficientemente ao documento."
        )

    return True
# import unicodedata
# import re


# def normalizar_texto(texto):
#     """
#     Remove acentos e caracteres especiais
#     """

#     if not texto:
#         return ""

#     texto = unicodedata.normalize("NFKD", texto)
#     texto = texto.encode("ASCII", "ignore").decode("ASCII")

#     texto = texto.upper()

#     texto = re.sub(r"[^A-Z0-9\s]", " ", texto)

#     texto = re.sub(r"\s+", " ", texto)

#     return texto.strip()


# def normalizar_texto_ocr(texto):
#     """
#     Corrige erros comuns do OCR
#     """

#     if not texto:
#         return ""

#     texto = texto.upper()

#     texto = texto.replace("O", "0")
#     texto = texto.replace("I", "1")
#     texto = texto.replace("L", "1")

#     texto = re.sub(r"[^A-Z0-9]", "", texto)

#     return texto


# def extrair_numero_bi(texto):
#     """
#     Extrai número do BI a partir do texto OCR
#     """

#     texto = normalizar_texto_ocr(texto)

#     # padrão comum: 11–13 dígitos + letra final
#     match = re.search(r"\d{11,13}[A-Z]", texto)

#     if match:
#         return match.group()

#     # fallback: apenas números longos
#     match = re.search(r"\d{11,13}", texto)

#     if match:
#         return match.group()

#     return None
# import os
# from difflib import SequenceMatcher
# from django.core.exceptions import ValidationError
# from django.conf import settings

# from .files import salvar_temp, remover_temp
# from .ocr import extrair_texto_bi, extrair_nome_do_bi, normalizar_texto


# STOPWORDS = {"DE", "DA", "DO", "DOS", "DAS", "E"}


# def normalizar_nome(nome):

#     nome = normalizar_texto(nome)

#     partes = [
#         p for p in nome.split()
#         if p not in STOPWORDS
#     ]

#     return " ".join(partes)


# def similaridade_nomes(nome1, nome2):

#     nome1 = normalizar_nome(nome1)
#     nome2 = normalizar_nome(nome2)

#     return SequenceMatcher(None, nome1, nome2).ratio()


# def validar_nome_bi(nome_form, nome_bi, threshold):

#     if not nome_bi:

#         raise ValidationError(
#             "Não foi possível ler o nome no documento. "
#             "Envie uma imagem mais nítida."
#         )

#     score = similaridade_nomes(nome_form, nome_bi)

#     if score < threshold:

#         raise ValidationError(
#             "O nome informado não corresponde ao documento."
#         )


# def verificar_face(bi_path, selfie_path):

#     try:

#         from deepface import DeepFace

#         resultado = DeepFace.verify(
#             img1_path=bi_path,
#             img2_path=selfie_path,
#             model_name="ArcFace",
#             detector_backend="retinaface",
#             enforce_detection=False
#         )

#         distance = resultado.get("distance", 1)

#         return distance <= 0.85

#     except Exception as e:

#         print(f"[ERRO FACE] {e}")

#         return False


# def validar_documento_completo(
#     nome_form,
#     bi_file,
#     selfie_file=None,
#     threshold_nome=0.60
# ):

#     bi_path = None
#     selfie_path = None

#     try:

#         bi_path = salvar_temp(bi_file)

#         if getattr(settings, "ENABLE_OCR", True):

#             texto = extrair_texto_bi(bi_path)

#             nome_bi = extrair_nome_do_bi(texto)

#             validar_nome_bi(
#                 nome_form,
#                 nome_bi,
#                 threshold_nome
#             )

#         if getattr(settings, "ENABLE_FACE_RECOGNITION", False) and selfie_file:

#             selfie_path = salvar_temp(selfie_file)

#             if not verificar_face(bi_path, selfie_path):

#                 raise ValidationError(
#                     "A selfie não corresponde ao documento de identidade."
#                 )

#     finally:

#         remover_temp(bi_path)
#         remover_temp(selfie_path)
# import re


# def extrair_numero_bi(texto):

#     if not texto:
#         return None

#     texto = texto.upper()

#     texto = re.sub(r"\s+", " ", texto)

#     padroes = [

#         r"\b\d{13}\b",

#         r"\b\d{6}\s?\d{6}\s?[A-Z]\b",

#         r"\b\d{6}/\d{6}/[A-Z]\b",

#         r"\b\d{6}-\d{6}-[A-Z]\b",

#     ]

#     for padrao in padroes:

#         match = re.search(padrao, texto)

#         if match:

#             numero = match.group()

#             numero = re.sub(r"[^A-Z0-9]", "", numero)

#             return numero

#     return None

# import re


# def extrair_numero_bi(texto):

#     if not texto:
#         return None

#     texto = texto.upper()

#     texto = re.sub(r"\s+", " ", texto)

#     padroes = [

#         # 13 números
#         r"\b\d{13}\b",

#         # 110100 123456 A
#         r"\b\d{6}\s?\d{6}\s?[A-Z]\b",

#         # 110100/123456/A
#         r"\b\d{6}/\d{6}/[A-Z]\b",

#         # 110100-123456-A
#         r"\b\d{6}-\d{6}-[A-Z]\b",

#     ]

#     for padrao in padroes:

#         match = re.search(padrao, texto)

#         if match:

#             numero = match.group()

#             numero = re.sub(r"[^A-Z0-9]", "", numero)

#             return numero

#     return None