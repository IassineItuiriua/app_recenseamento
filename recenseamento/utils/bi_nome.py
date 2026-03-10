import re


def extrair_nome_bi(texto):

    linhas = texto.split("\n")

    for linha in linhas:

        if "NOME" in linha:

            nome = linha.replace("NOME", "")

            nome = re.sub(r"[^A-Z ]", "", nome)

            return nome.strip()

    return None
# import re

# def extrair_nome_bi(texto):

#     linhas = texto.split("\n")

#     for linha in linhas:

#         if "NOME" in linha:
#             nome = linha.replace("NOME", "")
#             nome = re.sub(r"[^A-Z ]", "", nome)
#             return nome.strip()

#     return None