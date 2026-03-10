from .ocr import extrair_texto_do_bi
from .bi import extrair_numero_bi
from .bi_nome import extrair_nome_bi
from .face_crop import extrair_rosto_bi
from .face import comparar_faces


def validar_identidade(bi_path, selfie_path, nome_form):

    texto = extrair_texto_do_bi(bi_path)

    numero_bi = extrair_numero_bi(texto)

    nome_bi = extrair_nome_bi(texto)

    rosto_bi = extrair_rosto_bi(bi_path)

    if not rosto_bi:
        return False, "Não foi possível detectar rosto no BI"

    face_valida = comparar_faces(selfie_path, rosto_bi)

    if not face_valida:
        return False, "A selfie não corresponde ao BI"

    if nome_bi and nome_form.upper() not in nome_bi.upper():
        return False, "Nome diferente do BI"

    return True, numero_bi
# from .ocr import extrair_texto_do_bi
# from .bi import extrair_numero_bi
# from .bi_nome import extrair_nome_bi
# from .face_crop import extrair_rosto_bi
# from .face import comparar_faces


# def validar_identidade(bi_path, selfie_path, nome_form):

#     texto = extrair_texto_do_bi(bi_path)

#     numero_bi = extrair_numero_bi(texto)

#     nome_bi = extrair_nome_bi(texto)

#     rosto_bi = extrair_rosto_bi(bi_path)

#     if not rosto_bi:
#         return False, "Não foi possível detectar rosto no BI"

#     face_valida = comparar_faces(selfie_path, rosto_bi)

#     if not face_valida:
#         return False, "A selfie não corresponde ao BI"

#     if nome_form.upper() not in nome_bi.upper():
#         return False, "Nome diferente do BI"

#     return True, numero_bi