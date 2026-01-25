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
from .utils.files import salvar_temp_upload
from django.conf import settings

# Configuração Tesseract OCR (Windows)
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ======================
# Funções utilitárias
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
    if match:
        return match.group()
    match = re.search(r"\d{11,13}", texto)
    if match:
        return match.group()
    return None

def extrair_texto_do_bi(bi_file):
    if hasattr(bi_file, 'path'):
        caminho = bi_file.path
    elif hasattr(bi_file, 'temporary_file_path'):
        caminho = bi_file.temporary_file_path()
    elif isinstance(bi_file, str):
        caminho = bi_file
    else:
        raise ValidationError("Arquivo do BI inválido.")

    if caminho.lower().endswith(".pdf"):
        paginas = convert_from_path(caminho)
        texto = "".join(pytesseract.image_to_string(p) for p in paginas)
    else:
        img = Image.open(caminho)
        texto = pytesseract.image_to_string(img)
    return texto

# ==========================
# FORMULÁRIO RECENSEAMENTO
# ==========================
class RecenseamentoForm(forms.ModelForm):
    class Meta:
        model = Recenseamento
        exclude = ("usuario", "nim", "foi_submetido_exame", "resultado_exame")
        widgets = {
            "nome_completo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome conforme BI"}),
            "data_nascimento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "filiacao_pai": forms.TextInput(attrs={"class": "form-control"}),
            "filiacao_mae": forms.TextInput(attrs={"class": "form-control"}),
            "nacionalidade": forms.TextInput(attrs={"class": "form-control"}),
            "naturalidade": forms.TextInput(attrs={"class": "form-control"}),
            "morada": forms.TextInput(attrs={"class": "form-control"}),
            "contacto_familiar": forms.TextInput(attrs={"class": "form-control"}),
            "documento_identidade": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
            "foto_capturada": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["documento_identidade"].required = True
        self.fields["foto_capturada"].required = True

    def clean_data_nascimento(self):
        data = self.cleaned_data.get("data_nascimento")
        if not data:
            raise ValidationError("Data de nascimento é obrigatória.")
        idade = date.today().year - data.year - ((date.today().month, date.today().day) < (data.month, data.day))
        if idade < 18 or idade > 35:
            raise ValidationError("A idade permitida para o recenseamento é entre 18 e 35 anos.")
        self.cleaned_data["idade"] = idade
        return data

    def clean(self):
        cleaned_data = super().clean()

        # 🔒 Validações obrigatórias SEM OCR
        if not cleaned_data.get("documento_identidade"):
            self.add_error(
                "documento_identidade",
                "Documento de identidade é obrigatório."
            )

        if not cleaned_data.get("foto_capturada"):
            self.add_error(
                "foto_capturada",
                "A foto capturada é obrigatória."
            )

        # ⛔ Se OCR estiver desligado, para aqui
        if not settings.ENABLE_OCR:
            return cleaned_data

        # ================= OCR =================
        nome_form = cleaned_data.get("nome_completo")
        bi_file = cleaned_data.get("documento_identidade")
        bi_path = None

        try:
            if bi_file and nome_form:
                bi_path = salvar_temp_upload(bi_file) if hasattr(bi_file, "chunks") else bi_file
                texto_bi = extrair_texto_do_bi(bi_path)
                numero_bi = extrair_numero_bi(texto_bi)

                if not numero_bi:
                    raise ValidationError("Não foi possível identificar o número do BI.")

                cleaned_data["bi"] = numero_bi

                if normalizar_texto(nome_form) not in normalizar_texto(texto_bi):
                    raise ValidationError("O nome informado não coincide com o BI.")

        finally:
            if bi_path and os.path.exists(bi_path):
                os.remove(bi_path)

        return cleaned_data


    def save(self, commit=True):
        instance = super().save(commit=False)
        if "bi" in self.cleaned_data:
            instance.bi = self.cleaned_data["bi"]
        if commit:
            instance.save()
        return instance

# ==========================
# FORMULÁRIO PERFIL CIDADÃO (>35 anos)
# ==========================
class CompletarPerfilCidadaoForm(forms.ModelForm):
    class Meta:
        model = PerfilCidadao
        fields = ("nome_completo", "data_nascimento", "numero_bi", "bi", "foto", "telefone", "email", "dados_confirmados")
        widgets = {
            "nome_completo": forms.TextInput(attrs={"class": "form-control"}),
            "data_nascimento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "numero_bi": forms.TextInput(attrs={"class": "form-control"}),
            "bi": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "dados_confirmados": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_data_nascimento(self):
        data = self.cleaned_data.get("data_nascimento")
        if not data:
            raise ValidationError("Data de nascimento é obrigatória.")
        idade = date.today().year - data.year - ((date.today().month, date.today().day) < (data.month, data.day))
        if idade < 18:
            raise ValidationError("Idade mínima é 18 anos.")
        self.cleaned_data["idade"] = idade
        return data

    def clean(self):
        cleaned_data = super().clean()
        nome_form = cleaned_data.get("nome_completo")
        bi_file = cleaned_data.get("bi")
        bi_path = None

        try:
            if bi_file and nome_form:
                bi_path = salvar_temp_upload(bi_file) if hasattr(bi_file, "chunks") else bi_file
                texto_bi = extrair_texto_do_bi(bi_path)
                numero_bi = extrair_numero_bi(texto_bi)
                if not numero_bi:
                    raise ValidationError("Não foi possível extrair o número do BI.")
                cleaned_data["numero_bi"] = numero_bi

                if normalizar_texto(nome_form) not in normalizar_texto(texto_bi):
                    raise ValidationError("O nome informado não coincide com o documento de identidade.")
        finally:
            if bi_path and os.path.exists(bi_path):
                os.remove(bi_path)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        numero_bi_extraido = self.cleaned_data.get("numero_bi")
        if numero_bi_extraido:
            instance.numero_bi = numero_bi_extraido
        if commit:
            instance.save()
        return instance
