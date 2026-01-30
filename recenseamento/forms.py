from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Recenseamento, PerfilCidadao
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import unicodedata
import re
import os
import shutil
from django.conf import settings
import cv2
import tempfile
from difflib import SequenceMatcher



# ======================
# TESSERACT (Docker/Render)
# ======================
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_CMD", "/usr/bin/tesseract"
)


def similaridade_nomes(nome1, nome2):
    return SequenceMatcher(
        None,
        normalizar_texto(nome1),
        normalizar_texto(nome2)
    ).ratio()

# ======================
# UTILITÁRIOS TEXTO
# ======================
def normalizar_texto(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("ASCII")
    texto = texto.upper()
    texto = re.sub(r"[^A-Z\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def normalizar_texto_ocr(texto):
    texto = texto.upper()
    texto = texto.replace("O", "0").replace("I", "1").replace("L", "1")
    texto = re.sub(r"[^A-Z0-9]", "", texto)
    return texto


def extrair_numero_bi(texto):
    texto = normalizar_texto_ocr(texto)
    match = re.search(r"\d{11,13}[A-Z]?", texto)
    return match.group() if match else None


# ======================
# OCR BI
# ======================
def extrair_texto_bi(caminho):
    if caminho.lower().endswith(".pdf"):
        paginas = convert_from_path(caminho)
        return "".join(pytesseract.image_to_string(p) for p in paginas)
    img = Image.open(caminho)
    return pytesseract.image_to_string(img)


# ======================
# FACE RECOGNITION
# ======================
def verificar_face(bi_path, selfie_path):
    try:
        from deepface import DeepFace

        resultado = DeepFace.verify(
            img1_path=bi_path,
            img2_path=selfie_path,
            model_name="ArcFace",
            detector_backend="retinaface",
            enforce_detection=False
        )

        return {
            "match": resultado.get("distance", 1) <= 0.75,
            "distance": resultado.get("distance", 1)
        }

    except Exception as e:
        print(f"[ERRO FACE] {e}")
        return {
            "match": False,
            "distance": 1
        }





def salvar_temp(file):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    for chunk in file.chunks():
        temp.write(chunk)
    temp.close()
    return temp.name


# ==========================
# FORMULÁRIO RECENSEAMENTO
# ==========================
class RecenseamentoForm(forms.ModelForm):

    class Meta:
        model = Recenseamento
        exclude = ("usuario", "nim", "foi_submetido_exame", "resultado_exame")

    def clean_data_nascimento(self):
        data = self.cleaned_data.get("data_nascimento")
        idade = date.today().year - data.year
        if idade < 18 or idade > 35:
            raise ValidationError("Idade permitida: 18 a 35 anos.")
        return data

    def clean(self):
        cleaned = super().clean()

        bi = cleaned.get("documento_identidade")
        foto = cleaned.get("foto_capturada")
        nome_form = cleaned.get("nome_completo")

        if not bi or not foto:
            raise ValidationError("Documento e foto são obrigatórios.")

        bi_path = foto_path = None
        nome_ok = False
        face_ok = False

        try:
            bi_path = salvar_temp(bi)
            foto_path = salvar_temp(foto)

            # ===== OCR =====
            if settings.ENABLE_OCR:
                texto_bi = extrair_texto_bi(bi_path)
                nome_ok = normalizar_texto(nome_form) in normalizar_texto(texto_bi)
                numero_bi = extrair_numero_bi(texto_bi)
                if numero_bi:
                    cleaned["bi"] = numero_bi

            # ===== FACE =====
            if settings.ENABLE_FACE_RECOGNITION:
                face_ok = verificar_face(bi_path, foto_path)

            # ===== DECISÃO FINAL =====
            if not nome_ok and not face_ok:
                raise ValidationError(
                    "Falha na validação: nome e rosto não correspondem ao documento."
                )

        finally:
            if bi_path and os.path.exists(bi_path):
                os.remove(bi_path)
            if foto_path and os.path.exists(foto_path):
                os.remove(foto_path)

        return cleaned


# ==========================
# PERFIL CIDADÃO (>35)
# ==========================
class CompletarPerfilCidadaoForm(forms.ModelForm):

    class Meta:
        model = PerfilCidadao
        fields = (
            "nome_completo", "data_nascimento", "numero_bi",
            "bi", "foto", "telefone", "email", "dados_confirmados"
        )

    def clean_data_nascimento(self):
        data = self.cleaned_data.get("data_nascimento")
        idade = date.today().year - data.year
        if idade < 18:
            raise ValidationError("Idade mínima: 18 anos.")
        return data

    def clean(self):
        cleaned = super().clean()

        bi = cleaned.get("bi")
        foto = cleaned.get("foto")
        nome_form = cleaned.get("nome_completo")

        bi_path = foto_path = None
        nome_ok = False
        face_ok = False

        try:
            bi_path = salvar_temp(bi)
            foto_path = salvar_temp(foto)

            if settings.ENABLE_OCR:
                texto_bi = extrair_texto_bi(bi_path)
                score_nome = similaridade_nomes(nome_form, texto_bi)
                nome_ok = score_nome >= 0.70

                numero_bi = extrair_numero_bi(texto_bi)
                if numero_bi:
                    cleaned["bi"] = numero_bi

            # ===== FACE =====
                if settings.ENABLE_FACE_RECOGNITION:
                    face_result = verificar_face(bi_path, foto_path)
                    face_ok = face_result["match"]
                    face_distance = face_result["distance"]
                else:
                    face_ok = True
                    face_distance = None

            # ===== DECISÃO FINAL (institucional) =====
            if not face_ok:
                raise ValidationError(
                    "Falha na validação biométrica facial. Submeta uma foto mais nítida."
                )

            if not nome_ok:
                raise ValidationError(
                    "O nome informado não corresponde suficientemente ao documento."
                )

        finally:
            if bi_path and os.path.exists(bi_path):
                os.remove(bi_path)
            if foto_path and os.path.exists(foto_path):
                os.remove(foto_path)

        return cleaned


# from django import forms
# from django.core.exceptions import ValidationError
# from datetime import date
# from .models import Recenseamento, PerfilCidadao
# from PIL import Image
# from pdf2image import convert_from_path
# import pytesseract
# import unicodedata
# import re
# import os
# from .utils.files import salvar_temp_upload
# from django.conf import settings
# import shutil
# from difflib import SequenceMatcher

# # ======================
# # CONFIG TESSERACT
# # ======================
# pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")
# pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")

# # ======================
# # OCR & TEXTO
# # ======================
# def normalizar_texto(texto):
#     if not texto:
#         return ""
#     texto = unicodedata.normalize("NFKD", texto)
#     texto = texto.encode("ASCII", "ignore").decode("ASCII")
#     texto = texto.upper()
#     texto = re.sub(r"[^A-Z\s]", " ", texto)
#     texto = re.sub(r"\s+", " ", texto).strip()
#     return texto


# def normalizar_texto_ocr(texto):
#     texto = texto.upper()
#     texto = texto.replace("O", "0").replace("I", "1").replace("L", "1")
#     texto = re.sub(r"[^A-Z0-9]", "", texto)
#     return texto


# def extrair_numero_bi(texto):
#     texto = normalizar_texto_ocr(texto)
#     match = re.search(r"\d{11,13}[A-Z]?", texto)
#     return match.group() if match else None


# def extrair_texto_do_bi(bi_file):
#     caminho = bi_file.path if hasattr(bi_file, "path") else bi_file
#     if caminho.lower().endswith(".pdf"):
#         paginas = convert_from_path(caminho)
#         return "".join(pytesseract.image_to_string(p) for p in paginas)
#     img = Image.open(caminho)
#     return pytesseract.image_to_string(img)


# def extrair_nome_do_bi(texto):
#     linhas = texto.splitlines()
#     candidatos = []
#     for linha in linhas:
#         linha = normalizar_texto(linha)
#         if len(linha.split()) >= 2 and len(linha) > 10:
#             candidatos.append(linha)
#     return max(candidatos, key=len, default="")


# def similaridade_nomes(nome1, nome2):
#     return SequenceMatcher(
#         None,
#         normalizar_texto(nome1),
#         normalizar_texto(nome2)
#     ).ratio()

# # ======================
# # RECONHECIMENTO FACIAL
# # ======================
# def validar_face(foto_usuario, foto_documento):
#     """
#     Retorna True se for a mesma pessoa.
#     """
#     if not settings.ENABLE_FACE_RECOGNITION:
#         return True

#     try:
#         from deepface import DeepFace

#         resultado = DeepFace.verify(
#             img1_path=foto_usuario,
#             img2_path=foto_documento,
#             enforce_detection=True
#         )
#         return resultado.get("verified", False)
#     except Exception:
#         return False

# # ==========================
# # FORM RECENSEAMENTO
# # ==========================
# class RecenseamentoForm(forms.ModelForm):
#     class Meta:
#         model = Recenseamento
#         exclude = ("usuario", "nim", "foi_submetido_exame", "resultado_exame")

#     def clean_data_nascimento(self):
#         data = self.cleaned_data.get("data_nascimento")
#         idade = date.today().year - data.year
#         if idade < 18 or idade > 35:
#             raise ValidationError("Idade permitida: 18 a 35 anos.")
#         return data

#     def clean(self):
#         cleaned = super().clean()
#         nome = cleaned.get("nome_completo")
#         bi_file = cleaned.get("documento_identidade")
#         foto = cleaned.get("foto_capturada")

#         if not all([nome, bi_file, foto]):
#             raise ValidationError("Todos os campos obrigatórios devem ser preenchidos.")

#         bi_path = salvar_temp_upload(bi_file)
#         try:
#             texto_bi = extrair_texto_do_bi(bi_path)
#             numero_bi = extrair_numero_bi(texto_bi)
#             if not numero_bi:
#                 raise ValidationError("BI inválido ou ilegível.")

#             cleaned["bi"] = numero_bi

#             nome_bi = extrair_nome_do_bi(texto_bi)
#             score = similaridade_nomes(nome, nome_bi)
#             if score < 0.75:
#                 raise ValidationError("Nome não corresponde ao documento.")

#             if not validar_face(foto.path, bi_path):
#                 raise ValidationError("Reconhecimento facial falhou.")

#         finally:
#             if os.path.exists(bi_path):
#                 os.remove(bi_path)

#         return cleaned

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.bi = self.cleaned_data.get("bi")
#         if commit:
#             instance.save()
#         return instance

# # ==========================
# # FORM PERFIL CIDADÃO
# # ==========================
# class CompletarPerfilCidadaoForm(forms.ModelForm):
#     class Meta:
#         model = PerfilCidadao
#         fields = "__all__"

#     def clean_data_nascimento(self):
#         data = self.cleaned_data.get("data_nascimento")
#         idade = date.today().year - data.year
#         if idade < 18:
#             raise ValidationError("Idade mínima: 18 anos.")
#         return data

#     def clean(self):
#         cleaned = super().clean()
#         nome = cleaned.get("nome_completo")
#         bi_file = cleaned.get("bi")
#         foto = cleaned.get("foto")

#         if not all([nome, bi_file, foto]):
#             raise ValidationError("Todos os campos são obrigatórios.")

#         bi_path = salvar_temp_upload(bi_file)
#         try:
#             texto_bi = extrair_texto_do_bi(bi_path)
#             numero_bi = extrair_numero_bi(texto_bi)
#             if not numero_bi:
#                 raise ValidationError("Número de BI inválido.")

#             cleaned["numero_bi"] = numero_bi

#             nome_bi = extrair_nome_do_bi(texto_bi)
#             score = similaridade_nomes(nome, nome_bi)
#             if score < 0.75:
#                 raise ValidationError("Nome não corresponde ao BI.")

#             if not validar_face(foto.path, bi_path):
#                 raise ValidationError("Face não corresponde ao documento.")

#         finally:
#             if os.path.exists(bi_path):
#                 os.remove(bi_path)

#         return cleaned



# from django import forms
# from django.core.exceptions import ValidationError
# from datetime import date
# from .models import Recenseamento, PerfilCidadao
# from PIL import Image
# from pdf2image import convert_from_path
# import pytesseract
# import unicodedata
# import re
# import os
# from .utils.files import salvar_temp_upload
# from django.conf import settings
# import shutil


# # Configuração multiplataforma do Tesseract
# # if settings.ENABLE_OCR:
# #     if os.name == "nt":
# #         pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# #     else:
# #         tesseract_path = shutil.which("tesseract")
# #         if not tesseract_path:
# #             raise RuntimeError("Tesseract não encontrado no sistema")
# #         pytesseract.pytesseract.tesseract_cmd = tesseract_path
# pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")
# pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
# # ======================
# # Funções utilitárias
# # ======================
# def normalizar_texto(texto):
#     if not texto:
#         return ""
#     texto = unicodedata.normalize("NFKD", texto)
#     texto = texto.encode("ASCII", "ignore").decode("ASCII")
#     texto = texto.upper()
#     texto = re.sub(r"[^A-Z\s]", " ", texto)
#     texto = re.sub(r"\s+", " ", texto).strip()
#     return texto

# def normalizar_texto_ocr(texto):
#     texto = texto.upper()
#     texto = texto.replace("O", "0").replace("I", "1").replace("L", "1")
#     texto = re.sub(r"[^A-Z0-9]", "", texto)
#     return texto

# def extrair_numero_bi(texto):
#     texto = normalizar_texto_ocr(texto)
#     match = re.search(r"\d{11,13}[A-Z]?", texto)
#     if match:
#         return match.group()
#     match = re.search(r"\d{11,13}", texto)
#     if match:
#         return match.group()
#     return None

# def extrair_texto_do_bi(bi_file):
#     if hasattr(bi_file, 'path'):
#         caminho = bi_file.path
#     elif hasattr(bi_file, 'temporary_file_path'):
#         caminho = bi_file.temporary_file_path()
#     elif isinstance(bi_file, str):
#         caminho = bi_file
#     else:
#         raise ValidationError("Arquivo do BI inválido.")

#     if caminho.lower().endswith(".pdf"):
#         paginas = convert_from_path(caminho)
#         texto = "".join(pytesseract.image_to_string(p) for p in paginas)
#     else:
#         img = Image.open(caminho)
#         texto = pytesseract.image_to_string(img)
#     return texto

# # ==========================
# # FORMULÁRIO RECENSEAMENTO
# # ==========================
# class RecenseamentoForm(forms.ModelForm):
#     class Meta:
#         model = Recenseamento
#         exclude = ("usuario", "nim", "foi_submetido_exame", "resultado_exame")
#         widgets = {
#             "nome_completo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome conforme BI"}),
#             "data_nascimento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "filiacao_pai": forms.TextInput(attrs={"class": "form-control"}),
#             "filiacao_mae": forms.TextInput(attrs={"class": "form-control"}),
#             "nacionalidade": forms.TextInput(attrs={"class": "form-control"}),
#             "naturalidade": forms.TextInput(attrs={"class": "form-control"}),
#             "morada": forms.TextInput(attrs={"class": "form-control"}),
#             "contacto_familiar": forms.TextInput(attrs={"class": "form-control"}),
#             "documento_identidade": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
#             "foto_capturada": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png"}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields["documento_identidade"].required = True
#         self.fields["foto_capturada"].required = True

#     def clean_data_nascimento(self):
#         data = self.cleaned_data.get("data_nascimento")
#         if not data:
#             raise ValidationError("Data de nascimento é obrigatória.")
#         idade = date.today().year - data.year - ((date.today().month, date.today().day) < (data.month, data.day))
#         if idade < 18 or idade > 35:
#             raise ValidationError("A idade permitida para o recenseamento é entre 18 e 35 anos.")
#         self.cleaned_data["idade"] = idade
#         return data

#     def clean(self):
#         cleaned_data = super().clean()

#         # 🔒 Validações obrigatórias SEM OCR
#         if not cleaned_data.get("documento_identidade"):
#             self.add_error(
#                 "documento_identidade",
#                 "Documento de identidade é obrigatório."
#             )

#         if not cleaned_data.get("foto_capturada"):
#             self.add_error(
#                 "foto_capturada",
#                 "A foto capturada é obrigatória."
#             )

#         # ⛔ Se OCR estiver desligado, para aqui
#         if not settings.ENABLE_OCR:
#             return cleaned_data

#         # ================= OCR =================
#         nome_form = cleaned_data.get("nome_completo")
#         bi_file = cleaned_data.get("documento_identidade")
#         bi_path = None

#         try:
#             if bi_file and nome_form:
#                 bi_path = salvar_temp_upload(bi_file) if hasattr(bi_file, "chunks") else bi_file
#                 texto_bi = extrair_texto_do_bi(bi_path)
#                 numero_bi = extrair_numero_bi(texto_bi)

#                 if not numero_bi:
#                     raise ValidationError("Não foi possível identificar o número do BI.")

#                 cleaned_data["bi"] = numero_bi

#                 if normalizar_texto(nome_form) not in normalizar_texto(texto_bi):
#                     raise ValidationError("O nome informado não coincide com o BI.")

#         finally:
#             if bi_path and os.path.exists(bi_path):
#                 os.remove(bi_path)

#         return cleaned_data


#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         if "bi" in self.cleaned_data:
#             instance.bi = self.cleaned_data["bi"]
#         if commit:
#             instance.save()
#         return instance

# # ==========================
# # FORMULÁRIO PERFIL CIDADÃO (>35 anos)
# # ==========================
# class CompletarPerfilCidadaoForm(forms.ModelForm):
#     class Meta:
#         model = PerfilCidadao
#         fields = ("nome_completo", "data_nascimento", "numero_bi", "bi", "foto", "telefone", "email", "dados_confirmados")
#         widgets = {
#             "nome_completo": forms.TextInput(attrs={"class": "form-control"}),
#             "data_nascimento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
#             "numero_bi": forms.TextInput(attrs={"class": "form-control"}),
#             "bi": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
#             "foto": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
#             "telefone": forms.TextInput(attrs={"class": "form-control"}),
#             "email": forms.EmailInput(attrs={"class": "form-control"}),
#             "dados_confirmados": forms.CheckboxInput(attrs={"class": "form-check-input"}),
#         }

#     def clean_data_nascimento(self):
#         data = self.cleaned_data.get("data_nascimento")
#         if not data:
#             raise ValidationError("Data de nascimento é obrigatória.")
#         idade = date.today().year - data.year - ((date.today().month, date.today().day) < (data.month, data.day))
#         if idade < 18:
#             raise ValidationError("Idade mínima é 18 anos.")
#         self.cleaned_data["idade"] = idade
#         return data

#     def clean(self):
#         cleaned_data = super().clean()
#         nome_form = cleaned_data.get("nome_completo")
#         bi_file = cleaned_data.get("bi")
#         bi_path = None

#         try:
#             if bi_file and nome_form:
#                 bi_path = salvar_temp_upload(bi_file) if hasattr(bi_file, "chunks") else bi_file
#                 texto_bi = extrair_texto_do_bi(bi_path)
#                 numero_bi = extrair_numero_bi(texto_bi)
#                 if not numero_bi:
#                     raise ValidationError("Não foi possível extrair o número do BI.")
#                 cleaned_data["numero_bi"] = numero_bi

#                 if normalizar_texto(nome_form) not in normalizar_texto(texto_bi):
#                     raise ValidationError("O nome informado não coincide com o documento de identidade.")
#         finally:
#             if bi_path and os.path.exists(bi_path):
#                 os.remove(bi_path)

#         return cleaned_data

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         numero_bi_extraido = self.cleaned_data.get("numero_bi")
#         if numero_bi_extraido:
#             instance.numero_bi = numero_bi_extraido
#         if commit:
#             instance.save()
#         return instance
