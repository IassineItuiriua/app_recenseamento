import tempfile
import os


def salvar_temp(file):

    temp = tempfile.NamedTemporaryFile(delete=False)

    for chunk in file.chunks():
        temp.write(chunk)

    temp.close()

    return temp.name


def remover_temp(path):

    if path and os.path.exists(path):
        os.remove(path)
# import tempfile
# import os

# def salvar_temp_upload(uploaded_file):
#     sufixo = os.path.splitext(uploaded_file.name)[1]

#     temp = tempfile.NamedTemporaryFile(delete=False, suffix=sufixo)
#     for chunk in uploaded_file.chunks():
#         temp.write(chunk)

#     temp.close()
#     return temp.name
