import tempfile
import os

def salvar_temp_upload(uploaded_file):
    sufixo = os.path.splitext(uploaded_file.name)[1]

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=sufixo)
    for chunk in uploaded_file.chunks():
        temp.write(chunk)

    temp.close()
    return temp.name
