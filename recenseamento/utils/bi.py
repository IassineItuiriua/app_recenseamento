import re


def extrair_numero_bi(texto):

    if not texto:
        return None

    texto = texto.upper()

    texto = re.sub(r"\s+", " ", texto)

    padroes = [

        r"\b\d{13}\b",

        r"\b\d{6}\s?\d{6}\s?[A-Z]\b",

        r"\b\d{6}/\d{6}/[A-Z]\b",

        r"\b\d{6}-\d{6}-[A-Z]\b",

    ]

    for padrao in padroes:

        match = re.search(padrao, texto)

        if match:

            numero = match.group()

            numero = re.sub(r"[^A-Z0-9]", "", numero)

            return numero

    return None

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