# usuarios/forms.py
from django import forms
from .models import CustomUser
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
# =====================================================
#   REGISTO / CADASTRO DE USUÁRIO /LOGIN POR EMAIL
# =====================================================

# usuarios/forms.py

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        self.user = authenticate(self.request, email=email, password=password)
        if self.user is None:
            raise forms.ValidationError("Email ou password inválidos.")
        return self.cleaned_data

    def get_user(self):
        return self.user


# =====================================================
#   COMPLETAR PERFIL BÁSICO DO USUÁRIO
# =====================================================
class CompletarPerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "telefone",
        )

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    telefone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "telefone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
