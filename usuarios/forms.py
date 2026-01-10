# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
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


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirmar Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "telefone")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe uma conta com este email.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 != p2:
            raise forms.ValidationError("As passwords não coincidem.")

        validate_password(p1)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user